"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
AI Email Agent
Handles email processing, name extraction, and response generation.

Main Use:
---------
Core AI agent that:
1. Extracts sender name from email content using AI
2. Generates intelligent email responses
3. Processes complete email workflows
4. Integrates with multiple AI providers
"""

import openai
from typing import Dict, Optional
from config.settings import settings

class EmailAgent:
    """AI-powered email processing agent."""
    
    def __init__(self):
        """Initialize the email agent with OpenAI client."""
        # =============== start __init__ ======
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def extract_sender_name(self, email_content: str) -> Optional[str]:
        """
        Extract sender name from email content using AI.
        
        Args:
            email_content: Raw email content
            
        Returns:
            Extracted sender name or None if extraction fails
        """
        # =============== start extract_sender_name ======
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract the sender's name from this email. Return only the name, nothing else."},
                    {"role": "user", "content": email_content}
                ],
                max_tokens=50
            )
            
            name = response.choices[0].message.content.strip()
            return name if name else None
            
        except Exception as e:
            print(f"Error extracting sender name: {e}")
            return None
    
    def generate_reply(self, sender_name: str, email_content: str) -> str:
        """
        Generate an AI-powered reply to the email.
        
        Args:
            sender_name: Name of the sender
            email_content: Original email content
            
        Returns:
            Generated reply text
        """
        # =============== start generate_reply ======
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Generate a professional, friendly reply to {sender_name}. Keep it concise and appropriate."},
                    {"role": "user", "content": email_content}
                ],
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return f"Thank you for your email, {sender_name}. I'll get back to you soon."
    
    def process_email(self, email_content: str) -> Dict[str, str]:
        """
        Complete email processing workflow.
        
        Args:
            email_content: Raw email content
            
        Returns:
            Dictionary containing extracted name and generated reply
        """
        # =============== start process_email ======
        sender_name = self.extract_sender_name(email_content)
        reply = self.generate_reply(sender_name or "there", email_content)
        
        return {
            "sender_name": sender_name,
            "reply": reply
        }
