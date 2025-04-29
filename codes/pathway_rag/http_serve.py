"""
This module provides an HTTP server for file uploads using FastAPI.
"""
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import time

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads" # Directory to store uploaded files
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...),filename: str = Form(None)):
    """
    Uploads a file to the server.

    Args:
        file (UploadFile): The file to be uploaded.
        filename (str): The name of the file.

    Returns:
        dict: A dictionary containing a message and the filename.
    """
    try:
        # Use the provided filename if available, otherwise use the original filename
        original_filename = filename or file.filename
        
        # Check if a file with the same name already exists
        file_path = os.path.join(UPLOAD_DIR, original_filename)
        if os.path.exists(file_path):
            # If it exists, add a timestamp to make it unique
            timestamp = int(time.time())
            name, extension = os.path.splitext(original_filename)
            new_filename = f"{name}_{timestamp}{extension}"
            file_path = os.path.join(UPLOAD_DIR, new_filename)
        else:
            new_filename = original_filename

        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return {"message": "File uploaded successfully", "filename": new_filename}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


