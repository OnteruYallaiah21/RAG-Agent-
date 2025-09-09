"""
===========================================================
Project: Thryvix Email Agent
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
CRM Service - Handles existing/new leads table, async updates
Manages lead data and CRM operations
"""

import json
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.logger import logger

class CRMService:
    """Service for managing CRM data and lead operations"""
    
    def __init__(self):
        self.data_dir = "data"
        self.existing_leads_file = os.path.join(self.data_dir, "existing_leads.json")
        self.new_leads_file = os.path.join(self.data_dir, "new_leads.json")
        self.outbox_file = os.path.join(self.data_dir, "outbox.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        files_to_init = [
            (self.existing_leads_file, []),
            (self.new_leads_file, []),
            (self.outbox_file, [])
        ]
        
        for file_path, default_data in files_to_init:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
    
    async def get_existing_leads(self) -> List[Dict[str, Any]]:
        """Get all existing leads"""
        try:
            with open(self.existing_leads_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading existing leads: {e}")
            return []
    
    async def get_new_leads(self) -> List[Dict[str, Any]]:
        """Get all new leads"""
        try:
            with open(self.new_leads_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading new leads: {e}")
            return []
    
    async def get_all_leads(self) -> List[Dict[str, Any]]:
        """Get all leads (existing + new)"""
        try:
            existing_leads = await self.get_existing_leads()
            new_leads = await self.get_new_leads()
            return existing_leads + new_leads
        except Exception as e:
            logger.error(f"Error loading all leads: {e}")
            return []
    
    async def check_lead(self, email: str) -> Dict[str, Any]:
        """Check if lead exists and return lead info"""
        try:
            email_lower = email.lower()
            
            # Check existing leads
            existing_leads = await self.get_existing_leads()
            for lead in existing_leads:
                if lead.get('email', '').lower() == email_lower:
                    return {
                        'exists': True,
                        'lead_type': 'existing_lead',
                        'lead_data': lead
                    }
            
            # Check new leads
            new_leads = await self.get_new_leads()
            for lead in new_leads:
                if lead.get('email', '').lower() == email_lower:
                    return {
                        'exists': True,
                        'lead_type': 'new_lead',
                        'lead_data': lead
                    }
            
            return {'exists': False, 'lead_type': 'new_lead', 'lead_data': None}
            
        except Exception as e:
            logger.error(f"Error checking lead: {e}")
            return {'exists': False, 'lead_type': 'new_lead', 'lead_data': None}
    
    async def add_new_lead(self, lead_data: Dict[str, Any]) -> bool:
        """Add new lead to CRM"""
        try:
            new_leads = await self.get_new_leads()
            
            # Generate unique ID
            lead_id = f"lead_{int(asyncio.get_event_loop().time() * 1000)}"
            
            # Create lead entry
            lead_entry = {
                'id': lead_id,
                'name': lead_data.get('name', ''),
                'email': lead_data.get('email', ''),
                'intent': lead_data.get('intent', 'general'),
                'status': lead_data.get('status', 'New Lead'),
                'account_id': None,
                'created_at': datetime.now().isoformat(),
                'last_contact': datetime.now().isoformat()
            }
            
            new_leads.append(lead_entry)
            
            # Save to file
            await self.save_new_leads(new_leads)
            
            # Added new lead
            return True
            
        except Exception as e:
            logger.error(f"Error adding new lead: {e}")
            return False
    
    async def update_lead(self, email: str, update_data: Dict[str, Any]) -> bool:
        """Update existing lead"""
        try:
            email_lower = email.lower()
            updated = False
            
            # Update in existing leads
            existing_leads = await self.get_existing_leads()
            for lead in existing_leads:
                if lead.get('email', '').lower() == email_lower:
                    lead.update(update_data)
                    lead['last_contact'] = datetime.now().isoformat()
                    updated = True
                    break
            
            if updated:
                await self.save_existing_leads(existing_leads)
            else:
                # Update in new leads
                new_leads = await self.get_new_leads()
                for lead in new_leads:
                    if lead.get('email', '').lower() == email_lower:
                        lead.update(update_data)
                        lead['last_contact'] = datetime.now().isoformat()
                        updated = True
                        break
                
                if updated:
                    await self.save_new_leads(new_leads)
            
            return updated
            
        except Exception as e:
            logger.error(f"Error updating lead: {e}")
            return False
    
    async def promote_lead(self, email: str) -> bool:
        """Promote new lead to existing lead"""
        try:
            email_lower = email.lower()
            
            # Find in new leads
            new_leads = await self.get_new_leads()
            lead_to_promote = None
            
            for i, lead in enumerate(new_leads):
                if lead.get('email', '').lower() == email_lower:
                    lead_to_promote = new_leads.pop(i)
                    break
            
            if lead_to_promote:
                # Update lead data
                lead_to_promote['status'] = 'Existing Lead'
                lead_to_promote['account_id'] = f"AC{int(asyncio.get_event_loop().time())}"
                lead_to_promote['last_contact'] = datetime.now().isoformat()
                
                # Add to existing leads
                existing_leads = await self.get_existing_leads()
                existing_leads.append(lead_to_promote)
                
                # Save both files
                await self.save_existing_leads(existing_leads)
                await self.save_new_leads(new_leads)
                
                logger.info(f"Promoted lead to existing: {email}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error promoting lead: {e}")
            return False
    
    async def get_existing_emails(self) -> List[str]:
        """Get list of all existing lead emails"""
        try:
            existing_leads = await self.get_existing_leads()
            return [lead.get('email', '') for lead in existing_leads if lead.get('email')]
        except Exception as e:
            logger.error(f"Error getting existing emails: {e}")
            return []
    
    async def save_existing_leads(self, leads: List[Dict[str, Any]]) -> bool:
        """Save existing leads to file"""
        try:
            with open(self.existing_leads_file, 'w') as f:
                json.dump(leads, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving existing leads: {e}")
            return False
    
    async def save_new_leads(self, leads: List[Dict[str, Any]]) -> bool:
        """Save new leads to file"""
        try:
            with open(self.new_leads_file, 'w') as f:
                json.dump(leads, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving new leads: {e}")
            return False
    
    async def get_outbox(self) -> List[Dict[str, Any]]:
        """Get outbox (sent emails)"""
        try:
            with open(self.outbox_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading outbox: {e}")
            return []
    
    async def add_to_outbox(self, email_data: Dict[str, Any]) -> bool:
        """Add email to outbox"""
        try:
            outbox = await self.get_outbox()
            outbox.append(email_data)
            
            with open(self.outbox_file, 'w') as f:
                json.dump(outbox, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error adding to outbox: {e}")
            return False
    
    async def get_lead_stats(self) -> Dict[str, int]:
        """Get lead statistics"""
        try:
            existing_leads = await self.get_existing_leads()
            new_leads = await self.get_new_leads()
            
            return {
                'total_leads': len(existing_leads) + len(new_leads),
                'existing_leads': len(existing_leads),
                'new_leads': len(new_leads)
            }
        except Exception as e:
            logger.error(f"Error getting lead stats: {e}")
            return {'total_leads': 0, 'existing_leads': 0, 'new_leads': 0}

# Global CRM service instance
crm_service = CRMService()
