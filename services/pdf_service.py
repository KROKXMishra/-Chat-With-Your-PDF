import hashlib
import tempfile
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from utils.text_cleaner import clean_text


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"


# Extract text from PDF bytes
def extract_pdf(file_bytes):

    if not file_bytes:
        raise ValueError("The uploaded PDF is empty.")

    # Basic PDF signature validation
    if not file_bytes.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    temp_path = None

    try:

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as temp_file:

            temp_file.write(file_bytes)

            temp_path = Path(temp_file.name)

        # Extract PDF pages
        loader = PyPDFLoader(str(temp_path))

        docs = loader.load()

        if not docs:
            raise ValueError("No pages found in the PDF.")

        # Clean extracted text
        for doc in docs:

            doc.page_content = clean_text(
                doc.page_content
            )

        # Remove empty pages
        docs = [
            doc for doc in docs
            if doc.page_content.strip()
        ]

        if not docs:
            raise ValueError(
                "No readable text found in the PDF."
            )

        return docs

    finally:

        # Always remove temporary PDF
        if temp_path and temp_path.exists():

            temp_path.unlink()


# Save original PDF permanently
def save_uploaded_pdf(file_bytes, user_id, pdf_hash):

    if not file_bytes:
        raise ValueError("Cannot save an empty PDF.")

    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user ID.")

    # Validate SHA-256 hash
    expected_hash = hashlib.sha256(
        file_bytes
    ).hexdigest()

    if pdf_hash != expected_hash:
        raise ValueError("Invalid PDF hash.")

    # Create user-specific directory
    user_dir = (
        UPLOAD_DIR / f"user_{user_id}"
    )

    user_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Store PDF using its hash
    pdf_path = user_dir / f"{pdf_hash}.pdf"

    resolved_dir = user_dir.resolve()
    resolved_path = pdf_path.resolve()

    if not resolved_path.is_relative_to(resolved_dir):
        raise ValueError("Invalid PDF storage path.")

    # Save original PDF
    resolved_path.write_bytes(file_bytes)

    # Return relative path
    return str(
        resolved_path.relative_to(BASE_DIR)
    )


# Validate saved PDF path
def get_safe_pdf_path(pdf_path, user_id):

    if not pdf_path:
        raise ValueError("PDF path is missing.")

    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user ID.")

    # Resolve requested path
    full_path = (
        BASE_DIR / pdf_path
    ).resolve()

    # Expected user directory
    user_dir = (
        UPLOAD_DIR / f"user_{user_id}"
    ).resolve()

    # Ensure PDF belongs to this user
    if not full_path.is_relative_to(user_dir):
        raise ValueError("Invalid PDF path.")

    # Only allow PDF files
    if full_path.suffix.lower() != ".pdf":
        raise ValueError("Invalid PDF file extension.")

    if not full_path.is_file():
        raise FileNotFoundError(
            "Saved PDF not found."
        )

    return full_path


# Load previously saved PDF
def load_saved_pdf(pdf_path, user_id):

    full_path = get_safe_pdf_path(
        pdf_path,
        user_id
    )

    return extract_pdf(
        full_path.read_bytes()
    )


# Delete saved PDF
def delete_saved_pdf(pdf_path, user_id):

    if not pdf_path:
        return

    full_path = get_safe_pdf_path(
        pdf_path,
        user_id
    )

    full_path.unlink()