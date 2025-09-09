"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
LangChain-based agents with tools and advanced prompt engineering.
Implements sophisticated AI agents for email processing and response generation.

Main Use:
---------
Advanced AI agents that:
1. Use LangChain framework for complex AI workflows
2. Implement custom tools for email analysis and processing
3. Provide prompt engineering and optimization
4. Orchestrate multi-agent workflows for complex tasks
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

from config.settings import settings
from agents.llm_manager import llm_manager
from utils.logger import logger

class EmailAnalysisTool(BaseTool):
    """Tool for analyzing email content and extracting key information."""
    
    name: str = "email_analyzer"
    description: str = "Analyze email content to extract sender information, sentiment, and key topics"
    
    def _run(self, email_content: str) -> str:
        """Synchronous version of the tool."""
        return asyncio.run(self._arun(email_content))
    
    async def _arun(self, email_content: str) -> str:
        """Analyze email content asynchronously."""
        # =============== start _arun ======
        try:
            # Extract basic information
            analysis = {
                "word_count": len(email_content.split()),
                "has_greeting": any(greeting in email_content.lower() for greeting in ["hello", "hi", "dear", "good morning"]),
                "has_question": "?" in email_content,
                "urgency_indicators": ["urgent", "asap", "immediately", "critical"] in email_content.lower(),
                "sentiment": "neutral"  # Could be enhanced with sentiment analysis
            }
            
            return f"Email Analysis: {analysis}"
            
        except Exception as e:
            logger.error(f"Error in email analysis: {e}")
            return f"Analysis failed: {str(e)}"

class SenderExtractionTool(BaseTool):
    """Tool for extracting sender information from emails."""
    
    name: str = "sender_extractor"
    description: str = "Extract sender name and email address from email content"
    
    def _run(self, email_content: str) -> str:
        """Synchronous version of the tool."""
        return asyncio.run(self._arun(email_content))
    
    async def _arun(self, email_content: str) -> str:
        """Extract sender information asynchronously."""
        try:
            import re
            
            # Extract email address
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, email_content)
            email_address = email_match.group(0) if email_match else "Not found"
            
            # Extract name patterns
            name_patterns = [
                r'From:\s*([^<\n]+)',
                r'Sender:\s*([^<\n]+)',
                r'^([^<\n]+)\s*<[^>]+>',
            ]
            
            sender_name = "Not found"
            for pattern in name_patterns:
                match = re.search(pattern, email_content, re.IGNORECASE | re.MULTILINE)
                if match:
                    sender_name = match.group(1).strip()
                    break
            
            return f"Sender: {sender_name}, Email: {email_address}"
            
        except Exception as e:
            logger.error(f"Error in sender extraction: {e}")
            return f"Extraction failed: {str(e)}"

