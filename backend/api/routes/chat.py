"""
Chat API Routes
Handles chat messages to the AI Financial Risk Assistant.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional
from sqlalchemy.orm import Session
from database.connection import get_db
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("")
def ask_assistant(
    message: str = Body(..., embed=True),
    dataset_id: Optional[int] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """Ask the AI Financial Risk Assistant a question about the active dataset."""
    try:
        response = ChatService.ask_assistant(message, dataset_id, db)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assistant error: {str(e)}")
