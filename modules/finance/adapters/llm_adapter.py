import logging
import asyncio
from openai import AsyncOpenAI
from config import config

logger = logging.getLogger("LLMAdapter")

class LLMAdapter:
    """
    Adapter for Local LLM (Ollama/DeepSeek) using OpenAI compatible API.
    Provides async interface matching the pipeline requirements.
    """
    
    def __init__(self):
        if config.receipt_ai_provider == "openai":
            self.client = AsyncOpenAI(
                api_key=config.base.openai_api_key
            )
            logger.info("llm_adapter_openai_initialized", model=config.openai_receipt_model)
        else:
            self.client = AsyncOpenAI(
                base_url=f"{config.base.ollama_host}/v1",
                api_key="ollama"
            )
            logger.info("llm_adapter_ollama_initialized", model=config.ollama_receipt_model)
        
    async def generate_content_async(
        self, 
        user_prompt: str, 
        system_prompt: str, 
        response_format: str = "json",
        model_name: str = None
    ) -> str:
        """
        Generate content using AsyncOpenAI.
        """
        if model_name:
            model = model_name
        elif config.receipt_ai_provider == "openai":
            model = config.openai_receipt_model
        else:
            model = config.ollama_receipt_model
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Request
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                # response_format={"type": "json_object"} if response_format == "json" else None
                # Note: Ollama doesn't always strictly support response_format="json_object" depending on version/model
                # but DeepSeek usually handles prompt-based JSON well. 
                # We'll rely on system prompt instructions primarily.
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            raise e