class ResponseGeneratorTool(BaseTool):
    """Tool for generating contextual email responses."""
    
    name: str = "response_generator"
    description: str = "Generate appropriate email responses based on content and context"
    
    def _run(self, email_content: str, sender_name: str = "there") -> str:
        """Synchronous version of the tool."""
        return asyncio.run(self._arun(email_content, sender_name))
    
    async def _arun(self, email_content: str, sender_name: str = "there") -> str:
        """Generate response asynchronously."""
        try:
            # Use AI provider manager to generate response
            response = await ai_provider_manager.generate_reply(
                sender_name=sender_name,
                email_content=email_content,
                provider=AIProvider.OPENAI
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Thank you for your email, {sender_name}. I'll get back to you soon."

class EmailProcessingAgent:
    """Advanced email processing agent with LangChain tools."""
    
    def __init__(self, provider: AIProvider = AIProvider.OPENAI):
        """Initialize the email processing agent."""
        self.provider = provider
        self.llm = ai_provider_manager.get_provider(provider)
        
        # Check if provider is available
        if not self.llm:
            available_providers = ai_provider_manager.get_available_providers()
            if available_providers:
                # Use the first available provider
                self.provider = available_providers[0]
                self.llm = ai_provider_manager.get_provider(self.provider)
                logger.warning(f"Requested provider {provider.value} not available, using {self.provider.value}")
            else:
                logger.error("No AI providers available. Please configure API keys in .env file")
                raise ValueError("No AI providers available. Please configure API keys in .env file")
        
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5
        )
    
    def _create_tools(self) -> List[BaseTool]:
        """Create tools for the agent."""
        return [
            EmailAnalysisTool(),
            SenderExtractionTool(),
            ResponseGeneratorTool()
        ]
    
    def _create_agent(self):
        """Create the agent with prompt template."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert email processing assistant. Your role is to:
            1. Analyze incoming emails to understand their content and context
            2. Extract sender information accurately
            3. Generate appropriate, professional responses
            4. Use the available tools to gather information and generate responses
            
            Always be professional, helpful, and contextually appropriate in your responses.
            Use the tools available to you to gather information before generating responses."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        return create_openai_tools_agent(self.llm, self.tools, prompt)
    
    async def process_email(self, email_content: str) -> Dict[str, Any]:
        """Process email using the agent."""
        try:
            # Create input for the agent
            agent_input = f"""
            Please process this email:
            
            {email_content}
            
            Steps:
            1. Analyze the email content
            2. Extract sender information
            3. Generate an appropriate response
            """
            
            # Execute the agent
            result = await self.agent_executor.ainvoke({
                "input": agent_input
            })
            
            return {
                "success": True,
                "result": result,
                "provider": self.provider.value
            }
            
        except Exception as e:
            logger.error(f"Error in agent processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider.value
            }

class PromptEngineeringAgent:
    """Agent specialized in prompt engineering and optimization."""
    
    def __init__(self, provider: AIProvider = AIProvider.OPENAI):
        """Initialize the prompt engineering agent."""
        self.provider = provider
        self.llm = ai_provider_manager.get_provider(provider)
        
        # Check if provider is available
        if not self.llm:
            available_providers = ai_provider_manager.get_available_providers()
            if available_providers:
                # Use the first available provider
                self.provider = available_providers[0]
                self.llm = ai_provider_manager.get_provider(self.provider)
                logger.warning(f"Requested provider {provider.value} not available, using {self.provider.value}")
            else:
                logger.error("No AI providers available. Please configure API keys in .env file")
                raise ValueError("No AI providers available. Please configure API keys in .env file")
    
    def create_email_extraction_prompt(self, context: str = "") -> str:
        """Create optimized prompt for email extraction."""
        return f"""
        You are an expert email parser with the following context: {context}
        
        TASK: Extract sender information from the email content below.
        
        REQUIREMENTS:
        - Extract the sender's full name (if available)
        - Extract the sender's email address (if available)
        - Identify the email subject/topic
        - Determine the urgency level (low, medium, high)
        - Extract key topics or concerns mentioned
        
        OUTPUT FORMAT:
        {{
            "sender_name": "extracted name or null",
            "sender_email": "extracted email or null",
            "subject": "email subject or null",
            "urgency": "low/medium/high",
            "topics": ["topic1", "topic2", ...],
            "confidence": 0.0-1.0
        }}
        
        EMAIL CONTENT:
        """
    
    def create_response_generation_prompt(self, sender_name: str, context: Dict[str, Any]) -> str:
        """Create optimized prompt for response generation."""
        return f"""
        You are a professional email assistant responding to {sender_name}.
        
        CONTEXT:
        - Sender: {sender_name}
        - Urgency: {context.get('urgency', 'medium')}
        - Topics: {', '.join(context.get('topics', []))}
        - Previous interactions: {context.get('history', 'none')}
        
        TASK: Generate a professional, helpful email response.
        
        GUIDELINES:
        - Be polite and professional
        - Address their specific concerns
        - Keep the response concise but complete
        - Match the urgency level appropriately
        - Use a warm but professional tone
        
        RESPONSE REQUIREMENTS:
        - Start with appropriate greeting
        - Acknowledge their message
        - Address their concerns
        - Provide next steps or information
        - End with professional closing
        
        Generate the response now:
        """
    
    async def optimize_prompt(self, original_prompt: str, task_type: str) -> str:
        """Optimize a prompt for better performance."""
        optimization_prompt = f"""
        You are a prompt engineering expert. Optimize the following prompt for {task_type}:
        
        ORIGINAL PROMPT:
        {original_prompt}
        
        OPTIMIZATION REQUIREMENTS:
        - Make it more specific and clear
        - Add examples if helpful
        - Improve structure and flow
        - Ensure it follows best practices
        - Maintain the original intent
        
        Provide the optimized prompt:
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=optimization_prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Error optimizing prompt: {e}")
            return original_prompt

class MultiAgentOrchestrator:
    """Orchestrates multiple agents for complex email processing tasks."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.agents = {
            "email_processor": EmailProcessingAgent(),
            "prompt_engineer": PromptEngineeringAgent()
        }
    
    async def process_email_with_agents(
        self,
        email_content: str,
        use_optimized_prompts: bool = True
    ) -> Dict[str, Any]:
        """Process email using multiple agents."""
        try:
            results = {}
            
            # Step 1: Use prompt engineering agent to create optimized prompts
            if use_optimized_prompts:
                extraction_prompt = self.agents["prompt_engineer"].create_email_extraction_prompt()
                response_prompt = self.agents["prompt_engineer"].create_response_generation_prompt(
                    "Unknown", {"urgency": "medium", "topics": []}
                )
                results["optimized_prompts"] = {
                    "extraction": extraction_prompt,
                    "response": response_prompt
                }
            
            # Step 2: Use email processing agent
            processing_result = await self.agents["email_processor"].process_email(email_content)
            results["processing"] = processing_result
            
            # Step 3: Generate final response
            if processing_result["success"]:
                # Extract information from agent result
                agent_output = processing_result["result"].get("output", "")
                
                # Use AI provider manager for final response
                final_response = await ai_provider_manager.generate_response(
                    prompt=f"Based on this analysis: {agent_output}\n\nGenerate a professional email response.",
                    provider=AIProvider.OPENAI
                )
                
                results["final_response"] = final_response.dict()
            
            return {
                "success": True,
                "results": results,
                "agents_used": list(self.agents.keys())
            }
            
        except Exception as e:
            logger.error(f"Error in multi-agent processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "agents_used": list(self.agents.keys())
            }
    
    async def batch_process_with_agents(
        self,
        emails: List[Dict[str, Any]],
        use_optimized_prompts: bool = True
    ) -> List[Dict[str, Any]]:
        """Process multiple emails using agents."""
        tasks = []
        
        for email in emails:
            task = self.process_email_with_agents(
                email.get("content", ""),
                use_optimized_prompts
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing email {i} with agents: {result}")
                processed_results.append({
                    "error": str(result),
                    "email": emails[i],
                    "success": False
                })
            else:
                processed_results.append(result)
        
        return processed_results

# Global agent instances - only create if providers are available
try:
    email_processing_agent = EmailProcessingAgent()
    prompt_engineering_agent = PromptEngineeringAgent()
    multi_agent_orchestrator = MultiAgentOrchestrator()
except ValueError as e:
    logger.warning(f"Could not initialize agents: {e}")
    email_processing_agent = None
    prompt_engineering_agent = None
    multi_agent_orchestrator = None
