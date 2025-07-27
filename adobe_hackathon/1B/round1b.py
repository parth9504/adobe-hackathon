import os
import json
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
import torch
from tqdm import tqdm
import re
from collections import Counter
import datetime

# --- Configuration & Model Loading ---
MODEL_NAME = 'paraphrase-MiniLM-L3-v2'
try:
    model = SentenceTransformer(MODEL_NAME)
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    exit()

# --- Core Functions ---

def get_most_common_font_size(doc):
    """Analyzes the document to find the most common font size, likely body text."""
    sizes = []
    for page in doc:
        # The 'flags' parameter has been removed for better compatibility
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            # Check if block contains lines to avoid errors
            if not b.get("lines"):
                continue
            for l in b["lines"]:
                for s in l["spans"]:
                    sizes.append(round(s["size"]))
    if not sizes:
        return 10  # Default body size if no text is found
    return Counter(sizes).most_common(1)[0][0]

def extract_sections_from_pdf(pdf_path):
    """
    Extracts structured sections (title, content, page_number) from a PDF.
    Identifies titles based on font size being larger than the document's body text.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return []

    body_font_size = get_most_common_font_size(doc)
    heading_threshold = body_font_size * 1.15  # Titles are slightly larger

    sections = []
    current_content = ""
    current_title = "Introduction"  # Default title for content at the beginning
    start_page = 1

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if not b.get("lines"):
                continue
            try:
                block_text = " ".join([s["text"] for l in b["lines"] for s in l["spans"]]).strip()
                block_size = round(b["lines"][0]["spans"][0]["size"])
            except (IndexError, KeyError):
                continue

            if block_size > heading_threshold and len(block_text) < 100:
                if current_content.strip():
                    sections.append({
                        "title": current_title,
                        "content": current_content.strip(),
                        "page_number": start_page
                    })
                current_title = block_text
                current_content = ""
                start_page = page_num + 1
            else:
                block_full_text = " ".join([s["text"] for l in b["lines"] for s in l["spans"]]).strip()
                current_content += " " + block_full_text

    if current_content.strip():
        sections.append({
            "title": current_title,
            "content": current_content.strip(),
            "page_number": start_page
        })

    return sections

def get_refined_summary(text_content, query, top_k=3):
    """Extracts the most relevant sentences from a text block to form a summary."""
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text_content)
    clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not clean_sentences:
        return text_content[:500]

    query_embedding = model.encode(query, convert_to_tensor=True)
    sentence_embeddings = model.encode(clean_sentences, convert_to_tensor=True)
    
    cosine_scores = util.cos_sim(query_embedding, sentence_embeddings)[0]
    top_results = torch.topk(cosine_scores, k=min(top_k, len(clean_sentences)))
    
    top_indices = sorted(top_results.indices.tolist())
    summary = " ".join([clean_sentences[i] for i in top_indices])
    return summary

def process_challenge(base_dir="."):
    """Main function to process all 'Collection' folders."""
    for folder_name in os.listdir(base_dir):
        collection_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(collection_path) and folder_name.lower().startswith("collection"):
            print(f"\n📂 Processing: {folder_name}")
            
            input_path = os.path.join(collection_path, "challenge1b_input.json")
            output_path = os.path.join(collection_path, "challenge1b_output.json")
            pdf_dir = os.path.join(collection_path, "PDFs")

            if not os.path.exists(input_path):
                print(f"  ❌ Input file not found in {folder_name}. Skipping.")
                continue

            with open(input_path, "r", encoding='utf-8') as f:
                input_data = json.load(f)

            all_sections = []
            persona = input_data["persona"]["role"]
            job = input_data["job_to_be_done"]["task"]
            query = f"Task for a {persona}: {job}"

            print(f"  🔍 Analyzing documents for query: '{query}'")
            for doc_info in tqdm(input_data["documents"], desc="  Parsing PDFs"):
                pdf_path = os.path.join(pdf_dir, doc_info["filename"])
                if not os.path.exists(pdf_path):
                    continue
                
                sections = extract_sections_from_pdf(pdf_path)
                for section in sections:
                    content_embedding = model.encode(section["content"])
                    query_embedding = model.encode(query)
                    score = util.cos_sim(content_embedding, query_embedding).item()
                    
                    section["document"] = doc_info["filename"]
                    section["relevance_score"] = score
                    all_sections.append(section)

            all_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
            top_5_sections = all_sections[:5]

            output_json = {
                "metadata": {
                    "input_documents": [d["filename"] for d in input_data["documents"]],
                    "persona": persona,
                    "job_to_be_done": job,
                    "processing_timestamp": datetime.datetime.now().isoformat()
                },
                "extracted_sections": [],
                "subsection_analysis": []
            }

            for i, section in enumerate(top_5_sections):
                output_json["extracted_sections"].append({
                    "document": section["document"],
                    "section_title": section["title"],
                    "importance_rank": i + 1,
                    "page_number": section["page_number"]
                })
                
                refined_text = get_refined_summary(section["content"], query)
                output_json["subsection_analysis"].append({
                    "document": section["document"],
                    "refined_text": refined_text,
                    "page_number": section["page_number"]
                })

            with open(output_path, "w", encoding='utf-8') as f:
                json.dump(output_json, f, indent=4, ensure_ascii=False)
            
            print(f"\n  ✅ Output successfully written to {output_path}")

if __name__ == "__main__":
    process_challenge()