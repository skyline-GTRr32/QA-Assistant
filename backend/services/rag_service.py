# backend/services/rag_service.py
import os
from pathlib import Path
from typing import Dict, List, Union
import chromadb
from chromadb.utils import embedding_functions
import fitz  # PyMuPDF
from dotenv import load_dotenv
import re
import time
from openai import OpenAI
from openai import APIConnectionError, APIError, RateLimitError

load_dotenv()

class OpenAIEmbeddingFunction:
    """Custom OpenAI embedding function compatible with openai>=1.0.0"""
    
    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedding function.
        
        Args:
            api_key: OpenAI API key
            model_name: Embedding model name (text-embedding-3-small or text-embedding-3-large)
        """
        # Configure OpenAI client with timeout and retry settings
        self.client = OpenAI(
            api_key=api_key,
            timeout=60.0,  # 60 second timeout
            max_retries=3  # OpenAI client already has retry logic
        )
        self.model_name = model_name
        
        # Set dimension based on model
        if "large" in model_name:
            self.dimension = 3072
        else:
            self.dimension = 1536
    
    def __call__(self, input: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for input text(s) with retry logic.
        
        Args:
            input: Single text string or list of text strings
            
        Returns:
            Single embedding vector or list of embedding vectors
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Handle single string input
                if isinstance(input, str):
                    response = self.client.embeddings.create(
                        model=self.model_name,
                        input=input
                    )
                    return response.data[0].embedding
                
                # Handle list of strings
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=input
                )
                return [item.embedding for item in response.data]
                
            except (APIConnectionError, APIError) as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"OpenAI API error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"OpenAI API error after {max_retries} attempts: {e}")
                    raise
            except RateLimitError as e:
                wait_time = 60  # Wait 60 seconds for rate limit
                if attempt < max_retries - 1:
                    print(f"Rate limit exceeded (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"Rate limit error after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                print(f"Unexpected error generating embeddings: {e}")
                raise

class RAGService:
    def __init__(self):
        """Initialize RAG Service with ChromaDB for vector storage using OpenAI embeddings."""
        # --- FIX: REMOVED ALL LLM (Groq/OpenAI) CLIENT INITIALIZATION ---
        # This service is now only responsible for vector storage and retrieval.
        # The QA Agent will handle all LLM calls.
        
        # Get OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for embeddings")
        
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use custom OpenAI embedding function compatible with openai>=1.0.0
        # text-embedding-3-small: 1536 dimensions, faster and cheaper
        # text-embedding-3-large: 3072 dimensions, more accurate but slower
        self.embedding_function = OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )
        
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks, current_chunk, current_length = [], [], 0
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence: continue
            
            sentence_length = len(sentence.split())
            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                overlap_word_count = int(chunk_overlap / 5) 
                current_chunk = current_chunk[-overlap_word_count:]
                current_length = sum(len(s.split()) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def process_and_index_file(self, file_path: Union[str, Path], run_id: str) -> bool:
        """
        Processes a file and indexes it into a UNIQUE collection for this run.
        """
        try:
            file_path = Path(file_path)
            print(f"Extracting text from {file_path}...")
            text = self._extract_text(file_path)
            
            if not text or not text.strip():
                print(f"ERROR: No text could be extracted from {file_path}. Cannot create RAG collection.")
                return False

            print(f"Text extracted: {len(text)} characters. Chunking...")
            chunks = self.chunk_text(text)
            if not chunks:
                print(f"Warning: No text chunks were generated from the extracted text of {file_path}.")
                return False

            print(f"Created {len(chunks)} chunks. Creating collection and generating embeddings...")
            collection_name = f"run_{run_id}"
            collection = self.chroma_client.get_or_create_collection(name=collection_name, embedding_function=self.embedding_function)
            ids = [f"{run_id}_{i}" for i in range(len(chunks))]
            
            # Add documents in batches to avoid overwhelming the API
            batch_size = 10
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                batch_metadatas = [{"source": file_path.name} for _ in batch_chunks]
                
                print(f"Indexing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size} ({len(batch_chunks)} chunks)...")
                collection.add(documents=batch_chunks, metadatas=batch_metadatas, ids=batch_ids)
            
            print(f"Successfully indexed {len(chunks)} chunks into collection '{collection_name}'")
            return True
        except Exception as e:
            import traceback
            print(f"Error processing file {file_path}: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def query_collection(self, question: str, run_id: str, k: int = 5) -> Dict[str, any]:
        """
        Queries the UNIQUE collection for a specific run and returns the context.
        """
        try:
            collection_name = f"run_{run_id}"
            collection = self.chroma_client.get_collection(name=collection_name)
            results = collection.query(query_texts=[question], n_results=k)
            
            context = "\n\n".join(results['documents'][0])
            return {"context": context, "sources": results['metadatas'][0]}
            
        except Exception as e:
            print(f"Error querying collection 'run_{run_id}': {e}")
            return {"error": str(e), "context": "Could not retrieve context from the document."}

    def cleanup_collection(self, run_id: str):
        """Deletes the collection associated with a run to save space."""
        try:
            collection_name = f"run_{run_id}"
            self.chroma_client.delete_collection(name=collection_name)
            print(f"Successfully cleaned up collection '{collection_name}'")
        except Exception as e:
            print(f"Info: Could not clean up collection 'run_{run_id}' (it may not have been created): {e}")

    def _extract_text(self, file_path: Path) -> str:
        if file_path.suffix.lower() == '.pdf':
            return self._extract_from_pdf_pymupdf(file_path)
        elif file_path.suffix.lower() == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def _extract_from_pdf_pymupdf(self, file_path: Path) -> str:
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()
            return text
        except Exception as e:
            print(f"FATAL: Error reading PDF with PyMuPDF {file_path}: {e}")
            return ""

    def _extract_from_txt(self, file_path: Path) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()