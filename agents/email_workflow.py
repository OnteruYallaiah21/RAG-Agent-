"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Email Processing Workflow with Multiple Agents
Handles complete email processing pipeline from inbound email to response.

Main Use:
---------
Complete email workflow that:
1. Parses email content and extracts intent
2. Validates against CRM/database
3. Generates appropriate reply using LLM
4. Logs to appropriate data folder (new/existing leads)
5. Sends email response
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from agents.llm_manager import llm_manager
from utils.logger import logger

@dataclass
class EmailPayload:
    """Email payload structure"""
    from_email: str
    name: str
    subject: str
    email_content: str

@dataclass
class ValidationResult:
    """Validation result from CRM check"""
    validated: bool
    user_id: Optional[int] = None
    customer_type: Optional[str] = None
    is_new_lead: bool = True

@dataclass
class ReplyResult:
    """Generated reply result"""
    subject: str
    body: str
    intent: str

class ParserAgent:
    """Agent for parsing email content and extracting intent"""
    
    def __init__(self):
        self.intent_keywords = {
            "sales": ["demo", "pricing", "buy", "purchase", "cost", "price", "interested", "product"],
            "support": ["help", "issue", "problem", "bug", "error", "not working", "support"],
            "partnership": ["partnership", "collaborate", "partner", "business", "deal"],
            "general": ["hello", "hi", "information", "question", "inquiry"]
        }
    
    async def parse_email(self, email_payload: EmailPayload) -> Dict[str, Any]:
        """Parse email and extract intent"""
        try:
            # Use LLM to extract intent
            intent_prompt = f"""
            Analyze this email and determine the primary intent:
            
            From: {email_payload.name} ({email_payload.from_email})
            Subject: {email_payload.subject}
            Content: {email_payload.email_content}
            
            Classify the intent as one of: sales, support, partnership, general
            Also extract any specific requests or key information.
            
            Return JSON format:
            {{
                "intent": "sales|support|partnership|general",
                "confidence": 0.0-1.0,
                "key_requests": ["list of specific requests"],
                "urgency": "low|medium|high"
            }}
            """
            
            result = await llm_manager.generate_text(
                prompt=intent_prompt,
                system_prompt="You are an expert email parser. Extract intent and key information accurately."
            )
            
            if result["success"]:
                # Parse the JSON response
                try:
                    parsed_result = json.loads(result["response"])
                    return {
                        "intent": parsed_result.get("intent", "general"),
                        "confidence": parsed_result.get("confidence", 0.5),
                        "key_requests": parsed_result.get("key_requests", []),
                        "urgency": parsed_result.get("urgency", "low"),
                        "parsed_successfully": True
                    }
                except json.JSONDecodeError:
                    # Fallback to keyword-based parsing
                    return self._fallback_intent_parsing(email_payload)
            else:
                return self._fallback_intent_parsing(email_payload)
                
        except Exception as e:
            logger.error(f"Error in ParserAgent: {e}")
            return self._fallback_intent_parsing(email_payload)
    
    def _fallback_intent_parsing(self, email_payload: EmailPayload) -> Dict[str, Any]:
        """Fallback keyword-based intent parsing"""
        content_lower = (email_payload.subject + " " + email_payload.email_content).lower()
        
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return {
                    "intent": intent,
                    "confidence": 0.6,
                    "key_requests": [],
                    "urgency": "medium",
                    "parsed_successfully": True
                }
        
        return {
            "intent": "general",
            "confidence": 0.3,
            "key_requests": [],
            "urgency": "low",
            "parsed_successfully": True
        }

class ValidationAgent:
    """Agent for validating email against CRM/database"""
    
    def __init__(self):
        self.crm_file = "data/crm/customers.json"
        self._ensure_crm_file()
    
    def _ensure_crm_file(self):
        """Ensure CRM file exists"""
        os.makedirs(os.path.dirname(self.crm_file), exist_ok=True)
        if not os.path.exists(self.crm_file):
            with open(self.crm_file, 'w') as f:
                json.dump([], f)
    
    async def validate_email(self, email_payload: EmailPayload) -> ValidationResult:
        """Validate email against CRM database"""
        try:
            # Load existing customers
            with open(self.crm_file, 'r') as f:
                customers = json.load(f)
            
            # Check if email exists
            for customer in customers:
                if customer.get("email", "").lower() == email_payload.from_email.lower():
                    return ValidationResult(
                        validated=True,
                        user_id=customer.get("id"),
                        customer_type=customer.get("type", "existing"),
                        is_new_lead=False
                    )
            
            # New lead - add to CRM
            new_customer_id = len(customers) + 1
            new_customer = {
                "id": new_customer_id,
                "name": email_payload.name,
                "email": email_payload.from_email,
                "type": "new_lead",
                "status": "New Lead",
                "account_id": None,
                "created_at": datetime.now().isoformat(),
                "last_contact": datetime.now().isoformat()
            }
            
            customers.append(new_customer)
            
            # Save updated CRM
            with open(self.crm_file, 'w') as f:
                json.dump(customers, f, indent=2)
            
            return ValidationResult(
                validated=True,
                user_id=new_customer_id,
                customer_type="lead",
                is_new_lead=True
            )
            
        except Exception as e:
            logger.error(f"Error in ValidationAgent: {e}")
            return ValidationResult(validated=False)

