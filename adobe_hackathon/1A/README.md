## ✨ Challenge Tackled

- **Challenge 1A: Structured Outline Extraction**
  > Automatically extract a hierarchical outline (H1, H2, H3) from a PDF document, identifying the title and organizing the content structure into a clean JSON format.

---

## 🔧 Technical Approach & Architecture

Our solution uses a sophisticated, multi-tiered hybrid model to ensure high accuracy across a wide variety of document layouts.

1.  **Layout-Aware Parsing**: The process begins by parsing the PDF using **`pdfplumber`**. Unlike basic text extraction, this library provides detailed, word-level information, including font name, size, and precise coordinates. This rich data is the foundation for all subsequent analysis.

2.  **Heuristic Filtering & Title Detection**: Before identifying headings, the script performs a cleaning pass to remove "garbage" lines like page numbers, footers, or decorative separators. It then heuristically identifies the document's main title by scoring lines on the first page based on their font size and boldness.

3.  **Hybrid Heading Classification**: This is the core of our solution. To accurately classify heading levels (H1, H2, H3), we use a three-tier strategy:
    - **Tier 1: Regex-Based Rules**: The script first checks for explicit numbering patterns (e.g., `2.1`, `3.1.2`, `Appendix A`). This is the fastest and most reliable method for well-structured documents.
    - **Tier 2: Style-Based Analysis**: If no numbering pattern is found, the script falls back to visual styling. It identifies all unique heading styles (combinations of font size and boldness), ranks them, and maps the most prominent styles to H1, the next to H2, and so on.
    - **Tier 3: Semantic Fallback**: For ambiguous lines that aren't caught by the first two tiers, the script uses a **`sentence-transformers`** model as a final check. It compares the semantic meaning of a potential heading to a list of known heading templates (e.g., "Introduction", "Use Case"). This allows the model to intelligently classify headings even when their styling is inconsistent.

This hybrid approach makes the extractor robust, resilient, and accurate for both conventionally formatted and unstructured documents.

---

## 📚 Libraries & Tools

| Library                 | Purpose                                                                                              |
| :---------------------- | :--------------------------------------------------------------------------------------------------- |
| `pdfplumber`            | The core library for extracting rich, structured data (text, fonts, coordinates) from PDF files.     |
| `sentence-transformers` | Used for the semantic fallback model, allowing for intelligent classification of ambiguous headings. |
| `torch`                 | The underlying deep learning framework required by `sentence-transformers`.                          |

---

## ⚙️ Setup & Installation

1.  **Prerequisites**: Python 3.9+
2.  **Clone the Repository**:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```
3.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ How to Run the Solution

1.  **File Structure**:
    The script expects input PDFs to be in an `input` folder in the project's root directory. It will create an `output` folder for the results.

    ```
    .
    ├── input/
    │   ├── document1.pdf
    │   └── document2.pdf
    ├── output/                 <-- Will be created by the script
    │   ├── document1.json
    │   └── document2.json
    ├── round1a.py
    └── requirements.txt
    ```

2.  **Execute the Script**:
    Run the script from your terminal. It will automatically process all PDFs in the `./input` directory.
    ```bash
    python round1a.py
    ```

---

## 🐳 Docker Execution

The provided `Dockerfile` allows for easy, dependency-free execution.

1.  **Build the Docker Image**:
    From the root of the project directory, run:

    ```bash
    docker build -t adobe-hackathon-1a .
    ```

2.  **Run the Container**:
    You must map your local `input` and `output` folders to the corresponding directories inside the container.

        ```bash
        docker run --rm \
          -v "$(pwd)/input:/app/input" \
          -v "$(pwd)/output:/app/output" \
          adobe-hackathon-1a
        ```

    This command ensures the script inside the container can access your PDFs and save the JSON results back to your local machine.
