"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Simple run script to start the AI Agents application on port 5000.

Main Use:
---------
Quick start script that:
1. Starts the application on port 5000
2. Shows helpful startup information
3. Provides easy access to the welcome page
"""

#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    print("🚀 Starting AI Agents on Port 5000...")
    print("=" * 50)
    print("Welcome to AI Agents World!")
    print("Developer: Yallaiah Onteru")
    print("Contact: yonteru414@gmail.com")
    print("=" * 50)
    main()
