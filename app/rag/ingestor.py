import uuid, os , shutil , tempfile , zipfile
from .chunker import chunk_file
from .embedder import embed_chunks
from .store import store_chunks
from git import Repo
import hashlib

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
def ingest_zip(zip_path: str) -> dict:
    try:
        repo_id = str(uuid.uuid4())
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmp_dir)
        files = _collect_files(tmp_dir)
        all_chunks = []
        for rel_path, source in files:
            chunks = chunk_file(rel_path , source)
            all_chunks.extend(chunks)
        embeded_chunks = embed_chunks(all_chunks)
        chunks_stored = store_chunks(repo_id=repo_id, embedded_chunks=embeded_chunks)
        return {"repo_id" : repo_id , "files_processed" : len(files) , "chunks_stored" : chunks_stored}
    finally:
        shutil.rmtree(tmp_dir)
        
#In case user sent github repo
def ingest_github(github_url : str) -> dict:
    try:
        repo_id = hashlib.md5(github_url.encode()).hexdigest()[:12]
        tmp_dir = tempfile.mkdtemp()
        Repo.clone_from(github_url , tmp_dir , depth=1)
        files = _collect_files(tmp_dir)
        all_chunks = []
        for rel_path, source in files:
            chunks = chunk_file(rel_path , source)
            all_chunks.extend(chunks)
        embeded_chunks = embed_chunks(all_chunks)
        chunks_stored = store_chunks(repo_id=repo_id, embedded_chunks=embeded_chunks)
        return {"repo_id" : repo_id , "files_processed" : len(files) , "chunks_stored" : chunks_stored}
    finally:
        shutil.rmtree(tmp_dir)