from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from sentence_transformers import SentenceTransformer, util
from io import BytesIO
import requests
import PyPDF2
import uuid
import re

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load SentenceTransformer model
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    raise RuntimeError(f"Failed to load embedding model: {str(e)}")

# In-memory storage for processed data
data_store = {}

# Helper function to clean and normalize text
def clean_text(text: str) -> str:
    """Clean and normalize text by removing extra whitespace."""
    return re.sub(r'\s+', ' ', text).strip()

def chunk_text(text: str, chunk_size: int = 500):
    """Splits text into smaller chunks for better embedding and comparison."""
    sentences = re.split(r'(?<=[.!?]) +', text)  # Split into sentences
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Root endpoint for status check (GET method)
@app.get("/")
def read_root():
    return {"message": "FastAPI server is running successfully!"}

# Endpoint to check if /process_url is ready (GET method)
@app.get("/process_url")
def process_url_status():
    return {"message": "The /process_url endpoint is ready to accept POST requests."}

# Endpoint to check if /process_pdf is ready (GET method)
@app.get("/process_pdf")
def process_pdf_status():
    return {"message": "The /process_pdf endpoint is ready to accept POST requests."}

# Endpoint to check if /chat is ready (GET method)
@app.get("/chat")
def chat_status():
    return {"message": "The /chat endpoint is ready to accept POST requests."}

# Endpoint to process a URL (POST method)
@app.post("/process_url")
async def process_url(url: str = Form(...)):
    try:
        # Validate URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or parsed_url.scheme not in ["http", "https"]:
            raise HTTPException(status_code=400, detail="Invalid URL format. Use http:// or https://")

        # Add User-Agent to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        }

        # Fetch and process content
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        text = clean_text(soup.get_text())

        if not text:
            raise HTTPException(status_code=400, detail="Extracted content is empty.")

        # Chunk text and compute embeddings
        chunks = chunk_text(text)
        embeddings = [embedding_model.encode(chunk, convert_to_tensor=True) for chunk in chunks]

        # Store data with unique ID
        chat_id = str(uuid.uuid4())
        data_store[chat_id] = {"type": "url", "chunks": chunks, "embeddings": embeddings}

        return {"chat_id": chat_id, "message": "URL content processed successfully."}
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Endpoint to process a PDF file (POST method)
@app.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...)):
    try:
        # Validate file extension
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Uploaded file is not a PDF.")

        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(BytesIO(await file.read()))
        extracted_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text found in the PDF.")

        # Chunk text and compute embeddings
        chunks = chunk_text(clean_text(extracted_text))
        embeddings = [embedding_model.encode(chunk, convert_to_tensor=True) for chunk in chunks]

        # Store data with unique ID
        chat_id = str(uuid.uuid4())
        data_store[chat_id] = {"type": "pdf", "chunks": chunks, "embeddings": embeddings}

        return {"chat_id": chat_id, "message": "PDF content processed successfully."}
    except PyPDF2.errors.PdfReadError as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Endpoint to query processed data (POST method)
@app.post("/chat")
async def chat(chat_id: str = Form(...), question: str = Form(...)):
    try:
        if chat_id not in data_store:
            raise HTTPException(status_code=404, detail="Chat ID not found.")

        stored_data = data_store[chat_id]
        question_embedding = embedding_model.encode(question, convert_to_tensor=True)

        # Calculate similarities with each chunk
        similarities = [
            util.pytorch_cos_sim(question_embedding, emb).item()
            for emb in stored_data["embeddings"]
        ]

        # Find the most relevant chunk
        max_similarity = max(similarities)
        best_chunk = stored_data["chunks"][similarities.index(max_similarity)]

        return {
            "query": question,
            "response": best_chunk if max_similarity > 0.2 else "No highly relevant content found.",
            "similarity": max_similarity,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
