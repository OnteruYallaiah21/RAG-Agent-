"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Simple FastAPI web server with LLM integration.
Provides REST API endpoints for text generation and email processing.

Main Use:
---------
Web server that:
1. Provides REST API endpoints for text generation
2. Handles email processing with LLM fallback
3. Serves the web interface and static files
4. Uses simple LLM manager with fallback logic
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from agents.llm_manager import llm_manager
from agents.email_workflow import email_workflow
from services.file_logger import FileLogger
from utils.logger import logger

# Initialize file logger
file_logger = FileLogger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting AI Agents web server...")
    yield
    logger.info("Shutting down AI Agents web server...")

# Create FastAPI app
app = FastAPI(
    title="AI Agents API",
    description="Simple AI Agents with LLM fallback",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": {}})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard interface."""
    return templates.TemplateResponse("dashboard.html", {"request": {}})

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model_info = llm_manager.get_model_info()
    return {
        "status": "healthy",
        "models": model_info["available_models"],
        "model_count": model_info["model_count"]
    }

@app.post("/api/generate")
async def generate_text(
    prompt: str,
    system_prompt: Optional[str] = None,
    preferred_model: Optional[str] = None
):
    """Generate text using available LLM models with fallback."""
    try:
        result = await llm_manager.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            preferred_model=preferred_model
        )
        
        # Log the request
        file_logger.log_request({
            "endpoint": "/api/generate",
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "model_used": result.get("model_used"),
            "success": result["success"],
            "processing_time": result.get("processing_time", 0)
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/email/reply")
async def generate_email_reply(
    sender_name: str,
    email_content: str,
    preferred_model: Optional[str] = None
):
    """Generate email reply with fallback logic."""
    try:
        reply = await llm_manager.generate_email_reply(
            sender_name=sender_name,
            email_content=email_content,
            preferred_model=preferred_model
        )
        
        # Log the request
        file_logger.log_request({
            "endpoint": "/api/email/reply",
            "sender_name": sender_name,
            "email_content": email_content[:100] + "..." if len(email_content) > 100 else email_content,
            "success": True
        })
        
        return {
            "success": True,
            "reply": reply,
            "sender_name": sender_name
        }
        
    except Exception as e:
        logger.error(f"Error in generate_email_reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/email/extract-sender")
async def extract_sender_name(
    email_content: str,
    preferred_model: Optional[str] = None
):
    """Extract sender name from email content."""
    try:
        sender_name = await llm_manager.extract_sender_name(
            email_content=email_content,
            preferred_model=preferred_model
        )
        
        # Log the request
        file_logger.log_request({
            "endpoint": "/api/email/extract-sender",
            "email_content": email_content[:100] + "..." if len(email_content) > 100 else email_content,
            "sender_name": sender_name,
            "success": True
        })
        
        return {
            "success": True,
            "sender_name": sender_name
        }
        
    except Exception as e:
        logger.error(f"Error in extract_sender_name: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/email/process")
async def process_email(
    email_data: Dict[str, Any]
):
    """Process email using complete workflow with proper payload structure."""
    try:
        # Validate required fields
        if "email" not in email_data:
            raise HTTPException(status_code=400, detail="Missing 'email' field in payload")
        
        email_info = email_data["email"]
        required_fields = ["from", "name", "subject", "Email_Content"]
        for field in required_fields:
            if field not in email_info:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Process email through complete workflow
        result = await email_workflow.process_email(email_data)
        
        # Log the request
        file_logger.log_request({
            "endpoint": "/api/email/process",
            "from": email_info["from"],
            "name": email_info["name"],
            "subject": email_info["subject"],
            "success": result.get("status") == "processed"
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in process_email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/email/process-simple")
async def process_email_simple(
    email_content: str,
    preferred_model: Optional[str] = None
):
    """Simple email processing - extract sender and generate reply."""
    try:
        # Extract sender name
        sender_name = await llm_manager.extract_sender_name(
            email_content=email_content,
            preferred_model=preferred_model
        )
        
        # Generate reply
        reply = await llm_manager.generate_email_reply(
            sender_name=sender_name or "there",
            email_content=email_content,
            preferred_model=preferred_model
        )
        
        # Log the request
        file_logger.log_request({
            "endpoint": "/api/email/process-simple",
            "email_content": email_content[:100] + "..." if len(email_content) > 100 else email_content,
            "sender_name": sender_name,
            "success": True
        })
        
        return {
            "success": True,
            "sender_name": sender_name,
            "reply": reply
        }
        
    except Exception as e:
        logger.error(f"Error in process_email_simple: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_available_models():
    """Get list of available models."""
    try:
        model_info = llm_manager.get_model_info()
        return {
            "success": True,
            "models": model_info["available_models"],
            "model_count": model_info["model_count"],
            "model_order": model_info["model_order"]
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crm/leads")
async def get_crm_leads():
    """Get all CRM leads data."""
    try:
        import json
        import os
        
        crm_file = "data/crm/customers.json"
        if os.path.exists(crm_file):
            with open(crm_file, 'r') as f:
                customers = json.load(f)
        else:
            customers = []
        
        return {
            "success": True,
            "leads": customers,
            "total_count": len(customers),
            "new_leads": len([c for c in customers if c.get("status") == "New Lead"]),
            "existing_leads": len([c for c in customers if c.get("status") == "Existing Lead"])
        }
    except Exception as e:
        logger.error(f"Error getting CRM leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notifications")
async def get_notifications():
    """Get recent notifications."""
    try:
        # This would typically come from a database or notification service
        notifications = [
            {
                "id": 1,
                "message": "New lead added: Emily Chen",
                "type": "new_lead",
                "timestamp": "2025-09-08T15:30:00",
                "read": False
            },
            {
                "id": 2,
                "message": "Existing lead contacted: Sarah Johnson",
                "type": "existing_lead",
                "timestamp": "2025-09-08T16:21:19",
                "read": False
            },
            {
                "id": 3,
                "message": "Sales team notified for new lead",
                "type": "sales_notification",
                "timestamp": "2025-09-08T15:30:05",
                "read": True
            }
        ]
        
        return {
            "success": True,
            "notifications": notifications,
            "unread_count": len([n for n in notifications if not n["read"]])
        }
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch/process")
async def batch_process_emails(
    emails: List[Dict[str, Any]],
    preferred_model: Optional[str] = None
):
    """Process multiple emails in batch."""
    try:
        results = []
        
        for i, email in enumerate(emails):
            try:
                email_content = email.get("content", "")
                sender_name = email.get("sender_name")
                
                if not sender_name:
                    sender_name = await llm_manager.extract_sender_name(
                        email_content=email_content,
                        preferred_model=preferred_model
                    )
                
                reply = await llm_manager.generate_email_reply(
                    sender_name=sender_name or "there",
                    email_content=email_content,
                    preferred_model=preferred_model
                )
                
                results.append({
                    "index": i,
                    "success": True,
                    "sender_name": sender_name,
                    "reply": reply
                })
                
            except Exception as e:
                logger.error(f"Error processing email {i}: {e}")
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        # Log the batch request
        file_logger.log_request({
            "endpoint": "/api/batch/process",
            "email_count": len(emails),
            "success_count": sum(1 for r in results if r["success"]),
            "success": True
        })
        
        return {
            "success": True,
            "results": results,
            "total_processed": len(results),
            "successful": sum(1 for r in results if r["success"])
        }
        
    except Exception as e:
        logger.error(f"Error in batch_process_emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web_server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )