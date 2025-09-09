"""
===========================================================
Project: Thryvix Email Agent
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Validation Agent - Checks if lead exists, determines lead type
Handles CRM operations and lead validation
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from services.crm_service import crm_service
from utils.logger import logger

@dataclass
class ValidationResult:
    """Validation result structure"""
    exists: bool
    lead_id: Optional[str] = None
    lead_type: Optional[str] = None
    status: Optional[str] = None
    account_id: Optional[str] = None
    last_contact: Optional[str] = None
    confidence: float = 0.0

class ValidationAgent:
    """Agent for validating leads and determining customer type"""
    
    def __init__(self):
        self.crm_service = crm_service
    
    async def validate_lead(self, email: str, name: Optional[str] = None) -> ValidationResult:
        """Validate if lead exists in CRM and determine type"""
        try:
            logger.info(f"Validating lead: {email}")
            
            # Check existing leads
            existing_leads = await self.crm_service.get_existing_leads()
            email_lower = email.lower()
            
            for lead in existing_leads:
                if lead.get('email', '').lower() == email_lower:
                    return ValidationResult(
                        exists=True,
                        lead_id=lead.get('id'),
                        lead_type='existing_lead',
                        status=lead.get('status', 'Existing Lead'),
                        account_id=lead.get('account_id'),
                        last_contact=lead.get('last_contact'),
                        confidence=1.0
                    )
            
            # Check new leads
            new_leads = await self.crm_service.get_new_leads()
            for lead in new_leads:
                if lead.get('email', '').lower() == email_lower:
                    return ValidationResult(
                        exists=True,
                        lead_id=lead.get('id'),
                        lead_type='new_lead',
                        status=lead.get('status', 'New Lead'),
                        account_id=lead.get('account_id'),
                        last_contact=lead.get('last_contact'),
                        confidence=0.9
                    )
            
            # Lead doesn't exist
            return ValidationResult(
                exists=False,
                lead_type='new_lead',
                status='New Lead',
                confidence=1.0
            )
            
        except Exception as e:
            logger.error(f"Error in ValidationAgent: {e}")
            return ValidationResult(
                exists=False,
                lead_type='new_lead',
                status='New Lead',
                confidence=0.0
            )
    
    async def determine_intent(self, email_content: str, subject: str) -> str:
        """Determine email intent using keyword analysis"""
        try:
            content_lower = (subject + " " + email_content).lower()
            
            # Intent keywords
            intent_keywords = {
                'sales': ['demo', 'pricing', 'buy', 'purchase', 'cost', 'price', 'interested', 'product', 'quote'],
                'support': ['help', 'issue', 'problem', 'bug', 'error', 'not working', 'support', 'assistance'],
                'partnership': ['partnership', 'collaborate', 'partner', 'business', 'deal', 'collaboration'],
                'general': ['hello', 'hi', 'information', 'question', 'inquiry', 'contact']
            }
            
            # Score each intent
            intent_scores = {}
            for intent, keywords in intent_keywords.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                intent_scores[intent] = score
            
            # Return highest scoring intent
            if intent_scores:
                best_intent = max(intent_scores, key=intent_scores.get)
                return best_intent if intent_scores[best_intent] > 0 else 'general'
            
            return 'general'
            
        except Exception as e:
            logger.error(f"Error determining intent: {e}")
            return 'general'
    
    async def get_lead_history(self, email: str) -> List[Dict[str, Any]]:
        """Get lead interaction history"""
        try:
            # Get from outbox
            outbox_entries = await self.crm_service.get_outbox()
            lead_history = []
            
            for entry in outbox_entries:
                if entry.get('to', '').lower() == email.lower():
                    lead_history.append({
                        'timestamp': entry.get('timestamp'),
                        'subject': entry.get('subject'),
                        'intent': entry.get('intent'),
                        'sent': entry.get('sent', False)
                    })
            
            # Sort by timestamp (newest first)
            lead_history.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            return lead_history[:10]  # Return last 10 interactions
            
        except Exception as e:
            logger.error(f"Error getting lead history: {e}")
            return []
    
    async def update_lead_status(self, email: str, new_status: str) -> bool:
        """Update lead status in CRM"""
        try:
            # Update in existing leads
            existing_leads = await self.crm_service.get_existing_leads()
            for lead in existing_leads:
                if lead.get('email', '').lower() == email.lower():
                    lead['status'] = new_status
                    lead['last_contact'] = asyncio.get_event_loop().time()
                    await self.crm_service.save_existing_leads(existing_leads)
                    return True
            
            # Update in new leads
            new_leads = await self.crm_service.get_new_leads()
            for lead in new_leads:
                if lead.get('email', '').lower() == email.lower():
                    lead['status'] = new_status
                    lead['last_contact'] = asyncio.get_event_loop().time()
                    await self.crm_service.save_new_leads(new_leads)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating lead status: {e}")
            return False

# Global validation agent instance
validation_agent = ValidationAgent()
