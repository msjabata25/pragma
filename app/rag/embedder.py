import google.generativeai as genai
import os
from .chunker import CodeChunk

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
EMBEDDING_MODEL = "models/gemini-embedding-001"


#embeds user query
def embed_query (query : str) -> list[float]:
    #sample input -> 
    response = genai.embed_content(
        model= EMBEDDING_MODEL,
        content= query , 
        task_type="retrieval_query")
    return response["embedding"]


#embeds chunks -> turning words into vector values
def embed_chunks (chunks : list[CodeChunk]) -> list[dict]:
    
    results = []
    for chunk in chunks:
        text = f"File: {chunk.file_path}\nType: {chunk.chunk_type} '{chunk.name}'\n\n{chunk.content}"
        response = genai.embed_content(
            content= text,
            model= EMBEDDING_MODEL,
            task_type="retrieval_document"
        )
        results.append({
            "chunk" : chunk,
            "embedding" : response["embedding"]
        })
    return results