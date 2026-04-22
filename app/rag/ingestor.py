import uuid, os , shutil , tempfile , zipfile
from .chunker import chunk_file
from .embedder import embed_chunks
from .store import store_chunks
from git import Repo
import hashlib
import os
import shutil
import stat
REPOS_DIR = "repos"
def force_rmtree(path):
    def onerror(func, path, exc_info):
        # Clear the read-only bit and retry
        os.chmod(path, stat.S_IWRITE)
        func(path)
        
    if os.path.exists(path):
        shutil.rmtree(path, onerror=onerror)


def _collect_files(root_dir : str) -> list[tuple[str, str]]:
    files  = [] #empty files list
    for dirpath, dirnames, filenames in os.walk(root_dir): #dirpath is the directory of the file, filenames are the names of the files
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext == ".py":
                full_path = os.path.join(dirpath , fname)
                rel_path = os.path.relpath(full_path, root_dir)
                with open(full_path, "r" , encoding="utf-8", errors="ignore")as f:
                    source = f.read() #opens and reads the file
                files.append((rel_path, source))
    return files

#In case user sent a zip
REPOS_DIR = "repos"  # add this at the top

def ingest_zip(zip_path: str) -> dict:
    repo_id = str(uuid.uuid4())
    repo_dir = os.path.join(REPOS_DIR, repo_id)
    os.makedirs(repo_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(repo_dir)
    
    files = _collect_files(repo_dir)
    all_chunks = []
    for rel_path, source in files:
        chunks = chunk_file(rel_path, source)
        all_chunks.extend(chunks)
    
    embedded_chunks = embed_chunks(all_chunks)
    chunks_stored = store_chunks(repo_id=repo_id, embedded_chunks=embedded_chunks)
    return {"repo_id": repo_id, "files_processed": len(files), "chunks_stored": chunks_stored}

def ingest_github(github_url: str) -> dict:
    repo_id = hashlib.md5(github_url.encode()).hexdigest()[:12]
    repo_dir = os.path.join(REPOS_DIR, repo_id)
    os.makedirs(repo_dir, exist_ok=True)
    
    if not os.listdir(repo_dir):  # skip re-cloning if already exists
        Repo.clone_from(github_url, repo_dir, depth=1)
    
    files = _collect_files(repo_dir)
    all_chunks = []
    for rel_path, source in files:
        chunks = chunk_file(rel_path, source)
        all_chunks.extend(chunks)
    
    embedded_chunks = embed_chunks(all_chunks)
    chunks_stored = store_chunks(repo_id=repo_id, embedded_chunks=embedded_chunks)
    return {"repo_id": repo_id, "files_processed": len(files), "chunks_stored": chunks_stored}