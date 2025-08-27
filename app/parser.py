import io
import docx
import PyPDF2


def extract_text(filename: str, file_bytes: bytes):
    ext = filename.split(".")[-1].lower()
    text = ""

    if ext == "pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

    elif ext == "docx":
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif ext == "txt":
        text = file_bytes.decode("utf-8")

    else:
        raise ValueError("Unsupported file type: " + ext)

    return ext, text
