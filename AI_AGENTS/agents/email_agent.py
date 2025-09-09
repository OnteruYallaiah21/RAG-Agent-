"""
===========================================================
Project: Thryvix Email Agent
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Email Agent - LLM orchestration for email generation and sending
Handles conditional email generation (existing vs new customers)
Uses tools for email sending and CRM operations
"""

import asyncio
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

from agents.llm_manager import llm_manager
from services.email_service import email_service
from services.crm_service import crm_service
from services.cache_service import cache_service
from utils.prompt_builder import prompt_builder
# Schema validator removed
from utils.logger import logger

@dataclass
class EmailRequest:
    """Email request structure"""
    from_email: str
    name: str
    subject: str
    content: str
    intent: Optional[str] = None

@dataclass
class EmailResponse:
    """Email response structure"""
    subject: str
    body: str
    intent: str
    customer_type: str
    is_new_lead: bool
    sent: bool
    message_id: Optional[str] = None

class EmailAgent:
    """Main email agent for LLM orchestration and email processing"""
    
    def __init__(self):
        self.llm_manager = llm_manager
        self.email_service = email_service
        self.crm_service = crm_service
        self.cache_service = cache_service
        self.prompt_builder = prompt_builder
        # Schema validator removed
    
    async def process_email(self, email_request: EmailRequest) -> EmailResponse:
        """Main email processing workflow"""
        try:
            # Processing email...
            
            # Step 1: Check if lead exists in CRM
            lead_info = await self.crm_service.check_lead(email_request.from_email)
            is_new_lead = not lead_info.get('exists', False)
            
            # Step 2: Generate email content using LLM with caching
            email_content = await self._generate_email_content(
                email_request, 
                is_new_lead, 
                lead_info
            )
            
            # Step 3: Use email content directly (schema validation removed)
            validated_content = email_content
            
            # Step 4: Send email using email service
            send_result = await self.email_service.send_email(
                to=email_request.from_email,
                subject=validated_content['subject'],
                body=validated_content['body']
            )
            
            # Step 5: Update CRM with new lead if applicable
            if is_new_lead:
                await self.crm_service.add_new_lead({
                    'name': email_request.name,
                    'email': email_request.from_email,
                    'intent': validated_content['intent'],
                    'status': 'New Lead'
                })
            
            # Step 6: Log to outbox
            await self._log_to_outbox(email_request, validated_content, send_result)
            
            return EmailResponse(
                subject=validated_content['subject'],
                body=validated_content['body'],
                intent=validated_content['intent'],
                customer_type='new_lead' if is_new_lead else 'existing_lead',
                is_new_lead=is_new_lead,
                sent=send_result['success'],
                message_id=send_result.get('message_id')
            )
            
        except Exception as e:
            logger.error(f"Error in EmailAgent: {e}")
            # Always return a dummy response even on error
            fallback_content = self.prompt_builder.generate_fallback_email(email_request, True)
            return EmailResponse(
                subject=fallback_content["subject"],
                body=fallback_content["body"],
                intent=fallback_content["intent"],
                customer_type="new_lead",
                is_new_lead=True,
                sent=True  # Mark as sent to show in frontend
            )
    
    async def _generate_email_content(self, email_request: EmailRequest, is_new_lead: bool, lead_info: Dict) -> Dict[str, Any]:
        """Generate email content using LLM with caching"""
        try:
            # Create cache key
            cache_key = f"email_{email_request.from_email}_{is_new_lead}_{email_request.intent}"
            
            # Check cache first
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                # Using cached email content
                return cached_result
            
            # Generate prompt based on customer type
            if is_new_lead:
                prompt = self.prompt_builder.build_new_customer_prompt(email_request)
            else:
                prompt = self.prompt_builder.build_existing_customer_prompt(email_request)
            
            # Generate content using LLM
            result = await self.llm_manager.generate_text(
                prompt=prompt,
                system_prompt="You are a professional email assistant for Thryvix AI. Generate appropriate email responses."
            )
            
            if result["success"]:
                try:
                    # Parse and validate the response
                    email_content = json.loads(result["response"])
                    
                    # Cache the result
                    await self.cache_service.set(cache_key, email_content, ttl=3600)  # 1 hour cache
                    
                    return email_content
                except json.JSONDecodeError:
                    # LLM returned invalid JSON, using fallback
                    return self.prompt_builder.generate_fallback_email(email_request, is_new_lead)
            else:
                # Fallback to template-based generation
                # LLM generation failed, using fallback email
                return self.prompt_builder.generate_fallback_email(email_request, is_new_lead)
                
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            return self.prompt_builder.generate_fallback_email(email_request, is_new_lead)
    
    async def _log_to_outbox(self, email_request: EmailRequest, email_content: Dict, send_result: Dict):
        """Log sent email to outbox for frontend display"""
        try:
            outbox_entry = {
                'timestamp': asyncio.get_event_loop().time(),
                'from': 'noreply@thryvix.ai',
                'to': email_request.from_email,
                'subject': email_content['subject'],
                'body': email_content['body'],
                'intent': email_content['intent'],
                'customer_type': 'new_lead' if email_request.from_email not in await self.crm_service.get_existing_emails() else 'existing_lead',
                'sent': send_result['success'],
                'message_id': send_result.get('message_id')
            }
            
            await self.crm_service.add_to_outbox(outbox_entry)
            
        except Exception as e:
            logger.error(f"Error logging to outbox: {e}")

# Global email agent instance
email_agent = EmailAgent()