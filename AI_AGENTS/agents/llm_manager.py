"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Simple LLM Manager with fallback logic.
Initializes all available LLM models at once and provides fallback functionality.

Main Use:
---------
Centralized LLM management that:
1. Initializes all available LLM models at startup
2. Provides fallback logic - if one LLM fails, try another
3. Uses only LangChain's built-in caching
4. Simple interface for text generation
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache

from config.settings import settings
from utils.logger import logger

# Set up LangChain's built-in caching
set_llm_cache(InMemoryCache())

class LLMManager:
    """Simple LLM Manager with fallback logic."""
    
    def __init__(self):
        """Initialize all available LLM models."""
        self.models = {}
        self.model_order = []  # Order to try models in case of failure
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available LLM models."""
        # Initializing LLM models...
        
        # OpenAI
        if settings.openai_api_key and settings.openai_api_key != "your_openai_key":
            try:
                self.models["openai"] = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model="gpt-3.5-turbo",
                    max_tokens=2000,
                    temperature=0.7
                )
                self.model_order.append("openai")
                # OpenAI model initialized
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Groq
        if settings.groq_api_key and settings.groq_api_key != "your_groq_key":
            try:
                self.models["groq"] = ChatGroq(
                    api_key=settings.groq_api_key,
                    model="llama-3.1-8b-instant",
                    max_tokens=2000,
                    temperature=0.7
                )
                self.model_order.append("groq")
                # Groq model initialized
            except Exception as e:
                logger.warning(f"Failed to initialize Groq: {e}")
        
        # Google Gemini
        if settings.google_api_key and settings.google_api_key != "your_google_key":
            try:
                self.models["google"] = ChatGoogleGenerativeAI(
                    api_key=settings.google_api_key,
                    model="gemini-1.5-flash",
                    max_tokens=2000,
                    temperature=0.7
                )
                self.model_order.append("google")
                # Google Gemini model initialized
            except Exception as e:
                logger.warning(f"Failed to initialize Google Gemini: {e}")
        
        # Anthropic
        if settings.anthropic_api_key and settings.anthropic_api_key != "your_anthropic_key":
            try:
                self.models["anthropic"] = ChatAnthropic(
                    api_key=settings.anthropic_api_key,
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    temperature=0.7
                )
                self.model_order.append("anthropic")
                # Anthropic model initialized
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic: {e}")
        
        if not self.models:
            logger.error("No LLM models available! Please configure API keys in .env file")
            raise ValueError("No LLM models available! Please configure API keys in .env file")
        
        # Initialized LLM models
    
    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        preferred_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using available LLM models with fallback logic.
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt
            preferred_model: Preferred model to try first
            
        Returns:
            Dictionary with response, model_used, and success status
        """
        start_time = time.time()
        
        # Determine which models to try
        models_to_try = []
        if preferred_model and preferred_model in self.models:
            models_to_try.append(preferred_model)
        
        # Add other models in order
        for model in self.model_order:
            if model not in models_to_try:
                models_to_try.append(model)
        
        # Try each model until one succeeds
        for model_name in models_to_try:
            try:
                # Trying model...
                
                model = self.models[model_name]
                
                # Prepare messages
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=prompt))
                
                # Generate response
                response = await model.ainvoke(messages)
                
                processing_time = time.time() - start_time
                
                result = {
                    "success": True,
                    "response": response.content,
                    "model_used": model_name,
                    "processing_time": processing_time,
                    "error": None
                }
                
                # Successfully generated response
                return result
                
            except Exception as e:
                logger.warning(f"Failed to generate response with {model_name}: {e}")
                continue
        
        # If all models failed
        processing_time = time.time() - start_time
        error_msg = "All LLM models failed to generate response"
        logger.error(error_msg)
        
        return {
            "success": False,
            "response": "I apologize, but I'm unable to generate a response at this time. Please try again later.",
            "model_used": None,
            "processing_time": processing_time,
            "error": error_msg
        }
    
    async def generate_email_reply(
        self, 
        sender_name: str, 
        email_content: str,
        preferred_model: Optional[str] = None
    ) -> str:
        """Generate email reply with fallback logic."""
        system_prompt = f"""You are a professional email assistant. Generate a helpful, 
        concise reply to {sender_name}. Be polite, professional, and address their concerns appropriately.
        Keep the response brief and to the point."""
        
        result = await self.generate_text(
            prompt=email_content,
            system_prompt=system_prompt,
            preferred_model=preferred_model
        )
        
        if result["success"]:
            return result["response"]
        else:
            return f"Thank you for your email, {sender_name}. I'll get back to you soon."
    
    async def extract_sender_name(
        self, 
        email_content: str,
        preferred_model: Optional[str] = None
    ) -> Optional[str]:
        """Extract sender name with fallback logic."""
        system_prompt = """You are an expert email parser. Extract the sender's name from the email content. 
        Return only the name, nothing else. If no clear name is found, return 'Unknown'."""
        
        result = await self.generate_text(
            prompt=email_content,
            system_prompt=system_prompt,
            preferred_model=preferred_model
        )
        
        if result["success"]:
            name = result["response"].strip()
            return name if name and name != "Unknown" else None
        else:
            return None
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.models.keys())
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models."""
        return {
            "available_models": self.get_available_models(),
            "model_count": len(self.models),
            "model_order": self.model_order
        }

# Global LLM manager instance
llm_manager = LLMManager()
