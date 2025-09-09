"""
===========================================================
Project: Thryvix Email Agent
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Prompt Builder - Centralized prompt templates & structured outputs
Handles prompt engineering for different customer types and intents
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from utils.logger import logger

@dataclass
class EmailRequest:
    """Email request structure for prompt building"""
    from_email: str
    name: str
    subject: str
    content: str
    intent: Optional[str] = None

class PromptBuilder:
    """Builder for creating structured prompts for LLM"""
    
    def __init__(self):
        self.company_name = "Thryvix AI"
        self.company_email = "noreply@thryvix.ai"
        self.company_website = "https://thryvix.ai"
    
    def build_new_customer_prompt(self, email_request: EmailRequest) -> str:
        """Build prompt for new customer email generation"""
        try:
            prompt = f"""
            Generate a WARM, PERSONALIZED email reply for a NEW CUSTOMER:
            
            Customer Details:
            - Name: {email_request.name}
            - Email: {email_request.from_email}
            - Subject: {email_request.subject}
            - Intent: {email_request.intent or 'general'}
            - Original Message: {email_request.content}
            
            IMPORTANT REQUIREMENTS:
            1. This is a NEW CUSTOMER - make them feel VERY IMPORTANT and SPECIAL
            2. Use warm, engaging language that makes them feel valued
            3. Include phrases like "You are very important to us" and "We're thrilled by your interest"
            4. Show excitement about their interest in {self.company_name}
            5. Offer personalized service and attention
            6. Make them feel like they're getting VIP treatment
            7. Use a welcoming, enthusiastic tone throughout
            
            Generate a reply that:
            - Makes them feel important and valued
            - Uses warm, engaging language
            - Shows excitement about their interest
            - Offers personalized service
            - Includes special welcome message
            - Addresses their specific request appropriately
            
            Return JSON format:
            {{
                "subject": "Welcome to {self.company_name} – You Are Very Important to Us!",
                "body": "Warm, personalized reply making them feel special",
                "intent": "{email_request.intent or 'general'}",
                "tone": "warm_personalized",
                "next_steps": ["list of next steps"],
                "personalization_level": "high"
            }}
            """
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error building new customer prompt: {e}")
            return self._get_fallback_prompt(email_request, is_new_customer=True)
    
    def build_existing_customer_prompt(self, email_request: EmailRequest) -> str:
        """Build prompt for existing customer email generation"""
        try:
            prompt = f"""
            Generate a PROFESSIONAL email reply for an EXISTING CUSTOMER:
            
            Customer Details:
            - Name: {email_request.name}
            - Email: {email_request.from_email}
            - Subject: {email_request.subject}
            - Intent: {email_request.intent or 'general'}
            - Original Message: {email_request.content}
            
            IMPORTANT REQUIREMENTS:
            1. This is an EXISTING CUSTOMER - provide professional, helpful acknowledgment
            2. Use professional, courteous language
            3. Address their specific request directly
            4. Provide helpful information and next steps
            5. Maintain a professional but friendly tone
            6. Show appreciation for their continued business
            
            Generate a reply that:
            - Acknowledges their request professionally
            - Is helpful and informative
            - Includes appropriate next steps
            - Matches the intent (sales, support, partnership, general)
            - Shows appreciation for their business
            
            Return JSON format:
            {{
                "subject": "Re: {email_request.subject}",
                "body": "Professional acknowledgment reply",
                "intent": "{email_request.intent or 'general'}",
                "tone": "professional",
                "next_steps": ["list of next steps"],
                "personalization_level": "medium"
            }}
            """
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error building existing customer prompt: {e}")
            return self._get_fallback_prompt(email_request, is_new_customer=False)
    
    def build_intent_analysis_prompt(self, email_content: str, subject: str) -> str:
        """Build prompt for intent analysis"""
        try:
            prompt = f"""
            Analyze this email and determine the primary intent:
            
            Subject: {subject}
            Content: {email_content}
            
            Classify the intent as one of: sales, support, partnership, general
            
            Consider these factors:
            - Keywords and phrases used
            - Tone and urgency
            - Specific requests made
            - Business context
            
            Return JSON format:
            {{
                "intent": "sales|support|partnership|general",
                "confidence": 0.0-1.0,
                "key_requests": ["list of specific requests"],
                "urgency": "low|medium|high",
                "sentiment": "positive|neutral|negative",
                "business_impact": "low|medium|high"
            }}
            """
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error building intent analysis prompt: {e}")
            return self._get_fallback_intent_prompt(email_content, subject)
    
    def build_lead_qualification_prompt(self, lead_data: Dict[str, Any]) -> str:
        """Build prompt for lead qualification"""
        try:
            prompt = f"""
            Qualify this lead based on the provided information:
            
            Lead Data:
            - Name: {lead_data.get('name', 'Unknown')}
            - Email: {lead_data.get('email', 'Unknown')}
            - Intent: {lead_data.get('intent', 'general')}
            - Company: {lead_data.get('company', 'Unknown')}
            - Message: {lead_data.get('message', 'No message')}
            
            Evaluate the lead on:
            - Lead quality (high/medium/low)
            - Potential value
            - Urgency level
            - Recommended next steps
            - Sales team assignment
            
            Return JSON format:
            {{
                "lead_quality": "high|medium|low",
                "potential_value": "high|medium|low",
                "urgency": "high|medium|low",
                "recommended_actions": ["list of recommended actions"],
                "sales_team": "enterprise|midmarket|small_business",
                "follow_up_timeline": "immediate|within_24h|within_week",
                "notes": "Additional qualification notes"
            }}
            """
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error building lead qualification prompt: {e}")
            return self._get_fallback_qualification_prompt(lead_data)
    
    def generate_fallback_email(self, email_request: EmailRequest, is_new_customer: bool) -> Dict[str, Any]:
        """Generate fallback email when LLM fails"""
        try:
            if is_new_customer:
                return {
                    "subject": f"Welcome to {self.company_name} – You Are Very Important to Us!",
                    "body": f"""Hi {email_request.name},

