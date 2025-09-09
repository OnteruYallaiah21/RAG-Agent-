"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
AI Provider Manager with LangChain integration.
Supports multiple AI providers: OpenAI, Groq, Google Gemini, Anthropic.

Main Use:
---------
Centralized AI provider management that:
1. Manages multiple AI providers with unified interface
2. Handles streaming responses and async operations
3. Provides caching and performance optimization
4. Supports batch processing and concurrent operations
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from config.settings import settings
?from utils.logger import logger

class StreamingCallbackHandler(AsyncCallbackHandler):
    """Custom callback handler for streaming responses."""
    
    def __init__(self, websocket=None):
        self.websocket = websocket
        self.chunks = []
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Handle new token in streaming response."""
        chunk = StreamingChunk(
            chunk_id=f"chunk_{len(self.chunks)}",
            content=token,
            is_final=False
        )
        self.chunks.append(chunk)
        
        if self.websocket:
            try:
                await self.websocket.send_text(chunk.json())
            except Exception as e:
                logger.error(f"Error sending streaming chunk: {e}")
    
    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Handle end of LLM response."""
        if self.chunks:
            # Mark last chunk as final
            self.chunks[-1].is_final = True
            if self.websocket:
                try:
                    await self.websocket.send_text(self.chunks[-1].json())
                except Exception as e:
                    logger.error(f"Error sending final chunk: {e}")

