from google import genai
from google.genai import types
import os
import time
from .chunker import CodeChunk
from dotenv import load_dotenv


load_dotenv()

os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/tmp/st_cache"  # ← here
os.environ["HF_HOME"] = "/tmp/hf_cache"          

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
EMBEDDING_MODEL = "models/gemini-embedding-001"
BATCH_SIZE = 50  # Gemini supports up to 100 per batch call


def embed_query(query: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="CODE_RETRIEVAL_QUERY")
    )
    return response.embeddings[0].values


def embed_chunks(chunks: list[CodeChunk]) -> list[dict]:
    results = []
    
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [
            f"File: {c.file_path}\nType: {c.chunk_type} '{c.name}'\n\n{c.content}"
            for c in batch
        ]
        
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts,  # list = batch call
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            )
        except Exception as e:
            # rate limit or API error — wait and retry once
            print(f"[embedder] batch {i//BATCH_SIZE} failed: {e}, retrying in 10s…")
            time.sleep(10)
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            )
        
        for chunk, embedding in zip(batch, response.embeddings):
            results.append({
                "chunk": chunk,
                "embedding": embedding.values
            })
    
    return results