"""
===========================================================
Project: Thryvix Email Agent
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Notification Agent - Triggers notifications to sales/account managers
Handles real-time notifications and alerts
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from utils.logger import logger

@dataclass
class Notification:
    """Notification structure"""
    id: str
    type: str
    title: str
    message: str
    priority: str
    timestamp: float
    read: bool = False
    data: Optional[Dict[str, Any]] = None

class NotificationAgent:
    """Agent for managing notifications and alerts"""
    
    def __init__(self):
        self.notifications: List[Notification] = []
        self.subscribers: Dict[str, List[str]] = {
            'new_lead': ['sales@thryvix.ai', 'manager@thryvix.ai'],
            'existing_lead': ['account@thryvix.ai'],
            'high_priority': ['ceo@thryvix.ai', 'manager@thryvix.ai'],
            'error': ['dev@thryvix.ai', 'manager@thryvix.ai']
        }
    
    async def create_notification(self, 
                                notification_type: str, 
                                title: str, 
                                message: str, 
                                priority: str = 'medium',
                                data: Optional[Dict[str, Any]] = None) -> str:
        """Create a new notification"""
        try:
            notification_id = f"notif_{int(asyncio.get_event_loop().time() * 1000)}"
            
            notification = Notification(
                id=notification_id,
                type=notification_type,
                title=title,
                message=message,
                priority=priority,
                timestamp=asyncio.get_event_loop().time(),
                data=data
            )
            
            self.notifications.append(notification)
            
            # Send to subscribers
            await self._notify_subscribers(notification)
            
            logger.info(f"Created notification: {notification_id} - {title}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return ""
    
    async def notify_new_lead(self, lead_data: Dict[str, Any]) -> str:
        """Notify about new lead"""
        title = "New Lead Added"
        message = f"New lead: {lead_data.get('name')} ({lead_data.get('email')}) - Intent: {lead_data.get('intent')}"
        
        return await self.create_notification(
            notification_type='new_lead',
            title=title,
            message=message,
            priority='high',
            data=lead_data
        )
    
    async def notify_existing_lead(self, lead_data: Dict[str, Any]) -> str:
        """Notify about existing lead interaction"""
        title = "Existing Lead Contact"
        message = f"Existing lead contacted: {lead_data.get('name')} ({lead_data.get('email')}) - Intent: {lead_data.get('intent')}"
        
        return await self.create_notification(
            notification_type='existing_lead',
            title=title,
            message=message,
            priority='medium',
            data=lead_data
        )
    
    async def notify_email_sent(self, email_data: Dict[str, Any]) -> str:
        """Notify about email sent"""
        title = "Email Sent Successfully"
        message = f"Email sent to {email_data.get('to')} - Subject: {email_data.get('subject')}"
        
        return await self.create_notification(
            notification_type='email_sent',
            title=title,
            message=message,
            priority='low',
            data=email_data
        )
    
    async def notify_error(self, error_data: Dict[str, Any]) -> str:
        """Notify about error"""
        title = "System Error"
        message = f"Error occurred: {error_data.get('error', 'Unknown error')}"
        
        return await self.create_notification(
            notification_type='error',
            title=title,
            message=message,
            priority='high',
            data=error_data
        )
    
    async def get_notifications(self, 
                              notification_type: Optional[str] = None,
                              unread_only: bool = False,
                              limit: int = 50) -> List[Notification]:
        """Get notifications with optional filtering"""
        try:
            filtered_notifications = self.notifications.copy()
            
            # Filter by type
            if notification_type:
                filtered_notifications = [
                    n for n in filtered_notifications 
                    if n.type == notification_type
                ]
            
            # Filter unread only
            if unread_only:
                filtered_notifications = [
                    n for n in filtered_notifications 
                    if not n.read
                ]
            
            # Sort by timestamp (newest first)
            filtered_notifications.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Limit results
            return filtered_notifications[:limit]
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        try:
            for notification in self.notifications:
                if notification.id == notification_id:
                    notification.read = True
                    logger.info(f"Marked notification as read: {notification_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    async def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        try:
            return len([n for n in self.notifications if not n.read])
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0
    
    async def _notify_subscribers(self, notification: Notification):
        """Send notification to subscribers"""
        try:
            subscribers = self.subscribers.get(notification.type, [])
            
            for subscriber in subscribers:
                # In a real implementation, this would send actual notifications
                # For now, we'll just log them
                logger.info(f"Notifying {subscriber}: {notification.title} - {notification.message}")
                
        except Exception as e:
            logger.error(f"Error notifying subscribers: {e}")
    
    async def cleanup_old_notifications(self, days: int = 30):
        """Clean up notifications older than specified days"""
        try:
            cutoff_time = asyncio.get_event_loop().time() - (days * 24 * 60 * 60)
            
            original_count = len(self.notifications)
            self.notifications = [
                n for n in self.notifications 
                if n.timestamp > cutoff_time
            ]
            
            removed_count = original_count - len(self.notifications)
            logger.info(f"Cleaned up {removed_count} old notifications")
            
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {e}")

# Global notification agent instance
notification_agent = NotificationAgent()
