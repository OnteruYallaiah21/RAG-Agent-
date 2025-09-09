# agent_email_crm.py
import json
from pathlib import Path
import os
import getpass
from typing import Dict
from datetime import datetime

# Install Groq support: pip install -qU "langchain[groq]"
from langchain.chat_models import init_chat_model
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# -------------------------
# Config / Paths
# -------------------------
CRM_PATH = Path("data/crm/customers.json")

# -------------------------
# Initialize LLM (Groq)
# -------------------------
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq:")

llm = init_chat_model("llama-3.1-8b-instant", model_provider="groq")

# -------------------------
# Structured output for emails
# -------------------------
email_schema = [
    ResponseSchema(name="subject", description="Email subject line"),
    ResponseSchema(name="body", description="Email message body"),
]

email_parser = StructuredOutputParser.from_response_schemas(email_schema)

# -------------------------
# CRM Utilities
# -------------------------
def check_lead_local(email: str) -> Dict:
    """
    Check if email exists locally without sending PII to LLM.
    Returns dict: {exists: bool, lead: dict or None}
    """
    if not CRM_PATH.exists():
        return {"exists": False, "lead": None}

    with open(CRM_PATH, "r") as f:
        data = json.load(f)

    result = [lead for lead in data if lead.get("email") == email]

    if result:
        return {"exists": True, "lead": result[0]}
    return {"exists": False, "lead": None}


def add_new_lead(name: str, email: str, company: str = "N/A") -> Dict:
    """
    Add new lead to CRM JSON file.
    """
    now = datetime.now().isoformat()
    new_id = 1
    if CRM_PATH.exists():
        with open(CRM_PATH) as f:
            data = json.load(f)
            if data:
                new_id = max([lead["id"] for lead in data]) + 1
    else:
        data = []

    lead = {
        "id": new_id,
        "name": name,
        "email": email,
        "company": company,
        "type": "new_lead",
        "status": "New Lead",
        "created_at": now,
        "last_contact": now
    }
    data.append(lead)

    with open(CRM_PATH, "w") as f:
        json.dump(data, f, indent=2)

    return lead

# -------------------------
# Tool: Send Email
# -------------------------
def send_email_tool(params: Dict) -> str:
    """
    Tool that sends email.
    params = {
        "to_email": str,
        "subject": str,
        "body": str
    }
    """
    # For demo purposes, we'll just print the email
    print("\n--- Sending Email ---")
    print(f"To: {params['to_email']}")
    print(f"Subject: {params['subject']}")
    print(f"Body: {params['body']}")
    print("--- Email Sent ---\n")
    return "Email sent successfully."

# Define the tool
tools = [
    Tool(
        name="SendEmail",
        func=send_email_tool,
        description="Sends email to user. Parameters: to_email, subject, body"
    )
]

# -------------------------
# Agent logic
# -------------------------
def prepare_email_agent(user_input: Dict):
    """
    user_input = {
        "name": str,
        "email": str,
        "company": str,
        "subject": str,
        "message": str
    }
    """
    print(f"🚀 AI AGENT STARTED - Processing: {user_input['name']} ({user_input['email']})")
    
    # Step 1: Check if lead exists locally
    lead_status = check_lead_local(user_input["email"])
    is_existing = lead_status["exists"]
    print(f"📊 Lead Status: {'Existing' if is_existing else 'New Lead'}")

    # Step 2: Prepare prompt for LLM (without exposing PII)
    if is_existing:
        prompt_text = (
            "Generate a comprehensive, engaging acknowledgment email to an existing customer. "
            "Make it 3-4 paragraphs long with: "
            "1) Warm greeting and appreciation for their continued trust "
            "2) Acknowledge their specific inquiry with personalized details "
            "3) Provide valuable insights or next steps "
            "4) Professional closing with clear call-to-action. "
            "Use an enthusiastic, professional tone with specific details about Thryvix AI's capabilities."
        )
    else:
        prompt_text = (
            "Generate an exciting, detailed welcome email for a new lead. "
            "Make it 4-5 paragraphs long with: "
            "1) Enthusiastic welcome and excitement about their interest "
            "2) Introduction to Thryvix AI's revolutionary capabilities and benefits "
            "3) Specific value propositions and how we can help their business "
            "4) Next steps and what to expect "
            "5) Professional closing with clear call-to-action. "
            "Use an engaging, professional tone that builds excitement and trust."
        )

    # Use structured parser
    formatted_prompt = f"{prompt_text}\n\nRespond using JSON format:\n{email_parser.get_format_instructions()}"

    # LLM call
    print("🤖 CALLING LLM FOR EMAIL GENERATION...")
    llm_response = llm.invoke([{"role": "user", "content": formatted_prompt}])
    email_content = email_parser.parse(llm_response.text())
    
    print("📧 GENERATED EMAIL CONTENT:")
    print("="*60)
    print(f"Subject: {email_content['subject']}")
    print(f"Body:\n{email_content['body']}")
    print("="*60)

    # Step 3: Send email via tool
    send_email_tool({
        "to_email": user_input["email"],
        "subject": email_content["subject"],
        "body": email_content["body"]
    })

    # Step 4: If new lead, add to CRM
    if not is_existing:
        add_new_lead(user_input["name"], user_input["email"], user_input.get("company", "N/A"))

    result = {
        "lead_exists": is_existing,
        "email_subject": email_content["subject"],
        "email_body": email_content["body"]
    }
    
    print(f"✅ AI AGENT COMPLETED - Result: {json.dumps(result, indent=2)}")
    return result

# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    test_input = {
        "name": "YALLAIAH ONTERU",
        "email": "Onteruyallaiah970@gmail.com",
        "company": "N/A",
        "subject": "General Inquiry",
        "message": "hfjdttyd",
        "tag": "contact, submission, form, inquiry"
    }

    result = prepare_email_agent(test_input)
    print("Agent Result:\n", json.dumps(result, indent=2))
