from google import genai
from google.genai import types
import os
from .chunker import CodeChunk
from dotenv import load_dotenv

load_dotenv()



client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
EMBEDDING_MODEL = "models/gemini-embedding-001"


#embeds user query
def embed_query(query: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="CODE_RETRIEVAL_QUERY")
    )
    return response.embeddings[0].values


#embeds chunks -> turning words into vector values
def embed_chunks(chunks: list[CodeChunk]) -> list[dict]:
    results = []
    for chunk in chunks:
        text = f"File: {chunk.file_path}\nType: {chunk.chunk_type} '{chunk.name}'\n\n{chunk.content}"
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        results.append({
            "chunk": chunk,
            "embedding": response.embeddings[0].values
        })
    return results