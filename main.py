"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
AI Agents - Simple Main Entry Point
Simple AI-powered text generation system with LLM fallback.

Main Use:
---------
Acts as the main entry point that:
1. Initializes the LLM manager
2. Starts the FastAPI web server
3. Provides simple text generation and email processing
"""

import uvicorn
from config.settings import settings
from web_server import app
from agents.llm_manager import llm_manager
from utils.logger import logger

def main():
    """Main entry point for the AI Agents system."""
    print("🚀 AI Agents - Simple LLM System")
    print("=" * 50)
    print(f"Configuration:")
    print(f"  - Host: {settings.host}")
    print(f"  - Port: {settings.port}")
    print(f"  - Debug: {settings.debug}")
    print(f"  - Available Models: {llm_manager.get_available_models()}")
    print("=" * 50)
    print(f"🌐 Web Interface: http://{settings.host}:{settings.port}")
    print(f"📊 Dashboard: http://{settings.host}:{settings.port}/dashboard")
    print(f"🔗 API Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)
    
    # Start the web server
    uvicorn.run(
        "web_server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

if __name__ == "__main__":
    main()