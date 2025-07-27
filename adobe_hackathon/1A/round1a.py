import pdfplumber
from pathlib import Path
import json
import re
from collections import defaultdict, Counter
from sentence_transformers import SentenceTransformer, util
import torch


def is_garbage_line(text):
    return (
        len(text.strip()) < 2 or
        re.fullmatch(r"[.\-\u2013=_* ]{5,}", text) or
        re.fullmatch(r"Page\s+\d+(\s+of\s+\d+)?", text, re.IGNORECASE) or
        re.fullmatch(r"\d+", text.strip())
    )

def classify_heading_level_by_text(text):
    text = text.strip()
    if re.match(r'^\d+\.\d+\.\d+.*', text):
        return "H3"
    if re.match(r'^\d+\.\d+.*', text):
        return "H2"
    if re.match(r'^\d+\..*', text):
        return "H1"
    if re.match(r'^Appendix\s[A-Z].*', text):
        return "H1"
    return None


# --- Setup transformer-based fallback (MiniLM-L3) ---
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')

heading_templates = {
    "H1": ["1. Introduction", "2. Overview", "Appendix A"],
    "H2": ["2.1 Features", "2.2 Use Case"],
    "H3": ["2.1.1 Details", "3.2.2 Method", "Timeline:"]
}

template_embeds = {
    level: model.encode(samples, convert_to_tensor=True)
    for level, samples in heading_templates.items()
}


def predict_heading_level_by_semantics(text):
    line_emb = model.encode(text, convert_to_tensor=True)
    best_level = None
    best_score = 0.0

    for level, embeddings in template_embeds.items():
        score = util.cos_sim(line_emb, embeddings).max().item()
        if score > best_score:
            best_score = score
            best_level = level

    return best_level if best_score >= 0.6 else None


def extract_outline_generic(pdf_path: Path):
    lines_info = []
    style_counts = Counter()

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(
                use_text_flow=True, x_tolerance=2, extra_attrs=['fontname', 'size']
            )
            lines = defaultdict(list)
            for word in words:
                lines[round(word['top'])].append(word)

            for y_pos in sorted(lines.keys()):
                line_words = sorted(lines[y_pos], key=lambda w: w['x0'])
                text = " ".join(w["text"] for w in line_words).strip()
                if not text or is_garbage_line(text):
                    continue

                size = round(max(w['size'] for w in line_words), 1)
                bold = any("Bold" in f.upper() or "Black" in f.upper()
                           for f in [w['fontname'] for w in line_words])

                style_counts[(size, bold)] += 1

                lines_info.append({
                    "text": text,
                    "page": page_num,
                    "y_pos": y_pos,
                    "x0": line_words[0]['x0'],
                    "size": size,
                    "bold": bold,
                    "all_caps": text.isupper(),
                    "ends_colon": text.endswith(":")
                })

    if not lines_info:
        return {"title": "", "outline": []}

    body_style = style_counts.most_common(1)[0][0]

    title = ""
    title_score = 0
    potential_title = None

    for line in lines_info:
        if line['page'] == 1 and line['y_pos'] < 200:
            score = line['size'] * 1.5 + (2 if line['bold'] else 0)
            if score > title_score:
                title_score = score
                potential_title = line

    if potential_title and potential_title['size'] > body_style[0]:
        title = potential_title['text']
        lines_info = [l for l in lines_info if l['text'] != title]

    heading_candidates = []
    for line in lines_info:
        if line['size'] > body_style[0] or (line['bold'] and not body_style[1]):
            if len(line['text']) < 150:
                heading_candidates.append(line)

    heading_styles = sorted(
        list(set((h['size'], h['bold']) for h in heading_candidates)),
        key=lambda x: (-x[0], not x[1])
    )
    style_to_level = {style: f"H{i+1}" for i,
                      style in enumerate(heading_styles)}

    outline = []
    for line in heading_candidates:
        level = classify_heading_level_by_text(line['text'])

        if not level:
            style = (line['size'], line['bold'])
            level = style_to_level.get(style)

        # Fallback to transformer-based prediction if no match
        if not level:
            level = predict_heading_level_by_semantics(line['text'])

        if level:
            outline.append({
                "level": level,
                "text": line['text'],
                "page": line['page'],
                "y_pos": line['y_pos']
            })

    sorted_outline = sorted(outline, key=lambda x: (x["page"], x["y_pos"]))
    for item in sorted_outline:
        del item['y_pos']
        item['text'] = re.sub(r'\s+\d+$', '', item['text']).strip()

    return {"title": title, "outline": sorted_outline}


if __name__ == "__main__":
    print("📄 Starting Heading extraction...")
    input_dir = Path("/app/input") 
    output_dir = Path("output") 
    output_dir.mkdir(exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDFs found in: {input_dir.resolve()}")
    else:
        for pdf_path in pdf_files:
            print(f"⚙️  Processing {pdf_path.name}...")
            try:
                result = extract_outline_generic(pdf_path)
                out_path = output_dir / f"{pdf_path.stem}.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                print(f"✅ Saved outline to: {out_path}")
            except Exception as e:
                print(f"❌ Error processing {pdf_path.name}: {e}")