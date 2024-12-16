from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.utils.claude_client import ClaudeClient
import json
import logging

class BackgroundPrincipal(BaseAgent):
    def __init__(self):
        super().__init__("Background Principal")
        self.claude = ClaudeClient()
        self.system_prompt = """You are a Background Principal at Principals Network, 
        specializing in analyzing skills, experience, and qualifications. Your expertise includes:
        - Skills assessment and gap analysis
        - Experience evaluation
        - Educational background analysis
        - Professional development planning
        """
        self.logger = logging.getLogger(__name__)

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user input and provide background-related insights"""
        conversation_history = data.get("conversation_history", [])
        user_info = data.get("user_info", {})
        
        prompt = f"""
        Based on this user information and conversation history:
        User Info: {json.dumps(user_info, indent=2)}
        Conversation: {json.dumps(conversation_history, indent=2)}
        
        Provide a comprehensive background analysis in this exact JSON format:
        {{
            "skills_assessment": [
                {{
                    "skill": "string",
                    "level": "expert|proficient|beginner",
                    "evidence": "string"
                }}
            ],
            "experience_analysis": {{
                "years_experience": "number",
                "key_achievements": [],
                "industry_exposure": []
            }},
            "education_insights": {{
                "formal_education": [],
                "certifications": [],
                "continuous_learning": []
            }},
            "development_areas": [
                {{
                    "area": "string",
                    "priority": "high|medium|low",
                    "rationale": "string"
                }}
            ],
            "summary": "string"
        }}
        """
        
        try:
            response = await self.claude.get_response(
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in background analysis: {e}")
            return {
                "skills_assessment": [],
                "experience_analysis": {
                    "years_experience": 0,
                    "key_achievements": [],
                    "industry_exposure": []
                },
                "education_insights": {
                    "formal_education": [],
                    "certifications": [],
                    "continuous_learning": []
                },
                "development_areas": [],
                "summary": "Error analyzing background"
            }