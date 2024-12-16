from typing import Dict, List, Any
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import json
from src.utils.claude_client import ClaudeClient

class BaseAgent(ABC):
    """Base class for all principal agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.conversation_history = []
        self.claude = ClaudeClient()
        
    @abstractmethod
    def _get_agent_specialties(self) -> Dict[str, str]:
        """Get agent's areas of specialty"""
        pass
        
    async def analyze(self, context: Dict) -> Dict:
        """Analyze the conversation context and provide insights"""
        prompt = f"""
        As {self.name}, analyze this career conversation:
        
        Basic Information:
        - Name: {context['user_info'].get('name')}
        - Current Role: {context['user_info'].get('current_role')}
        - Experience: {context['user_info'].get('experience_years')} years
        - Education: {context['user_info'].get('education')}
        - Industry: {context['user_info'].get('industry')}
        
        {context.get('career_vision_summary', 'Career Vision not yet discussed')}
        
        Total Responses: {context.get('response_count', 0)}
        
        Conversation History:
        {json.dumps(context['conversation_history'], indent=2)}
        
        Provide a structured analysis focusing on:
        1. Career Vision Analysis
           - Clarity of goals
           - Alignment with background
           - Level of ambition
           - Actionability
        
        2. Skills and Experience Assessment
           - Current capabilities
           - Skill gaps
           - Development needs
           - Learning opportunities
        
        3. Strategic Recommendations
           - Immediate next steps
           - Medium-term objectives
           - Long-term strategy
           - Development priorities
        
        Format the response as a structured JSON object with clear sections and insights.
        """
        
        try:
            response = await self.claude.get_response(
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in analysis: {e}")
            return {
                "error": str(e),
                "fallback_analysis": self._generate_fallback_analysis(context)
            }
            
    def _generate_fallback_analysis(self, context: Dict) -> Dict:
        """Generate a basic analysis when the main analysis fails"""
        return {
            "career_stage": "early" if int(context['user_info'].get('experience_years', 0)) < 5 else "mid",
            "basic_insights": {
                "role": context['user_info'].get('current_role', 'unknown'),
                "industry": context['user_info'].get('industry', 'unknown'),
                "response_count": context.get('response_count', 0)
            },
            "recommendations": [
                "Focus on skill development",
                "Build professional network",
                "Gain practical experience"
            ]
        }
        
    def log_interaction(self, interaction_type: str, details: Dict):
        """Log an interaction for analysis"""
        self.conversation_history.append({
            "type": interaction_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })