"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Email Parser Utility
Fallback email parsing functions when AI extraction fails.

Main Use:
---------
Email parsing utilities that:
1. Extract sender information using regex patterns
2. Parse email headers and content
3. Provide fallback when AI extraction fails
4. Clean and normalize email content
"""

import re
from typing import Optional, Dict

class EmailParser:
    """Utility class for parsing email content."""
    
    @staticmethod
    def extract_sender_name_fallback(email_content: str) -> Optional[str]:
        """
        Fallback method to extract sender name using regex patterns.
        
        Args:
            email_content: Raw email content
            
        Returns:
            Extracted sender name or None if not found
        """
        # =============== start extract_sender_name_fallback ======
        # Common patterns for sender name extraction
        patterns = [
            r'From:\s*([^<\n]+)',
            r'Sender:\s*([^<\n]+)',
            r'^([^<\n]+)\s*<[^>]+>',  # Name <email@domain.com>
            r'^([^@\n]+)@',  # name@domain.com
        ]
        
        for pattern in patterns:
            match = re.search(pattern, email_content, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'["\']', '', name)  # Remove quotes
                name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
                if name and len(name) > 1:
                    return name
        
        return None
    
    @staticmethod
    def extract_email_address(email_content: str) -> Optional[str]:
        """
        Extract email address from email content.
        
        Args:
            email_content: Raw email content
            
        Returns:
            Email address or None if not found
        """
        # =============== start extract_email_address ======
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, email_content)
        return match.group(0) if match else None
    
    @staticmethod
    def parse_email_headers(email_content: str) -> Dict[str, str]:
        """
        Parse common email headers from content.
        
        Args:
            email_content: Raw email content
            
        Returns:
            Dictionary of parsed headers
        """
        # =============== start parse_email_headers ======
        headers = {}
        
        # Common header patterns
        header_patterns = {
            'from': r'From:\s*([^\n]+)',
            'to': r'To:\s*([^\n]+)',
            'subject': r'Subject:\s*([^\n]+)',
            'date': r'Date:\s*([^\n]+)',
            'reply_to': r'Reply-To:\s*([^\n]+)',
        }
        
        for header_name, pattern in header_patterns.items():
            match = re.search(pattern, email_content, re.IGNORECASE)
            if match:
                headers[header_name] = match.group(1).strip()
        
        return headers
    
    @staticmethod
    def clean_email_content(email_content: str) -> str:
        """
        Clean and normalize email content.
        
        Args:
            email_content: Raw email content
            
        Returns:
            Cleaned email content
        """
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', email_content)
        
        # Remove common email artifacts
        content = re.sub(r'^>+', '', content, flags=re.MULTILINE)  # Remove quote markers
        content = re.sub(r'On .+ wrote:', '', content, flags=re.IGNORECASE)  # Remove reply headers
        
        return content.strip()
    
    @staticmethod
    def extract_message_body(email_content: str) -> str:
        """
        Extract the main message body from email content.
        
        Args:
            email_content: Raw email content
            
        Returns:
            Extracted message body
        """
        # Split by common separators
        separators = [
            '\n\n',  # Double newline
            '---',   # Common separator
            '___',   # Another common separator
        ]
        
        for separator in separators:
            if separator in email_content:
                parts = email_content.split(separator, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # If no separator found, return the whole content
        return email_content.strip()
