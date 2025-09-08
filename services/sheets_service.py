"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Google Sheets Service
Handles logging and data storage to Google Sheets.

Main Use:
---------
Google Sheets integration that:
1. Logs email processing results to Google Sheets
2. Retrieves processed email data
3. Provides fallback when Sheets unavailable
4. Manages authentication and API calls
"""

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import Dict, List, Optional
from config.settings import settings

class SheetsService:
    """Service for interacting with Google Sheets."""
    
    def __init__(self):
        """Initialize Google Sheets service."""
        # =============== start __init__ ======
        self.service = None
        self.sheet_id = settings.SHEET_ID
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Sheets API service."""
        # =============== start _initialize_service ======
        try:
            if not settings.GOOGLE_SHEETS_CREDENTIALS:
                print("Google Sheets credentials not configured")
                return
            
            # Define the scope
            scope = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Load credentials
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_SHEETS_CREDENTIALS, 
                scopes=scope
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=creds)
            print("Google Sheets service initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            self.service = None
    
    def log_email_data(self, sender_name: str, email_content: str, reply: str) -> bool:
        """
        Log email data to Google Sheets.
        
        Args:
            sender_name: Name of the sender
            email_content: Original email content
            reply: Generated reply
            
        Returns:
            True if successful, False otherwise
        """
        # =============== start log_email_data ======
        if not self.service:
            print("Google Sheets service not available")
            return False
        
        try:
            # Prepare data for insertion
            values = [[sender_name, email_content[:1000], reply[:1000], "processed"]]
            
            # Insert data
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=settings.SHEET_RANGE,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Data logged to Google Sheets: {result.get('updates', {}).get('updatedRows', 0)} rows")
            return True
            
        except Exception as e:
            print(f"Error logging to Google Sheets: {e}")
            return False
    
    def get_processed_emails(self) -> List[Dict[str, str]]:
        """
        Retrieve processed emails from Google Sheets.
        
        Returns:
            List of email data dictionaries
        """
        if not self.service:
            print("Google Sheets service not available")
            return []
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=settings.SHEET_RANGE
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []
            
            # Convert to list of dictionaries
            headers = values[0] if values else ['sender_name', 'email_content', 'reply', 'status']
            emails = []
            
            for row in values[1:]:
                email_data = {}
                for i, header in enumerate(headers):
                    email_data[header] = row[i] if i < len(row) else ""
                emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"Error retrieving data from Google Sheets: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Google Sheets service is available."""
        return self.service is not None