class AIProviderManager:
    """Manages multiple AI providers with LangChain integration."""
    
    def __init__(self):
        """Initialize AI provider manager."""
        # =============== start __init__ ======
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers."""
        # =============== start _initialize_providers ======
        # OpenAI
        if settings.is_provider_available(AIProvider.OPENAI):
            config = settings.get_ai_provider_config(AIProvider.OPENAI)
            self.providers[AIProvider.OPENAI] = ChatOpenAI(
                api_key=config["api_key"],
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            logger.info("OpenAI provider initialized")
        
        # Groq
        if settings.is_provider_available(AIProvider.GROQ):
            config = settings.get_ai_provider_config(AIProvider.GROQ)
            self.providers[AIProvider.GROQ] = ChatGroq(
                api_key=config["api_key"],
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            logger.info("Groq provider initialized")
        
        # Google Gemini
        if settings.is_provider_available(AIProvider.GOOGLE):
            config = settings.get_ai_provider_config(AIProvider.GOOGLE)
            self.providers[AIProvider.GOOGLE] = ChatGoogleGenerativeAI(
                api_key=config["api_key"],
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            logger.info("Google Gemini provider initialized")
        
        # Anthropic
        if settings.is_provider_available(AIProvider.ANTHROPIC):
            config = settings.get_ai_provider_config(AIProvider.ANTHROPIC)
            self.providers[AIProvider.ANTHROPIC] = ChatAnthropic(
                api_key=config["api_key"],
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            logger.info("Anthropic provider initialized")
    
    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available providers."""
        # =============== start get_available_providers ======
        return list(self.providers.keys())
    
    def get_provider(self, provider: AIProvider) -> Optional[Any]:
        """Get specific provider instance."""
        # =============== start get_provider ======
        return self.providers.get(provider)
    
    async def generate_response(
        self,
        prompt: str,
        provider: AIProvider,
        system_prompt: Optional[str] = None,
        use_cache: bool = True
    ) -> AIResponse:
        """Generate AI response using specified provider."""
        # =============== start generate_response ======
        start_time = time.time()
        
        try:
            # Check cache first
            if use_cache:
                cached_response = await cache_service.get_ai_response(
                    prompt, provider.value, settings.default_model
                )
                if cached_response:
                    logger.info(f"Using cached response for {provider.value}")
                    return AIResponse(**cached_response)
            
            # Get provider
            llm = self.get_provider(provider)
            if not llm:
                raise ValueError(f"Provider {provider.value} not available")
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            response = await llm.ainvoke(messages)
            
            # Calculate metrics
            processing_time = time.time() - start_time
            tokens_used = getattr(response, 'response_metadata', {}).get('token_usage', {}).get('total_tokens', 0)
            
            # Create AI response
            ai_response = AIResponse(
                reply=response.content,
                confidence=0.9,  # Default confidence
                model_used=settings.default_model,
                provider=provider,
                tokens_used=tokens_used,
                processing_time=processing_time
            )
            
            # Cache response
            if use_cache:
                await cache_service.set_ai_response(
                    prompt, provider.value, settings.default_model, ai_response.dict()
                )
            
            logger.info(f"Generated response using {provider.value} in {processing_time:.2f}s")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating response with {provider.value}: {e}")
            raise
    
    async def generate_response_stream(
        self,
        prompt: str,
        provider: AIProvider,
        system_prompt: Optional[str] = None,
        websocket=None
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Generate streaming AI response."""
        # =============== start generate_response_stream ======
        try:
            # Get provider
            llm = self.get_provider(provider)
            if not llm:
                raise ValueError(f"Provider {provider.value} not available")
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Set up streaming callback
            callback_handler = StreamingCallbackHandler(websocket)
            
            # Generate streaming response
            async for chunk in llm.astream(messages, callbacks=[callback_handler]):
                if hasattr(chunk, 'content') and chunk.content:
                    streaming_chunk = StreamingChunk(
                        chunk_id=f"chunk_{int(time.time() * 1000)}",
                        content=chunk.content,
                        is_final=False
                    )
                    yield streaming_chunk
            
            # Send final chunk
            final_chunk = StreamingChunk(
                chunk_id=f"chunk_final_{int(time.time() * 1000)}",
                content="",
                is_final=True
            )
            yield final_chunk
            
        except Exception as e:
            logger.error(f"Error generating streaming response with {provider.value}: {e}")
            raise
    
    async def extract_sender_name(
        self,
        email_content: str,
        provider: AIProvider = AIProvider.OPENAI
    ) -> Optional[str]:
        """Extract sender name using AI."""
        # =============== start extract_sender_name ======
        system_prompt = """You are an expert email parser. Extract the sender's name from the email content. 
        Return only the name, nothing else. If no clear name is found, return 'Unknown'."""
        
        try:
            response = await self.generate_response(
                prompt=email_content,
                provider=provider,
                system_prompt=system_prompt
            )
            
            name = response.reply.strip()
            return name if name and name != "Unknown" else None
            
        except Exception as e:
            logger.error(f"Error extracting sender name: {e}")
            return None
    
    async def generate_reply(
        self,
        sender_name: str,
        email_content: str,
        provider: AIProvider = AIProvider.OPENAI
    ) -> str:
        """Generate email reply using AI."""
        # =============== start generate_reply ======
        system_prompt = f"""You are a professional email assistant. Generate a helpful, 
        concise reply to {sender_name}. Be polite, professional, and address their concerns appropriately."""
        
        try:
            response = await self.generate_response(
                prompt=email_content,
                provider=provider,
                system_prompt=system_prompt
            )
            
            return response.reply
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return f"Thank you for your email, {sender_name}. I'll get back to you soon."
    
    async def batch_process_emails(
        self,
        emails: List[Dict[str, Any]],
        provider: AIProvider = AIProvider.OPENAI
    ) -> List[Dict[str, Any]]:
        """Process multiple emails concurrently."""
        # =============== start batch_process_emails ======
        tasks = []
        
        for email in emails:
            task = self.process_single_email(email, provider)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing email {i}: {result}")
                processed_results.append({
                    "error": str(result),
                    "email": emails[i]
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def process_single_email(
        self,
        email: Dict[str, Any],
        provider: AIProvider = AIProvider.OPENAI
    ) -> Dict[str, Any]:
        """Process a single email."""
        # =============== start process_single_email ======
        try:
            # Extract sender name
            sender_name = await self.extract_sender_name(
                email.get("content", ""), provider
            )
            
            # Generate reply
            reply = await self.generate_reply(
                sender_name or "there",
                email.get("content", ""),
                provider
            )
            
            return {
                "sender_name": sender_name,
                "reply": reply,
                "provider": provider.value,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return {
                "error": str(e),
                "provider": provider.value,
                "success": False
            }
    
    async def get_provider_health(self) -> Dict[str, Any]:
        """Check health of all providers."""
        # =============== start get_provider_health ======
        health_status = {}
        
        for provider in self.get_available_providers():
            try:
                # Simple test prompt
                test_response = await self.generate_response(
                    prompt="Hello, this is a test.",
                    provider=provider,
                    use_cache=False
                )
                
                health_status[provider.value] = {
                    "status": "healthy",
                    "response_time": test_response.processing_time,
                    "model": test_response.model_used
                }
                
            except Exception as e:
                health_status[provider.value] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health_status

# Global AI provider manager instance
ai_provider_manager = AIProviderManager()
