from typing import Dict, List
from src.agents.base_agent import BaseAgent

class VisionPrincipal(BaseAgent):
    """Vision Principal specializes in analyzing career vision and aspirations"""
    
    def __init__(self, name: str = "Vision Principal"):
        super().__init__(name)
        
    def _get_agent_specialties(self) -> Dict[str, str]:
        """Get agent's areas of specialty"""
        return {
            "vision_analysis": "Career vision and goal analysis",
            "aspiration_mapping": "Mapping aspirations to career paths",
            "potential_assessment": "Assessing career potential and opportunities",
            "strategic_planning": "Long-term career strategy development"
        }
        
    async def analyze(self, context: Dict) -> Dict:
        """Analyze career vision and provide insights"""
        # Extract career vision responses
        career_vision_responses = [
            entry for entry in context['conversation_history'] 
            if entry.get("section") == "Career Vision"
        ]
        
        # Analyze vision clarity and ambition
        vision_analysis = self._analyze_vision_responses(career_vision_responses)
        
        # Analyze alignment with background
        alignment_analysis = self._analyze_vision_alignment(
            career_vision_responses,
            context['user_info']
        )
        
        # Generate strategic recommendations
        recommendations = self._generate_vision_recommendations(
            vision_analysis,
            alignment_analysis,
            context['user_info']
        )
        
        return {
            "vision_analysis": vision_analysis,
            "alignment_analysis": alignment_analysis,
            "recommendations": recommendations,
            "career_vision_summary": context.get('career_vision_summary', '')
        }
        
    def _analyze_vision_responses(self, vision_responses: List[Dict]) -> Dict:
        """Analyze career vision responses for clarity and ambition"""
        if not vision_responses:
            return {
                "clarity_level": "undefined",
                "ambition_level": "undefined",
                "vision_completeness": 0,
                "key_themes": []
            }
            
        # Analyze response content
        responses_text = [resp["response"].lower() for resp in vision_responses]
        
        # Assess clarity
        clarity_indicators = {
            "high": ["specific", "clear", "defined", "exactly", "precisely"],
            "medium": ["think", "believe", "probably", "maybe"],
            "low": ["unsure", "not sure", "don't know", "unclear"]
        }
        
        clarity_scores = {level: sum(1 for ind in indicators for resp in responses_text if ind in resp)
                         for level, indicators in clarity_indicators.items()}
        
        clarity_level = max(clarity_scores.items(), key=lambda x: x[1])[0] if any(clarity_scores.values()) else "medium"
        
        # Assess ambition
        ambition_indicators = {
            "high": ["change the world", "revolutionary", "innovative", "leader", "best"],
            "medium": ["improve", "develop", "grow", "advance"],
            "moderate": ["stable", "secure", "comfortable", "balanced"]
        }
        
        ambition_scores = {level: sum(1 for ind in indicators for resp in responses_text if ind in resp)
                          for level, indicators in ambition_indicators.items()}
        
        ambition_level = max(ambition_scores.items(), key=lambda x: x[1])[0] if any(ambition_scores.values()) else "medium"
        
        # Extract key themes
        themes = set()
        theme_indicators = {
            "innovation": ["innovative", "new", "create", "develop"],
            "leadership": ["lead", "manage", "direct", "guide"],
            "technical": ["technical", "technology", "system", "build"],
            "impact": ["impact", "change", "improve", "help"],
            "growth": ["grow", "learn", "develop", "advance"]
        }
        
        for theme, indicators in theme_indicators.items():
            if any(any(ind in resp for ind in indicators) for resp in responses_text):
                themes.add(theme)
        
        return {
            "clarity_level": clarity_level,
            "ambition_level": ambition_level,
            "vision_completeness": len(vision_responses) / 3 * 100,  # Assuming 3 vision questions
            "key_themes": list(themes),
            "raw_responses": vision_responses
        }
        
    def _analyze_vision_alignment(self, vision_responses: List[Dict], user_info: Dict) -> Dict:
        """Analyze alignment between vision and background"""
        if not vision_responses:
            return {
                "alignment_level": "undefined",
                "gap_areas": [],
                "strengths": []
            }
            
        current_role = user_info.get('current_role', '').lower()
        industry = user_info.get('industry', '').lower()
        experience_years = int(user_info.get('experience_years', 0))
        
        # Analyze alignment factors
        alignment_factors = {
            "role_alignment": self._assess_role_alignment(vision_responses, current_role),
            "industry_alignment": self._assess_industry_alignment(vision_responses, industry),
            "experience_alignment": self._assess_experience_alignment(vision_responses, experience_years)
        }
        
        # Calculate overall alignment
        alignment_scores = [score for score in alignment_factors.values() if score > 0]
        overall_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0
        
        # Determine alignment level
        if overall_alignment > 0.7:
            alignment_level = "strong"
        elif overall_alignment > 0.4:
            alignment_level = "moderate"
        else:
            alignment_level = "weak"
            
        # Identify gaps and strengths
        gaps = []
        strengths = []
        for factor, score in alignment_factors.items():
            if score < 0.4:
                gaps.append(factor)
            elif score > 0.7:
                strengths.append(factor)
                
        return {
            "alignment_level": alignment_level,
            "alignment_factors": alignment_factors,
            "gap_areas": gaps,
            "strengths": strengths
        }
        
    def _assess_role_alignment(self, vision_responses: List[Dict], current_role: str) -> float:
        """Assess alignment between vision and current role"""
        if not vision_responses or not current_role:
            return 0.0
            
        role_keywords = set(current_role.split())
        alignment_score = 0
        
        for response in vision_responses:
            response_text = response["response"].lower()
            matching_keywords = sum(1 for keyword in role_keywords if keyword in response_text)
            alignment_score += matching_keywords / len(role_keywords) if role_keywords else 0
            
        return alignment_score / len(vision_responses)
        
    def _assess_industry_alignment(self, vision_responses: List[Dict], industry: str) -> float:
        """Assess alignment between vision and industry"""
        if not vision_responses or not industry:
            return 0.0
            
        industry_keywords = set(industry.split())
        alignment_score = 0
        
        for response in vision_responses:
            response_text = response["response"].lower()
            matching_keywords = sum(1 for keyword in industry_keywords if keyword in response_text)
            alignment_score += matching_keywords / len(industry_keywords) if industry_keywords else 0
            
        return alignment_score / len(vision_responses)
        
    def _assess_experience_alignment(self, vision_responses: List[Dict], experience_years: int) -> float:
        """Assess alignment between vision and experience level"""
        if not vision_responses:
            return 0.0
            
        # Define experience-appropriate keywords
        experience_indicators = {
            "entry": ["learn", "start", "begin", "develop", "grow"],
            "mid": ["lead", "manage", "improve", "advance", "specialize"],
            "senior": ["direct", "strategy", "transform", "executive", "vision"]
        }
        
        # Determine appropriate level
        if experience_years < 3:
            appropriate_level = "entry"
        elif experience_years < 8:
            appropriate_level = "mid"
        else:
            appropriate_level = "senior"
            
        # Calculate alignment
        alignment_score = 0
        appropriate_keywords = experience_indicators[appropriate_level]
        
        for response in vision_responses:
            response_text = response["response"].lower()
            matching_keywords = sum(1 for keyword in appropriate_keywords if keyword in response_text)
            alignment_score += matching_keywords / len(appropriate_keywords)
            
        return alignment_score / len(vision_responses)
        
    def _generate_vision_recommendations(self, vision_analysis: Dict, alignment_analysis: Dict, user_info: Dict) -> List[Dict]:
        """Generate recommendations based on vision analysis"""
        recommendations = []
        
        # Vision clarity recommendations
        if vision_analysis["clarity_level"] != "high":
            recommendations.append({
                "area": "Vision Clarity",
                "recommendation": "Develop more specific career goals",
                "actions": [
                    "Define specific 1-year, 3-year, and 5-year goals",
                    "Research specific roles and positions of interest",
                    "Identify concrete milestones for career progression"
                ],
                "priority": "high"
            })
            
        # Alignment recommendations
        if alignment_analysis["alignment_level"] != "strong":
            recommendations.append({
                "area": "Career Alignment",
                "recommendation": "Bridge gaps between current position and career vision",
                "actions": [
                    "Identify specific skills needed for desired roles",
                    "Seek opportunities to gain relevant experience",
                    "Build network in target areas"
                ],
                "priority": "high"
            })
            
        # Ambition-based recommendations
        if vision_analysis["ambition_level"] == "high":
            recommendations.append({
                "area": "Growth Strategy",
                "recommendation": "Develop structured approach to achieve ambitious goals",
                "actions": [
                    "Create detailed development plan",
                    "Identify potential mentors and sponsors",
                    "Look for high-visibility projects"
                ],
                "priority": "medium"
            })
            
        return recommendations 