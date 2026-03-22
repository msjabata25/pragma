import ast
import os
from dataclasses import dataclass

@dataclass
class CodeChunk:
    content: str   # -> the code itself
    file_path: str # -> the relative file path
    chunk_type: str # -> either function, class or module
    name: str # -> the name of the chunk
    start_line: int # -> start of the chunk
    end_line: int   # -> end of chunk
    language: str   # -> programming language used



def chunk_python_file(file_path : str , source: str) -> list[CodeChunk]:
    chunks = []

#we parse the code we got so we can make it readable for the rag
    try:
        tree = ast.parse(source)
    #just incase a syntax error happens we skip the file
    except SyntaxError as e:
        print(f"⚠️ Skipping {file_path}: syntax error at line {e.lineno} — {e.msg}")
        return chunks
    #splits the source code into an array of lines
    lines = source.splitlines()
    #we walk through the source code 
    for node in ast.walk(tree):
        #we look for any functions or async functions
        if isinstance(node, (ast.FunctionDef , ast.AsyncFunctionDef)):
            chunk_lines = lines[node.lineno - 1 : node.end_lineno]
            chunks.append(CodeChunk(
                content='\n'.join(chunk_lines),
                file_path= file_path,
                chunk_type="function",
                name=node.name,
                start_line= node.lineno,
                end_line= node.end_lineno,
                language="python"
            ))
        #If we dont find any functions , look for classes
        elif isinstance(node , ast.ClassDef):
            chunk_lines = lines[node.lineno - 1 : node.end_lineno]
            chunks.append(CodeChunk(
                content='\n'.join(chunk_lines),
                file_path= file_path,
                chunk_type="class",
                name=node.name,
                start_line= node.lineno,
                end_line= node.end_lineno,
                language="python"
            ))
            #if none of them exist in the code, just return it back as is.
    if not chunks:
        chunks.append(CodeChunk(
                content=source,
                file_path=file_path,
                chunk_type="module",
                name=os.path.basename(file_path),
                start_line=1,
                end_line=len(lines),
                language="python"
            ))
    return chunks


def chunk_file(file_path: str, source: str) -> list[CodeChunk]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".py":
        return chunk_python_file(file_path, source)
    # unsupported language fallback
    return [CodeChunk(
        content=source,
        file_path=file_path,
        chunk_type="module",
        name=os.path.basename(file_path),
        start_line=1,
        end_line=source.count("\n") + 1,
        language=ext.lstrip(".")
    )]