class ReplyGeneratorAgent:
    """Agent for generating email replies using LLM"""
    
    async def generate_reply(self, email_payload: EmailPayload, intent: str, customer_type: str, is_new_lead: bool) -> ReplyResult:
        """Generate appropriate reply based on intent and customer type"""
        try:
            # Different prompts for existing vs new customers
            if is_new_lead:
                # Special personalized email for new customers
                reply_prompt = f"""
                Generate a WARM, PERSONALIZED email reply for a NEW CUSTOMER:
                
                Customer: {email_payload.name} ({email_payload.from_email})
                Subject: {email_payload.subject}
                Intent: {intent}
                Original Message: {email_payload.email_content}
                
                IMPORTANT: This is a NEW CUSTOMER. Make them feel VERY IMPORTANT and SPECIAL.
                Use language like "You are very important to us" and "We're thrilled by your interest".
                Make them feel valued and excited about working with Thryvix AI.
                
                Generate a reply that:
                1. Makes them feel important and valued
                2. Uses warm, engaging language
                3. Shows excitement about their interest
                4. Offers personalized service
                5. Includes special welcome message
                
                Return JSON format:
                {{
                    "subject": "Welcome to Thryvix AI – You Are Very Important to Us!",
                    "body": "Warm, personalized reply making them feel special",
                    "intent": "{intent}",
                    "next_steps": ["list of next steps"]
                }}
                """
            else:
                # Normal acknowledgment for existing customers
                reply_prompt = f"""
                Generate a professional email reply for an EXISTING CUSTOMER:
                
                Customer: {email_payload.name} ({email_payload.from_email})
                Subject: {email_payload.subject}
                Intent: {intent}
                Original Message: {email_payload.email_content}
                
                This is an EXISTING CUSTOMER. Provide a professional, helpful acknowledgment.
                
                Generate a reply that:
                1. Acknowledges their request professionally
                2. Is helpful and informative
                3. Includes appropriate next steps
                4. Matches the intent (sales, support, partnership, general)
                
                Return JSON format:
                {{
                    "subject": "Re: {email_payload.subject}",
                    "body": "Professional acknowledgment reply",
                    "intent": "{intent}",
                    "next_steps": ["list of next steps"]
                }}
                """
            
            result = await llm_manager.generate_text(
                prompt=reply_prompt,
                system_prompt="You are a professional email assistant. Generate helpful, contextually appropriate replies."
            )
            
            if result["success"]:
                try:
                    parsed_reply = json.loads(result["response"])
                    return ReplyResult(
                        subject=parsed_reply.get("subject", f"Re: {email_payload.subject}"),
                        body=parsed_reply.get("body", "Thank you for your email. We'll get back to you soon."),
                        intent=intent
                    )
                except json.JSONDecodeError:
                    return self._fallback_reply(email_payload, intent, is_new_lead)
            else:
                return self._fallback_reply(email_payload, intent, is_new_lead)
                
        except Exception as e:
            logger.error(f"Error in ReplyGeneratorAgent: {e}")
            return self._fallback_reply(email_payload, intent, is_new_lead)
    
    def _fallback_reply(self, email_payload: EmailPayload, intent: str, is_new_lead: bool) -> ReplyResult:
        """Fallback reply generation"""
        if is_new_lead:
            # Special personalized email for new customers
            return ReplyResult(
                subject="Welcome to Thryvix AI – You Are Very Important to Us!",
                body=f"Hi {email_payload.name},\n\nWe are absolutely thrilled by your interest in Thryvix AI! You are very important to us, and we want to make sure your experience with our products is exceptional.\n\nOur team is excited to work with you and will reach out shortly to provide you with a personalized introduction to our services. We're committed to making you feel valued and ensuring your success.\n\nThank you for choosing Thryvix AI!\n\nWarm regards,\nThe Thryvix AI Team",
                intent=intent
            )
        else:
            # Normal acknowledgment for existing customers
            if intent == "sales":
                return ReplyResult(
                    subject=f"Re: {email_payload.subject}",
                    body=f"Hi {email_payload.name},\n\nThank you for your interest! Our team will contact you shortly to discuss your requirements.\n\nBest regards,\nThryvix AI Team",
                    intent=intent
                )
            elif intent == "support":
                return ReplyResult(
                    subject=f"Re: {email_payload.subject}",
                    body=f"Hi {email_payload.name},\n\nThank you for reaching out. We've received your support request and will get back to you within 24 hours.\n\nBest regards,\nThryvix AI Support Team",
                    intent=intent
                )
            else:
                return ReplyResult(
                    subject=f"Re: {email_payload.subject}",
                    body=f"Hi {email_payload.name},\n\nThank you for your email. We'll review your message and get back to you soon.\n\nBest regards,\nThryvix AI Team",
                    intent=intent
                )

