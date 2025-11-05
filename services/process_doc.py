import fitz
import io
import re
import os
import base64
import uuid
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.vector_store import db_global

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                # eliminar saltos de línea múltiples
                page_text = re.sub(r'\n+', '\n', page_text)
                # eliminar encabezados tipo "Página X de Y"
                page_text = re.sub(r'Página \d+ de \d+', '', page_text)
                # eliminar líneas que parecen índices "1. OBJETIVO.- ..."
                page_text = re.sub(r'^\d+\..*$', '', page_text, flags=re.MULTILINE)
                # eliminar múltiples espacios
                page_text = re.sub(r'[ ]{2,}', ' ', page_text)
                # eliminar caracteres especiales que no aportan semántica
                page_text = re.sub(r'[•✓■]', '', page_text)
                text += page_text + "\n"
    # opcional: pasar todo a minúsculas
    text = text.lower()
    return text

def chunk_text(text, chunk_size=400, chunk_overlap=80):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,      # tamaño del chunk
        chunk_overlap=chunk_overlap # overlap para mantener contexto
    )
    chunks = splitter.split_text(text)
    return chunks

def is_base64_pdf(base64_string: str) -> bool:
    """
    Checks if a given Base64 string represents a valid PDF file.
    """
    try:
        # 1. Decode the Base64 string
        decoded_bytes = base64.b64decode(base64_string)

        # 2. Check for PDF magic bytes
        if not decoded_bytes.startswith(b'%PDF-'):
            return False

        # 3. Attempt to load with a PDF library for more robust validation
        # Wrap the bytes in a BytesIO object to simulate a file
        pdf_buffer = io.BytesIO(decoded_bytes)
        reader = PdfReader(pdf_buffer)
        
        # If no exception is raised during PdfReader initialization, it's likely a valid PDF
        # You can also add further checks, like accessing a page:
        # num_pages = len(reader.pages) 
        # if num_pages > 0:
        #     return True

        return True

    except Exception:
        # Catch any errors during decoding or PDF parsing
        return False

def is_pdf_filename(filename):
    return filename.lower().endswith(".pdf")

def save_base64_pdf(base64_string, folder_path, filename):
    """
    Decodes a Base64 string and saves it as a PDF file in the specified folder.

    Args:
        base64_string (str): The Base64 encoded PDF data.
        folder_path (str): The path to the folder where the PDF should be saved.
        filename (str): The name of the PDF file (e.g., "my_document.pdf").
    """
   
    
    os.makedirs(folder_path, exist_ok=True)

  
    pdf_data = base64.b64decode(base64_string)

   
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as f:
        f.write(pdf_data)

def index_pdf(file_path):
    filename = os.path.basename(file_path)
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    ids = [f"{filename}_{uuid.uuid4()}" for _ in chunks]
    metadatas = [{"source":filename} for _ in chunks]
    db_global.add_texts(chunks, metadatas=metadatas, ids=ids)
    


