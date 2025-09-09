"""
===========================================================
Project: Thryvix Email Agent
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Schema Validator - Validate LLM outputs against JSON Schema / HJSON
Ensures structured outputs conform to expected format
"""

import json

def is_email_existing(email_to_check):
    """
    Check if the given email exists in the CRM JSON file.

    Args:
        email_to_check (str): Email to check.

    Returns:
        bool: True if email exists, False otherwise.
    """
    json_file_path = "AI_AGENTS/data/crm/customers.json"  
    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
        
        # Check if any record has the email
        return any(record.get("email") == email_to_check for record in data)
    
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return False
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {json_file_path}")
        return False

