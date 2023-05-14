from typing import List, Dict
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

app = FastAPI()

ORIGINS = [
    "http://localhost:8000",
    "https://chat.openai.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS: Dict[str, List[str]] = {}

class TodoItem(BaseModel):
    todo: str

class TodoIndex(BaseModel):
    todo_idx: int

@app.post("/todos/{username}", status_code=201)
async def add_todo(username: str, todo: TodoItem) -> Dict[str, str]:
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(todo.todo)
    return {"status": 'OK'}

@app.get("/todos/{username}", response_model=List[str])
async def get_todos(username: str) -> List[str]:
    return _TODOS.get(username, [])

@app.delete("/todos/{username}", status_code=204)
async def delete_todo(username: str, todo_index: TodoIndex):
    todos = _TODOS.get(username, [])
    if todo_index.todo_idx < len(todos):
        todos.pop(todo_index.todo_idx)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

@app.get("/logo.png")
async def plugin_logo() -> FileResponse:
    return FileResponse('logo.png', media_type='image/png')

@app.get("/openapi.yaml")
async def openapi_spec() -> Response:
    with open("openapi.yaml") as f:
        return Response(f.read(), media_type="text/yaml")
