"""
===========================================================
Project: Thryvix Email Agent
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Email Service - Sends emails via SMTP/Gmail/SendGrid (async)
Handles email sending with multiple providers
"""

import asyncio
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import os

from config.settings import settings
from utils.logger import logger

class EmailService:
    """Service for sending emails with multiple providers"""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
        self.from_name = settings.from_name
    
    async def send_email(self, 
                        to: str, 
                        subject: str, 
                        body: str, 
                        html_body: Optional[str] = None) -> Dict[str, Any]:
        """Send email using SMTP"""
        try:
            # Sending email...
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to
            
            # Add text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Send email
            result = await self._send_smtp_email(message, to)
            
            if result['success']:
                # Email sent successfully
                pass
            else:
                logger.error(f"Failed to send email to {to}: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None
            }
    
    async def _send_smtp_email(self, message: MIMEMultipart, to: str) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Create SMTP connection
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                
                # Send email
                text = message.as_string()
                server.sendmail(self.from_email, to, text)
                
                # Generate message ID
                message_id = f"msg_{int(asyncio.get_event_loop().time() * 1000)}"
                
                return {
                    'success': True,
                    'message_id': message_id,
                    'error': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message_id': None,
                'error': str(e)
            }
    
    async def send_bulk_email(self, 
                             recipients: list, 
                             subject: str, 
                             body: str, 
                             html_body: Optional[str] = None) -> Dict[str, Any]:
        """Send bulk email to multiple recipients"""
        try:
            logger.info(f"Sending bulk email to {len(recipients)} recipients")
            
            results = []
            successful = 0
            failed = 0
            
            # Send emails concurrently
            tasks = []
            for recipient in recipients:
                task = self.send_email(recipient, subject, body, html_body)
                tasks.append(task)
            
            # Wait for all emails to be sent
            email_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(email_results):
                if isinstance(result, Exception):
                    results.append({
                        'recipient': recipients[i],
                        'success': False,
                        'error': str(result)
                    })
                    failed += 1
                else:
                    results.append({
                        'recipient': recipients[i],
                        'success': result['success'],
                        'error': result.get('error')
                    })
                    if result['success']:
                        successful += 1
                    else:
                        failed += 1
            
            logger.info(f"Bulk email completed: {successful} successful, {failed} failed")
            
            return {
                'success': failed == 0,
                'total': len(recipients),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error sending bulk email: {e}")
            return {
                'success': False,
                'total': len(recipients),
                'successful': 0,
                'failed': len(recipients),
                'error': str(e)
            }
    
    async def send_template_email(self, 
                                 to: str, 
                                 template_name: str, 
                                 template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send email using template"""
        try:
            # Load template
            template = await self._load_template(template_name)
            if not template:
                return {
                    'success': False,
                    'error': f"Template {template_name} not found",
                    'message_id': None
                }
            
            # Replace variables in template
            subject = template['subject'].format(**template_vars)
            body = template['body'].format(**template_vars)
            html_body = template.get('html_body', '').format(**template_vars) if template.get('html_body') else None
            
            # Send email
            return await self.send_email(to, subject, body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending template email: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None
            }
    
    async def _load_template(self, template_name: str) -> Optional[Dict[str, str]]:
        """Load email template"""
        try:
            template_file = f"templates/email/{template_name}.json"
            if os.path.exists(template_file):
                import json
                with open(template_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            return None
    
    async def validate_email(self, email: str) -> bool:
        """Validate email format"""
        try:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception as e:
            logger.error(f"Error validating email {email}: {e}")
            return False
    
    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """Get email delivery status (placeholder for future implementation)"""
        try:
            # In a real implementation, this would check with the email provider
            # For now, we'll return a mock status
            return {
                'message_id': message_id,
                'status': 'delivered',
                'delivered_at': asyncio.get_event_loop().time(),
                'error': None
            }
        except Exception as e:
            logger.error(f"Error getting delivery status: {e}")
            return {
                'message_id': message_id,
                'status': 'unknown',
                'delivered_at': None,
                'error': str(e)
            }

# Global email service instance
email_service = EmailService()
