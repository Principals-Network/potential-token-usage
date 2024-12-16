from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.utils.claude_client import ClaudeClient
import json
import logging

class VisionPrincipal(BaseAgent):
    def __init__(self):
        super().__init__("Vision Principal")
        self.claude = ClaudeClient()
        self.system_prompt = """You are a Vision Principal at Principals Network, 
        specializing in understanding and shaping career aspirations. Your expertise includes:
        - Long-term career vision development
        - Goal alignment and strategic planning
        - Value and motivation analysis
        - Career trajectory optimization
        """
        self.vision_questions = [
            "What impact do you want to make in your career?",
            "Where do you see yourself in 5-10 years?",
            "What industries or fields excite you the most?",
            "What are your core values in work and life?",
            "What kind of work environment helps you thrive?"
        ]
        self.current_question_index = 0
        self.conversation_messages = []
        self.logger = logging.getLogger(__name__)

    async def interview(self, user_input: str) -> str:
        if user_input:
            self.save_response(user_input, "")
            self.conversation_messages.append({"role": "user", "content": user_input})
            try:
                await self._update_user_profile(user_input)
            except Exception as e:
                self.logger.error(f"Error updating user profile: {e}")
                # Continue with the interview even if profile update fails

        if self.current_question_index < len(self.vision_questions):
            question = self.vision_questions[self.current_question_index]
            self.current_question_index += 1
            return question
        
        return await self._generate_vision_summary()

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user input for career vision insights"""
        user_input = data.get("user_input", "")
        
        prompt = f"""Analyze this user input from a career vision perspective:
        "{user_input}"
        
        Provide insights in this exact JSON format. Use empty arrays or "unknown" for missing information:
        {{
            "career_goals": [
                {{
                    "goal": "string",
                    "timeframe": "short_term|medium_term|long_term",
                    "confidence": "high|medium|low"
                }}
            ],
            "values": [
                {{
                    "value": "string",
                    "importance": "high|medium|low"
                }}
            ],
            "interests": [
                {{
                    "area": "string",
                    "level": "high|medium|low"
                }}
            ],
            "vision_clarity": "high|medium|low"
        }}
        """
        
        try:
            response = await self.claude.get_response(
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in vision analysis: {e}")
            return {
                "career_goals": [],
                "values": [],
                "interests": [],
                "vision_clarity": "unknown"
            }

    async def _update_user_profile(self, response: str):
        prompt = f"""Based on the user's response: "{response}"
        Please analyze their career vision and extract key themes, values, and preferences.
        Be specific and detailed in your analysis.
        
        Respond with a JSON object in this exact format:
        {{
            "themes": [
                {{"theme": "string", "confidence": "high|medium|low", "evidence": "string"}},
                ...
            ],
            "values": [
                {{"value": "string", "importance": "high|medium|low", "context": "string"}},
                ...
            ],
            "preferences": [
                {{"preference": "string", "type": "environment|role|industry", "details": "string"}},
                ...
            ]
        }}
        """
        
        try:
            analysis = await self.claude.get_response(
                messages=[{"role": "user", "content": prompt}]
            )
            # Parse the JSON response
            parsed_analysis = json.loads(analysis)
            self.user_profile.update(parsed_analysis)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON from Claude: {e}")
            self.logger.debug(f"Raw response: {analysis}")
        except Exception as e:
            self.logger.error(f"Error in _update_user_profile: {e}")

    async def _generate_vision_summary(self) -> str:
        prompt = """Based on our conversation, please provide a comprehensive summary 
        of the user's career vision, including:
        1. Key aspirations and goals
        2. Core values and motivations
        3. Preferred industries and environments
        4. Potential growth areas
        
        Provide the response in a clear, narrative format."""

        try:
            return await self.claude.get_response(
                messages=self.conversation_messages + [{"role": "user", "content": prompt}]
            )
        except Exception as e:
            self.logger.error(f"Error generating vision summary: {e}")
            return "Unable to generate vision summary at this time."

    def _calculate_profile_completeness(self) -> Dict[str, Any]:
        """Calculate how complete and confident we are in the user profile"""
        completeness = {
            "overall_score": 0,
            "areas": {
                "career_vision": 0,
                "values": 0,
                "skills": 0,
                "preferences": 0
            },
            "missing_info": [],
            "suggested_questions": []
        }
        
        # Calculate scores based on collected information
        if self.user_profile.get("themes"):
            completeness["areas"]["career_vision"] = len(self.user_profile["themes"]) * 20
        
        if self.user_profile.get("values"):
            completeness["areas"]["values"] = len(self.user_profile["values"]) * 20
            
        # Add missing information
        if completeness["areas"]["career_vision"] < 60:
            completeness["missing_info"].append("Detailed career goals")
            completeness["suggested_questions"].append(
                "Can you elaborate on your specific goals in the space technology sector?"
            )
            
        # Calculate overall score
        completeness["overall_score"] = sum(completeness["areas"].values()) / len(completeness["areas"])
        
        return completeness

    async def generate_followup_questions(self) -> List[str]:
        """Generate personalized follow-up questions based on user profile"""
        prompt = f"""Based on the user's profile and responses so far:
        {json.dumps(self.user_profile, indent=2)}
        
        Generate 3 specific follow-up questions that would help clarify or deepen our understanding
        of their career aspirations in the space technology sector.
        
        Format the response as a JSON array of strings, each containing one question."""
        
        try:
            response = await self.claude.get_response(
                messages=[{"role": "user", "content": prompt}]
            )
            questions = json.loads(response)
            return questions
        except Exception as e:
            self.logger.error(f"Error generating follow-up questions: {e}")
            return [
                "Could you tell me more about your specific interests in space technology?",
                "What kind of testing experience do you currently have?",
                "Which space companies or projects inspire you the most?"
            ]