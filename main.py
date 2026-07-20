from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
@app.get("/files")
def file_lists():
    folder_path="shared files"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return {"message": "Folder created. Add some files into it..."}
    files=os.listdir(folder_path)
    return {"available files": files}