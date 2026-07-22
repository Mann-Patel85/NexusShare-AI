from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # The modern, updated syntax for rendering Jinja templates
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/files")
def file_lists():
    folder_path = "shared_files"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return {"message": "Folder created. Add some files into it..."}
        
    files = os.listdir(folder_path)
    return {"available_files": files}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs("shared_files", exist_ok=True)
    
    file_location = f"shared_files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    return {"filename": file.filename, "message": "Upload successful!"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"shared_files/{filename}"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    return {"error": "File not found"}