We are absolutely thrilled by your interest in {self.company_name}! You are very important to us, and we want to make sure your experience with our products is exceptional.

Our team is excited to work with you and will reach out shortly to provide you with a personalized introduction to our services. We're committed to making you feel valued and ensuring your success.

Thank you for choosing {self.company_name}!

Warm regards,
The {self.company_name} Team""",
                    "intent": email_request.intent or "general",
                    "tone": "warm_personalized",
                    "next_steps": ["Personalized consultation", "Product demonstration", "Follow-up call"],
                    "personalization_level": "high"
                }
            else:
                return {
                    "subject": f"Re: {email_request.subject}",
                    "body": f"""Hi {email_request.name},

Thank you for reaching out to {self.company_name}. We've received your message and appreciate your continued business.

Our team will review your request and get back to you within 24 hours with a detailed response.

If you have any urgent questions, please don't hesitate to contact us directly.

Best regards,
The {self.company_name} Team""",
                    "intent": email_request.intent or "general",
                    "tone": "professional",
                    "next_steps": ["Review request", "Prepare response", "Follow-up"],
                    "personalization_level": "medium"
                }
                
        except Exception as e:
            logger.error(f"Error generating fallback email: {e}")
            return {
                "subject": "Thank you for contacting us",
                "body": "Thank you for your message. We'll get back to you soon.",
                "intent": "general",
                "tone": "professional",
                "next_steps": ["Review message", "Prepare response"],
                "personalization_level": "low"
            }
    
    def _get_fallback_prompt(self, email_request: EmailRequest, is_new_customer: bool) -> str:
        """Get fallback prompt when main prompt building fails"""
        if is_new_customer:
            return f"Generate a warm, personalized email for new customer {email_request.name} about {email_request.subject}"
        else:
            return f"Generate a professional email for existing customer {email_request.name} about {email_request.subject}"
    
    def _get_fallback_intent_prompt(self, email_content: str, subject: str) -> str:
        """Get fallback intent analysis prompt"""
        return f"Analyze the intent of this email: Subject: {subject}, Content: {email_content}"
    
    def _get_fallback_qualification_prompt(self, lead_data: Dict[str, Any]) -> str:
        """Get fallback lead qualification prompt"""
        return f"Qualify this lead: {lead_data.get('name', 'Unknown')} - {lead_data.get('email', 'Unknown')}"

# Global prompt builder instance
prompt_builder = PromptBuilder()
