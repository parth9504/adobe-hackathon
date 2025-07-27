## ✨ Challenge 1B : Persona-Based Section Extraction

    > Given multiple documents, a user persona, and a specific "job-to-be-done," intelligently identify and rank the most relevant *sections* across all documents, providing a summarized, actionable output.

## 🔧 Technical Approach & Architecture

Our solution uses a sophisticated pipeline to analyze and extract information, going beyond simple keyword searching to understand the structure and semantic meaning of the content.

The script (`round1b.py`) implements a multi-step process to deliver highly relevant, cross-document insights:

1.  **Dynamic Sectioning**: Instead of treating a PDF as a single wall of text, we first parse it into logical sections. The script uses **PyMuPDF** to analyze the font properties of the text, automatically identifying section titles (text with a larger font size than the body) and grouping the subsequent content under them.

2.  **Semantic Embedding**: We use a state-of-the-art **`sentence-transformers`** model (`paraphrase-MiniLM-L3-v2`) to convert the user's query (Persona + Job-to-be-done) and the content of each extracted section into high-dimensional vectors. This allows us to compare chunks of text based on their meaning, not just keywords.

3.  **Cross-Document Ranking**: Using **PyTorch**, we calculate the cosine similarity between the query vector and every section vector from every document. This gives us a relevance score for each section. All sections are then ranked in a single global list to find the absolute best matches, regardless of which document they came from.

4.  **Summarization & Output Generation**: The top 5 most relevant sections are selected. For each of these sections, we generate a concise, "refined text" summary by identifying the most relevant sentences within that section. The final, structured JSON is then built according to the precise output schema.

---

## 📚 Libraries & Tools

| Library                 | Version   | Purpose                                                                                                              |
| :---------------------- | :-------- | :------------------------------------------------------------------------------------------------------------------- |
| `PyMuPDF`               | `1.23.x`+ | The core tool for robust and fast PDF parsing. Used to extract text along with metadata like font size and position. |
| `sentence-transformers` | `2.x`     | Used for generating high-quality semantic embeddings of text for our relevance analysis.                             |
| `torch`                 | `2.x`     | The underlying deep learning framework required by `sentence-transformers`.                                          |
| `tqdm`                  | `4.x`     | Provides clean and helpful progress bars for a better user experience during processing.                             |

---

## ⚙️ Setup & Installation

Follow these steps to get the project running on your local machine.

1.  **Prerequisites**:

    - Python 3.9 or higher.
    - `pip` for package management.

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
    Install all required packages from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ How to Run the Solution

The script is designed to automatically find and process all `Collection` folders in its directory.

1.  **Project Structure**:
    Ensure your project directory is structured correctly. The script will look for folders that start with "Collection".

    ```
    .
    ├── Collection1/
    │   ├── PDFs/
    │   │   ├── doc1.pdf
    │   │   └── doc2.pdf
    │   ├── challenge1b_input.json
    │   └── challenge1b_output.json  <-- Script will generate/overwrite this
    ├── Collection2/
    │   ├── ...
    ├── round1b.py
    └── requirements.txt
    ```

2.  **Execute the Script**:
    Simply run the main Python script from your terminal.

    ```bash
    python round1b.py
    ```

The script will print its progress and notify you upon completion, creating a `challenge1b_output.json` file inside each `Collection` folder.

---

## 🐳 Docker Execution

For a clean, reproducible, and offline-ready environment, you can use the provided `Dockerfile`.

1.  **Build the Docker Image**:
    From the root of the project directory, run:

    ```bash
    docker build -t adobe-hackathon-1b .
    ```

    This command builds the image and pre-downloads the sentence-transformer model, so it can run without an internet connection.

2.  **Run the Container**:
    ```bash
    docker run --rm -v "$(pwd):/app" adobe-hackathon-1b
    ```
    This command will run the script inside the container. The `-v "$(pwd):/app"` part mounts your current directory into the container's `/app` directory, so the script can read your input files and write the output back to your machine.
