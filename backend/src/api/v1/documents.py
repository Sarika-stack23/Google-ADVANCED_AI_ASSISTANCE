"""
Document Upload API — /api/v1/documents endpoints.
Handles PDF uploading and chunking for custom RAG.
"""

import logging
import tempfile
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from backend.src.api.middleware.auth import verify_firebase_token
from backend.src.services.qdrant_service import QdrantService

logger = logging.getLogger("math_assistant.api.documents")
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), uid: str = Depends(verify_firebase_token)):
    """Upload a PDF file and add it to the knowledge base."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
            
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        
        # Add metadata so user knows it's a custom uploaded doc
        for doc in docs:
            doc.metadata["source_file"] = file.filename
            doc.metadata["uploaded_by"] = uid
            doc.metadata["is_custom"] = True
            
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
        
        qdrant = QdrantService()
        qdrant.add_documents(chunks)
        
        os.unlink(tmp_path)
        
        return {
            "status": "success", 
            "message": f"Successfully processed {file.filename}",
            "chunks_added": len(chunks)
        }
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