class LoggingAgent:
    """Agent for logging email interactions"""
    
    def __init__(self):
        self.new_leads_dir = "data/new_leads"
        self.existing_leads_dir = "data/existing_leads"
        os.makedirs(self.new_leads_dir, exist_ok=True)
        os.makedirs(self.existing_leads_dir, exist_ok=True)
    
    async def log_interaction(self, 
                            email_payload: EmailPayload, 
                            validation_result: ValidationResult,
                            reply_result: ReplyResult,
                            intent: str) -> str:
        """Log email interaction to appropriate folder"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{email_payload.from_email.replace('@', '_at_')}.json"
            
            # Determine folder based on whether it's a new lead
            folder = self.new_leads_dir if validation_result.is_new_lead else self.existing_leads_dir
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "email": {
                    "from": email_payload.from_email,
                    "name": email_payload.name,
                    "subject": email_payload.subject,
                    "content": email_payload.email_content
                },
                "validation": {
                    "validated": validation_result.validated,
                    "user_id": validation_result.user_id,
                    "customer_type": validation_result.customer_type,
                    "is_new_lead": validation_result.is_new_lead
                },
                "reply": {
                    "subject": reply_result.subject,
                    "body": reply_result.body,
                    "intent": reply_result.intent
                },
                "processing": {
                    "intent": intent,
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            filepath = os.path.join(folder, filename)
            with open(filepath, 'w') as f:
                json.dump(log_entry, f, indent=2)
            
            logger.info(f"Logged interaction to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error in LoggingAgent: {e}")
            return ""

class EmailWorkflow:
    """Main email processing workflow"""
    
    def __init__(self):
        self.parser_agent = ParserAgent()
        self.validation_agent = ValidationAgent()
        self.reply_generator = ReplyGeneratorAgent()
        self.logging_agent = LoggingAgent()
    
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process complete email workflow"""
        try:
            # Extract email payload
            email_payload = EmailPayload(
                from_email=email_data["email"]["from"],
                name=email_data["email"]["name"],
                subject=email_data["email"]["subject"],
                email_content=email_data["email"]["Email_Content"]
            )
            
            logger.info(f"Processing email from {email_payload.name} ({email_payload.from_email})")
            
            # Step 1: Parse email and extract intent
            parse_result = await self.parser_agent.parse_email(email_payload)
            intent = parse_result["intent"]
            
            # Step 2: Validate against CRM
            validation_result = await self.validation_agent.validate_email(email_payload)
            
            # Step 3: Generate reply
            reply_result = await self.reply_generator.generate_reply(
                email_payload, intent, validation_result.customer_type or "unknown", validation_result.is_new_lead
            )
            
            # Step 4: Log interaction
            log_file = await self.logging_agent.log_interaction(
                email_payload, validation_result, reply_result, intent
            )
            
            # Step 5: Return final response
            return {
                "status": "processed",
                "to": email_payload.from_email,
                "reply_subject": reply_result.subject,
                "reply_body": reply_result.body,
                "intent": intent,
                "customer_type": validation_result.customer_type,
                "is_new_lead": validation_result.is_new_lead,
                "user_id": validation_result.user_id,
                "log_file": log_file,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in email workflow: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

# Global workflow instance
email_workflow = EmailWorkflow()
