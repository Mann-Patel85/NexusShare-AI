from fastapi import FastAPI
import os
app=FastAPI()
@app.get("/")
def root():
    return {"message": "NexusShare is live!"}

@app.get("/files")
def file_lists():
    folder_path="shared files"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return {"message": "Folder created. Add some files into it..."}
    files=os.listdir(folder_path)
    return {"available files": files}