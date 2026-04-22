import chromadb
from .chunker import CodeChunk

client = chromadb.PersistentClient(path='./chroma_db')

def get_or_create_collection(repo_id : str):
    return client.get_or_create_collection(
        name=f"pragma_{repo_id}", 
        metadata={"hnsw:space" : "cosine"}
    )

def store_chunks(repo_id : str , embedded_chunks : list[dict]):
    collection = get_or_create_collection(repo_id=repo_id)
    ids, embeddings, documents, metadata = [], [], [], []
    for item in embedded_chunks:
        chunk = item["chunk"]
        ids.append(f"{chunk.file_path}:{chunk.name}:{chunk.start_line}")
        embeddings.append(item["embedding"])
        documents.append(chunk.content)
        metadata.append({"file_path": chunk.file_path, "chunk_type": chunk.chunk_type, "name": chunk.name, "start_line": chunk.start_line, "end_line": chunk.end_line, "language": chunk.language})
    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadata)
    return len(ids)

def query_chunks(repo_id : str , query_embedding : list[float] , n_results : int = 5):
    collection = get_or_create_collection(repo_id=repo_id)
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results, include=["documents", "metadatas", "distances"])
    return [{"content": d, "metadata": m, "score": 1 - dist} for d, m, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])]

def get_chunk_count(repo_id: str) -> int:
    try:
        collection = get_or_create_collection(repo_id)
        return collection.count()
    except Exception as e:
        print(f"[store] Error: {e}")
        return 0