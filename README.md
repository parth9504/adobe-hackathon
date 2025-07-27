# 🚀 Adobe India Hackathon 2025 — Round 1 Submission

## Team: Lunatic Coders

This repository contains our solution to **Round 1 of the Adobe India Hackathon**, focused on extracting insights from PDF documents using both rule-based and transformer-powered methods.

---

## 📌 Overview

We tackled two key challenges:

### 🔹 Round 1A — Heading Extraction

> Automatically extract structured headings (H1, H2, H3) from PDFs, including identifying the document title and organizing the content as an outline.

### 🔹 Round 1B — Persona-based Document Summarization

> Given a specific user persona and a job-to-be-done, identify and extract the top relevant sections across multiple documents using semantic similarity.

---

## 💡 Our Approach

### 🔍 Round 1A — Heading Detection (`round1a.py`)

- **Tool Used**: [`pdfplumber`](https://github.com/jsvine/pdfplumber) for layout-aware text extraction.
- **Rule-based features**: Font size, boldness, all-caps, and indentation.
- **Regex detection**: Numbered headings like `1.2.3`, `2.1`, etc.
- **Semantic fallback**: Used `SentenceTransformer (paraphrase-MiniLM-L3-v2)` to classify ambiguous headings when styling is unclear.
- **Cleaned junk lines**: Page numbers, footers, and separator lines are filtered.

**📦 Output Format:**

```json
{
  "title": "Sample Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "1. Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "1.1 Overview",
      "page": 2
    }
  ]
}
```

### 🔍 Round 1B — Role-based Summarization (file: `round1b.py`)

- **Tool Used**: [`pdfplumber`](https://github.com/jsvine/pdfplumber) for page-wise text extraction.
- **Heading-based segmentation**: Sections split using regex patterns targeting numbered headings and appendix sections.
- **Query formulation**: Persona and job-to-be-done are merged into a natural language task prompt.
- **Embedding Model**: Used `SentenceTransformer (all-MiniLM-L6-v2)` to embed both sections and query.
- **Semantic search**: Cosine similarity ranking is used to find the most relevant content across documents.
- **Top-k selection**: Returns top 10 most relevant sections with metadata and snippet previews.

**📦 Output Format:**

```json
{
  "metadata": {
    "persona": "Investment Analyst",
    "job_to_be_done": "Analyze revenue trends, R&D investments, and market positioning strategies",
    ...
  },
  "extracted_sections": [
    {
      "document": "filename.pdf",
      "page_number": 3,
      "section_title": "2.1 Revenue Trends",
      "importance_rank": 1
    }
  ],
  "sub_section_analysis": [
    {
      "document": "filename.pdf",
      "page_number": 3,
      "refined_text": "This section discusses revenue growth across fiscal years..."
    }
  ]
}
```
