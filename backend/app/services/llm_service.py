import httpx
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = settings.OPENROUTER_MODEL # Default is openrouter/free
        
    async def get_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Get completion from OpenRouter using only free models
        """
        if not self.api_key:
            return "OpenRouter API Key not configured. Please add OPENROUTER_API_KEY to your environment variables."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/trae-ide/fraud-detection-platform", # Optional, for OpenRouter rankings
            "X-Title": "Fraud Detection Platform", # Optional
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    print(f"OpenRouter Error: {error_data}")
                    return f"Error from AI service: {error_data.get('error', {}).get('message', 'Unknown error')}"
                
                result = response.json()
                return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"LLM Service Error: {e}")
            return f"Failed to connect to AI service: {str(e)}"

    async def generate_fraud_insights(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate natural language insights about fraud trends using free LLM
        """
        prompt = f"""
        You are a senior fraud analyst. Analyze the following ML model performance metrics and provide 3 key insights.
        Metrics: {json.dumps(metrics)}
        
        Provide the response in the following JSON format:
        [
            {{"title": "Insight Title", "content": "Detailed analysis content", "pros": ["advantage1"], "cons": ["disadvantage1"]}},
            ...
        ]
        Only return the JSON array.
        """
        
        messages = [
            {"role": "system", "content": "You are a senior fraud detection expert. You only output valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response_text = await self.get_completion(messages)
        
        try:
            # Clean up response if it contains markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            return json.loads(response_text)
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            # Fallback to static insights if LLM fails
            return [
                {
                    "title": "Model Performance Analysis",
                    "content": "The current models show strong detection capabilities, particularly in identifying high-value transaction fraud.",
                    "pros": ["High precision"],
                    "cons": ["Potential false positives in international transactions"]
                }
            ]

llm_service = LLMService()
