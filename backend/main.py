from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import os
import shutil

app = FastAPI(title="Notes API")

NOTES_DIR = "notes"
os.makedirs(NOTES_DIR, exist_ok=True)

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    content: str

def get_note_path(title: str) -> str:
    # Sanitize title to avoid path traversal
    safe_title = "".join(c for c in title if c.isalnum() or c in " ._-")
    return os.path.join(NOTES_DIR, f"{safe_title}.md")

@app.get("/notes", response_class=PlainTextResponse)
def list_notes():
    files = [f.replace(".md", "") for f in os.listdir(NOTES_DIR) if f.endswith(".md")]
    return "\n".join(sorted(files))

@app.get("/notes/{title}", response_class=PlainTextResponse)
def read_note(title: str):
    path = get_note_path(title)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Note not found")
    with open(path, "r") as f:
        return f.read()

@app.post("/notes/{title}", status_code=201)
def create_note(title: str, note: NoteCreate):
    if title != note.title:
        raise HTTPException(status_code=400, detail="Title mismatch")
    path = get_note_path(title)
    if os.path.exists(path):
        raise HTTPException(status_code=409, detail="Note already exists")
    with open(path, "w") as f:
        f.write(note.content)
    return {"message": "Note created"}

@app.put("/notes/{title}")
def update_note(title: str, note: NoteUpdate):
    path = get_note_path(title)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Note not found")
    with open(path, "w") as f:
        f.write(note.content)
    return {"message": "Note updated"}

@app.delete("/notes/{title}")
def delete_note(title: str):
    path = get_note_path(title)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Note not found")
    os.remove(path)
    return {"message": "Note deleted"}