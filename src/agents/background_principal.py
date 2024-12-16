from typing import Dict, List, Any
from src.agents.base_agent import BaseAgent
import logging

class BackgroundPrincipal(BaseAgent):
    """Background Principal specializes in analyzing experience and skills"""
    
    def __init__(self, name: str = "Background Principal"):
        super().__init__(name)
        self.logger = logging.getLogger(__name__)
        
    def _get_agent_specialties(self) -> Dict[str, str]:
        """Get agent's areas of specialty"""
        return {
            "experience_analysis": "Professional experience analysis",
            "skill_assessment": "Technical and soft skills assessment",
            "background_evaluation": "Educational and career background evaluation",
            "competency_mapping": "Skills to career path mapping"
        }
        
    async def analyze(self, context: Dict) -> Dict:
        """Analyze background and provide insights"""
        # Extract relevant responses
        experience_responses = [
            entry for entry in context['conversation_history'] 
            if entry.get("section") == "Skills & Experience"
        ]
        
        # Analyze experience and skills
        experience_analysis = self._analyze_experience(
            experience_responses,
            context['user_info']
        )
        
        # Analyze education and background
        background_analysis = self._analyze_background(
            context['user_info']
        )
        
        # Generate recommendations
        recommendations = self._generate_background_recommendations(
            experience_analysis,
            background_analysis,
            context['user_info']
        )
        
        return {
            "experience_analysis": experience_analysis,
            "background_analysis": background_analysis,
            "recommendations": recommendations
        }
        
    def _analyze_experience(self, experience_responses: List[Dict], user_info: Dict) -> Dict:
        """Analyze professional experience and skills"""
        if not experience_responses:
            return {
                "experience_level": "undefined",
                "skill_assessment": {},
                "strengths": [],
                "development_areas": []
            }
            
        # Analyze responses
        responses_text = [resp["response"].lower() for resp in experience_responses]
        
        # Assess technical skills
        technical_skills = {
            "programming": ["coding", "programming", "development", "software"],
            "data": ["analytics", "data", "analysis", "metrics"],
            "design": ["design", "user experience", "interface", "creative"],
            "management": ["leadership", "management", "coordination", "planning"]
        }
        
        skill_scores = {category: sum(1 for ind in indicators for resp in responses_text if ind in resp)
                       for category, indicators in technical_skills.items()}
        
        # Identify strengths and development areas
        strengths = [skill for skill, score in skill_scores.items() if score > 1]
        development_areas = [skill for skill, score in skill_scores.items() if score == 0]
        
        # Determine experience level
        experience_years = int(user_info.get('experience_years', 0))
        experience_level = "senior" if experience_years > 8 else \
                          "mid" if experience_years > 3 else \
                          "entry"
        
        return {
            "experience_level": experience_level,
            "skill_assessment": skill_scores,
            "strengths": strengths,
            "development_areas": development_areas,
            "years_experience": experience_years
        }
        
    def _analyze_background(self, user_info: Dict) -> Dict:
        """Analyze educational and career background"""
        education = user_info.get('education', '').lower()
        current_role = user_info.get('current_role', '').lower()
        industry = user_info.get('industry', '').lower()
        
        # Determine education level
        education_levels = {
            "phd": ["phd", "doctorate", "doctor"],
            "masters": ["masters", "ms", "ma", "mba"],
            "bachelors": ["bachelors", "bs", "ba", "bsc"],
            "associate": ["associate", "as", "aa"],
            "certification": ["certification", "certificate", "diploma"]
        }
        
        education_level = next((level for level, indicators in education_levels.items()
                              if any(ind in education for ind in indicators)), "other")
        
        # Analyze role progression
        role_categories = {
            "technical": ["engineer", "developer", "analyst", "designer"],
            "management": ["manager", "lead", "head", "director"],
            "specialist": ["specialist", "expert", "consultant", "advisor"]
        }
        
        role_category = next((category for category, indicators in role_categories.items()
                            if any(ind in current_role for ind in indicators)), "other")
        
        return {
            "education_level": education_level,
            "role_category": role_category,
            "industry_context": industry,
            "background_alignment": self._assess_background_alignment(
                education_level,
                role_category,
                industry
            )
        }
        
    def _assess_background_alignment(self, education_level: str, role_category: str, industry: str) -> str:
        """Assess alignment between education, role, and industry"""
        # Define typical alignments
        typical_alignments = {
            "technical": ["bachelors", "masters", "phd"],
            "management": ["bachelors", "masters", "mba"],
            "specialist": ["masters", "phd", "certification"]
        }
        
        # Check alignment
        if role_category in typical_alignments and education_level in typical_alignments[role_category]:
            return "strong"
        elif education_level in ["bachelors", "masters", "phd"]:
            return "moderate"
        else:
            return "potential_gap"
        
    def _generate_background_recommendations(self, experience_analysis: Dict, background_analysis: Dict, user_info: Dict) -> List[Dict]:
        """Generate recommendations based on background analysis"""
        recommendations = []
        
        # Experience-based recommendations
        if experience_analysis["experience_level"] == "entry":
            recommendations.append({
                "area": "Experience Building",
                "recommendation": "Focus on foundational skill development",
                "actions": [
                    "Seek hands-on project experience",
                    "Build technical proficiency",
                    "Develop professional network"
                ],
                "priority": "high"
            })
        
        # Skill development recommendations
        if experience_analysis["development_areas"]:
            recommendations.append({
                "area": "Skill Development",
                "recommendation": "Address skill gaps in key areas",
                "actions": [
                    f"Develop expertise in {area}" for area in experience_analysis["development_areas"]
                ],
                "priority": "high"
            })
        
        # Background alignment recommendations
        if background_analysis["background_alignment"] == "potential_gap":
            recommendations.append({
                "area": "Education",
                "recommendation": "Consider formal education or certification",
                "actions": [
                    "Research relevant degree programs",
                    "Explore professional certifications",
                    "Identify key qualifications for career progression"
                ],
                "priority": "medium"
            })
        
        return recommendations
