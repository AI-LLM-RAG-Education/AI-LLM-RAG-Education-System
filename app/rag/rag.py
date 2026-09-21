from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import fitz
import pytesseract
import faiss
import pickle
import io
from PIL import Image

BASE_DIR = Path(__file__).resolve().parents[2]
DOCUMENTS = BASE_DIR / "documents"
VECTOR_STORE = BASE_DIR / "vector_store"

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def load_documents():
    text = ""

    pdf_files = list(DOCUMENTS.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF(s).")

    for pdf in pdf_files:
        print(f"Reading: {pdf.name}")

        reader = PdfReader(pdf)
        doc = fitz.open(pdf)

        for page_num, page in enumerate(reader.pages):

            page_text = page.extract_text() or ""

            if page_text.strip():
                text += page_text + "\n"
                print(
                    f"Page {page_num + 1}: "
                    f"extracted {len(page_text)} characters"
                )

            else:
                image_page = doc[page_num]

                pix = image_page.get_pixmap(
                    matrix=fitz.Matrix(2, 2)
                )

                image_bytes = pix.tobytes("png")
                image = Image.open(
                    io.BytesIO(image_bytes)
                )

                page_text = pytesseract.image_to_string(image)

                text += page_text + "\n"

                print(
                    f"Page {page_num + 1}: "
                    f"OCR extracted {len(page_text)} characters"
                )

        doc.close()

    return text


def split_text(text, chunk_size=500):
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
        if text[i:i + chunk_size].strip()
    ]


def create_vector_store():
    text = load_documents()

    if not text.strip():
        print("No PDF text found.")
        return False

    chunks = split_text(text)

    print(f"Created {len(chunks)} chunks.")

    embeddings = MODEL.encode(chunks)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    VECTOR_STORE.mkdir(exist_ok=True)

    faiss.write_index(
        index,
        str(VECTOR_STORE / "index.faiss")
    )

    with open(VECTOR_STORE / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("Vector store created successfully!")

    return True


def search(query, k=3):
    index = faiss.read_index(
        str(VECTOR_STORE / "index.faiss")
    )

    with open(VECTOR_STORE / "chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    query_embedding = MODEL.encode([query])

    distances, indexes = index.search(
        query_embedding,
        k
    )

    return [chunks[i] for i in indexes[0]]


if __name__ == "__main__":

    if create_vector_store():

        print("\nTesting retrieval...\n")

        results = search(
            "What is Java?"
        )

        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(result)