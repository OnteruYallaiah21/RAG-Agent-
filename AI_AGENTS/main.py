"""
===========================================================
Project: Thryvix AI - Contact Submission Service
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Simple Contact Form API - Print JSON payload and return dummy response
"""

import uvicorn
import json
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from config.settings import settings
from services.agent_tool_call import prepare_email_agent

# Initialize FastAPI app
app = FastAPI(
    title="Contact Form API",
    description="Simple contact form - print payload and return dummy response",
    version="1.0.0"
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

# Pydantic models
class ContactFormData(BaseModel):
    name: str
    email: str
    company: str
    subject: str
    message: str
    tag: str = "contact, submission, form, inquiry"

class EmailResponse(BaseModel):
    status: str
    name: str
    email: str
    company: str
    subject: str
    message: str
    reply_subject: str
    reply_body: str
    intent: str
    customer_type: str
    is_new_lead: bool
    sent: bool
    message_id: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the contact form interface"""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Contact form not found</h1>", status_code=404)

@app.post("/api/email/process", response_model=EmailResponse)
async def process_email(request_data: ContactFormData):
    """Process contact form using AI agent and return response"""
    
    # Print JSON payload received from frontend
    print("\n" + "="*60)
    print("📨 JSON PAYLOAD RECEIVED FROM FRONTEND:")
    print("="*60)
    print(json.dumps(request_data.dict(), indent=2))
    print("="*60)
    
    try:
        # Prepare input for agent
        agent_input = {
            "name": request_data.name,
            "email": request_data.email,
            "company": request_data.company,
            "subject": request_data.subject,
            "message": request_data.message,
            "tag": request_data.tag
        }
        
        print("🤖 CALLING AI AGENT...")
        print(f"Agent Input: {json.dumps(agent_input, indent=2)}")
        
        # Call the AI agent
        agent_result = prepare_email_agent(agent_input)
        
        print("✅ AI AGENT RESPONSE RECEIVED:")
        print(f"Agent Result: {json.dumps(agent_result, indent=2)}")
       
        # Map agent result to frontend response format
        response_data = {
            "status": "processed",
            "name": request_data.name,
            "email": request_data.email,
            "company": request_data.company,
            "subject": request_data.subject,
            "message": request_data.message,
            "reply_subject": agent_result["email_subject"],
            "reply_body": agent_result["email_body"],
            "intent": "contact_submission",
            "customer_type": "new_lead" if not agent_result["lead_exists"] else "existing_customer",
            "is_new_lead": not agent_result["lead_exists"],
            "sent": True,
            "message_id": f"agent_response_{request_data.email.replace('@', '_').replace('.', '_')}"
        }
        
        # Print agent response being sent
        print("🤖 AI AGENT RESPONSE SENT TO FRONTEND:")
        print("="*60)
        print(json.dumps(response_data, indent=2))
        print("="*60 + "\n")
        
        return EmailResponse(**response_data)
        
    except Exception as e:
        print(f"❌ Error processing with AI agent: {str(e)}")
        
        # Fallback to dummy response on error
        fallback_response = {
            "status": "processed",
            "name": request_data.name,
            "email": request_data.email,
            "company": request_data.company,
            "subject": request_data.subject,
            "message": request_data.message,
            "reply_subject": f"Thank you for your {request_data.subject} - Thryvix AI",
            "reply_body": f"Hi {request_data.name}!\n\nThank you for contacting Thryvix AI regarding your {request_data.subject.lower()}.\n\nWe have received your message and our team will review your inquiry. We'll get back to you within 24 hours.\n\nYour details:\n- Name: {request_data.name}\n- Email: {request_data.email}\n- Company: {request_data.company}\n- Subject: {request_data.subject}\n- Message: {request_data.message}\n\nBest regards,\nThe Thryvix AI Team",
            "intent": "contact_submission",
            "customer_type": "new_lead",
            "is_new_lead": True,
            "sent": True,
            "message_id": "fallback_response"
        }
        
        print("🤖 FALLBACK RESPONSE SENT TO FRONTEND:")
        print("="*60)
        print(json.dumps(fallback_response, indent=2))
        print("="*60 + "\n")
        
        return EmailResponse(**fallback_response)

@app.get("/api/crm/leads")
async def get_leads():
    """Get all leads from CRM"""
    try:
        from pathlib import Path
        import json
        
        crm_path = Path("data/crm/customers.json")
        
        if not crm_path.exists():
            return {"success": True, "leads": []}
        
        with open(crm_path, "r") as f:
            leads = json.load(f)
        
        # Add account_id field for frontend compatibility
        for lead in leads:
            if "account_id" not in lead:
                lead["account_id"] = f"ACC_{lead.get('id', '000')}"
        
        return {"success": True, "leads": leads}
        
    except Exception as e:
        print(f"❌ Error loading leads: {str(e)}")
        return {"success": False, "error": str(e), "leads": []}

def main():
    """Main entry point - Simple Contact Form API (DEV BRANCH)"""
    print("🚀 Contact Form API - DEV BRANCH")
    print(f"🌐 Contact Form: http://{settings.host}:{settings.port}")
    print("=" * 50)
    print("📨 Prints JSON payload from frontend")
    print("🤖 Returns AI-generated response from LLM")
    print("🔧 Development branch - Enhanced features")
    print("=" * 50)
    
    # Start the web server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

if __name__ == "__main__":
    main()