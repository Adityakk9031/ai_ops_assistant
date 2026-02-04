"""Gemini API client for LLM interactions."""

import os
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Gemini API."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.logger = logging.getLogger("gemini_client")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate_json(self, system_instruction: str, user_prompt: str, 
                     temperature: float = 0.1) -> Dict[str, Any]:
        """
        Generate JSON response from Gemini API.
        
        Args:
            system_instruction: System instruction for the model
            user_prompt: User prompt
            temperature: Temperature for generation (lower = more deterministic)
            
        Returns:
            Parsed JSON response
            
        Raises:
            ValueError: If response is not valid JSON
        """
        self.logger.info(f"Generating JSON with model {self.model_name}")
        
        # Configure model with JSON response format
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=system_instruction
        )
        
        try:
            response = model.generate_content(user_prompt)
            
            # Extract text from response
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse JSON
            try:
                result = json.loads(response.text)
                self.logger.info("Successfully generated and parsed JSON response")
                return result
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON: {response.text}")
                raise ValueError(f"Invalid JSON response: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def validate_and_retry_json(self, system_instruction: str, user_prompt: str,
                               validator: callable, max_retries: int = 2) -> Dict[str, Any]:
        """
        Generate JSON with validation and automatic retry.
        
        Args:
            system_instruction: System instruction for the model
            user_prompt: User prompt
            validator: Function that validates the JSON (returns True if valid)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Validated JSON response
            
        Raises:
            ValueError: If validation fails after all retries
        """
        for attempt in range(max_retries + 1):
            try:
                result = self.generate_json(system_instruction, user_prompt)
                
                # Validate result
                if validator(result):
                    return result
                else:
                    if attempt < max_retries:
                        self.logger.warning(f"Validation failed, retrying (attempt {attempt + 1}/{max_retries})")
                        # Add correction prompt
                        user_prompt += "\n\nPREVIOUS RESPONSE WAS INVALID. Please ensure your response matches the required schema exactly."
                    else:
                        raise ValueError("Validation failed after all retries")
                        
            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(f"Generation failed, retrying (attempt {attempt + 1}/{max_retries}): {str(e)}")
                else:
                    raise
        
        raise ValueError("Failed to generate valid JSON after all retries")


def load_prompt_template(prompt_file: str) -> Dict[str, str]:
    """
    Load prompt template from JSON file.
    
    Args:
        prompt_file: Path to prompt JSON file
        
    Returns:
        Dictionary with 'system_instruction' and 'user_template'
    """
    with open(prompt_file, 'r') as f:
        return json.load(f)
