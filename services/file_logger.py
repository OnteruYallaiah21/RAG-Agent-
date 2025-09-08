"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
File Logger Service
Alternative logging service using local files (CSV/txt) as fallback.

Main Use:
---------
Local file logging system that:
1. Logs email data to CSV files
2. Provides application logging to text files
3. Serves as fallback when cloud services unavailable
4. Manages local data storage and retrieval
"""

import csv
import os
from datetime import datetime
from typing import Dict, List
from config.settings import settings

class FileLogger:
    """Service for logging data to local files."""
    
    def __init__(self):
        """Initialize file logger with data directory."""
        # =============== start __init__ ======
        self.data_dir = "data"
        self.senders_file = os.path.join(self.data_dir, "senders.csv")
        self.logs_file = os.path.join(self.data_dir, "logs.txt")
        self._ensure_data_directory()
        self._initialize_csv_file()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists."""
        # =============== start _ensure_data_directory ======
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"Created data directory: {self.data_dir}")
    
    def _initialize_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist."""
        # =============== start _initialize_csv_file ======
        if not os.path.exists(self.senders_file):
            with open(self.senders_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'sender_name', 'email_content', 'reply', 'status'])
            print(f"Initialized CSV file: {self.senders_file}")
    
    def log_email_data(self, sender_name: str, email_content: str, reply: str) -> bool:
        """
        Log email data to CSV file.
        
        Args:
            sender_name: Name of the sender
            email_content: Original email content
            reply: Generated reply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().isoformat()
            
            with open(self.senders_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp,
                    sender_name,
                    email_content[:1000],  # Truncate for storage
                    reply[:1000],
                    'processed'
                ])
            
            print(f"Data logged to CSV: {self.senders_file}")
            return True
            
        except Exception as e:
            print(f"Error logging to CSV file: {e}")
            return False
    
    def log_message(self, message: str, level: str = "INFO"):
        """
        Log a message to the logs file.
        
        Args:
            message: Message to log
            level: Log level (INFO, ERROR, WARNING, etc.)
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {level}: {message}\n"
            
            with open(self.logs_file, 'a', encoding='utf-8') as file:
                file.write(log_entry)
            
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def get_processed_emails(self) -> List[Dict[str, str]]:
        """
        Retrieve processed emails from CSV file.
        
        Returns:
            List of email data dictionaries
        """
        try:
            emails = []
            
            if not os.path.exists(self.senders_file):
                return emails
            
            with open(self.senders_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    emails.append(dict(row))
            
            return emails
            
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []
    
    def get_logs(self, lines: int = 100) -> List[str]:
        """
        Retrieve recent log entries.
        
        Args:
            lines: Number of recent lines to retrieve
            
        Returns:
            List of log entries
        """
        try:
            if not os.path.exists(self.logs_file):
                return []
            
            with open(self.logs_file, 'r', encoding='utf-8') as file:
                all_lines = file.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
                
        except Exception as e:
            print(f"Error reading log file: {e}")
            return []
