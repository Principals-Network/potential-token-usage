from typing import Dict, List, Any
from src.agents.base_agent import BaseAgent
import logging
import json
import asyncio
from datetime import datetime
from src.utils.response_cache import ResponseCache

class ConversationCoordinator:
    def __init__(self):
        # Configure logging to write to file only
        logging.basicConfig(
            filename='career_planner.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Configure logging to only show errors and suppress HTTP request logs
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("anthropic").setLevel(logging.WARNING)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # Add file handler
        file_handler = logging.FileHandler('career_planner.log')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.conversation_history = []
        self.principals = {}
        self.current_context = {}
        self.user_info = {}
        self.response_cache = ResponseCache()
        
    def add_principal(self, principal: BaseAgent):
        """Add a principal to the team"""
        self.principals[principal.name] = principal
        
    async def start_conversation(self):
        """Execute the three-phase career planning process"""
        print("\n=== Welcome to Principals Network ===")
        print("We'll guide you through a three-phase career planning process:\n")
        print("Phase 1: Interview - Understanding your background and aspirations")
        print("Phase 2: Principal Discussion - Our experts analyze and discuss your profile")
        print("Phase 3: Career Roadmap - Detailed recommendations and action plan\n")
        
        # Phase 1: Interview
        await self._conduct_interview_phase()
        
        # Phase 2: Principal Discussion
        await self._conduct_discussion_phase()
        
        # Phase 3: Generate Report
        await self._generate_roadmap_phase()

    async def _conduct_interview_phase(self):
        """Phase 1: Interview Phase"""
        print("\n=== Phase 1: Interview ===")
        print("Let's start by getting to know you better.\n")
        
        # Gather basic information
        await self._gather_basic_info()
        
        # Core interview questions
        interview_sections = [
            {
                "title": "Career Vision",
                "questions": [
                    "What impact would you like to make in your career?",
                    "Where do you see yourself in 5-10 years?",
                    "What excites you most about your field?"
                ]
            },
            {
                "title": "Skills & Experience",
                "questions": [
                    "What are your key strengths and skills?",
                    "What achievements are you most proud of?",
                    "What areas would you like to develop?"
                ]
            },
            {
                "title": "Values & Preferences",
                "questions": [
                    "What are your core values in work and life?",
                    "What type of work environment helps you thrive?",
                    "What motivates you the most?"
                ]
            }
        ]

        current_section_index = 0
        current_question_index = 0

        while current_section_index < len(interview_sections):
            section = interview_sections[current_section_index]
            
            if current_question_index == 0:
                print(f"\n--- {section['title']} ---")
            
            question = section['questions'][current_question_index]
            response = input(f"\nPrincipal: {question}\nYou: ")
            
            if response.lower() == 'quit':
                return
            elif response.lower() == 'back':
                # Go back to previous question
                if current_question_index > 0:
                    current_question_index -= 1
                elif current_section_index > 0:
                    current_section_index -= 1
                    current_question_index = len(interview_sections[current_section_index]['questions']) - 1
                continue
            
            # Save response
            self.conversation_history.append({
                "phase": "interview",
                "section": section['title'],
                "question": question,
                "response": response
            })
            
            # Move to next question
            current_question_index += 1
            if current_question_index >= len(section['questions']):
                current_question_index = 0
                current_section_index += 1

        print("\nThank you for sharing. Our principals will now analyze this information.")

    async def _conduct_discussion_phase(self):
        """Phase 2: Principals' Discussion Phase"""
        print("\n=== Phase 2: Principal Discussion ===")
        print("Our principals will now analyze and discuss your profile.")
        
        # Step 1: Individual Analysis
        analyses = await self._gather_individual_analyses()
        
        # Step 2: Structured Discussion
        discussion_points = await self._conduct_structured_discussion(analyses)
        
        # Step 3: Consensus Building
        consensus = await self._build_consensus(discussion_points)
        
        # Store consensus for roadmap generation
        self.current_context['consensus'] = consensus

    async def _gather_individual_analyses(self) -> Dict:
        """Each principal conducts their individual analysis"""
        print("\n--- Step 1: Individual Principal Analysis ---")
        analyses = {}
        
        # Format career vision responses for emphasis
        career_vision_responses = [
            entry for entry in self.conversation_history 
            if entry.get("section") == "Career Vision"
        ]
        
        vision_summary = "\nCareer Vision Responses:"
        for entry in career_vision_responses:
            vision_summary += f"\n- {entry['question']}: {entry['response']}"
        
        for name, principal in self.principals.items():
            print(f"\n{name} is analyzing your profile...")
            try:
                analysis_context = {
                    "conversation_history": self.conversation_history,
                    "user_info": self.user_info,
                    "career_vision_summary": vision_summary,
                    "response_count": len(self.conversation_history)
                }
                
                analysis = await principal.analyze(analysis_context)
                analyses[name] = analysis
                
                # Present initial insights
                print(f"\n{name}'s Key Insights:")
                await self._present_principal_insights(name, analysis)
                
            except Exception as e:
                self.logger.error(f"Error in {name}'s analysis: {e}")
        
        return analyses

    async def _conduct_structured_discussion(self, analyses: Dict) -> Dict:
        """Facilitate structured discussion between principals"""
        print("\n--- Step 2: Structured Discussion ---")
        
        discussion_framework = [
            {
                "topic": "Career Direction",
                "aspects": [
                    "Long-term vision alignment",
                    "Short-term objectives",
                    "Potential challenges"
                ]
            },
            {
                "topic": "Skills Assessment",
                "aspects": [
                    "Current capabilities",
                    "Critical gaps",
                    "Development priorities"
                ]
            },
            {
                "topic": "Market Alignment",
                "aspects": [
                    "Industry trends",
                    "Opportunity areas",
                    "Competitive advantages"
                ]
            },
            {
                "topic": "Development Strategy",
                "aspects": [
                    "Learning priorities",
                    "Experience building",
                    "Network development"
                ]
            }
        ]

        discussion_points = {}
        for framework in discussion_framework:
            print(f"\nDiscussing: {framework['topic']}")
            discussion_points[framework['topic']] = await self._discuss_topic(
                framework['topic'],
                framework['aspects'],
                analyses
            )
            
        return discussion_points

    async def _discuss_topic(self, topic: str, aspects: List[str], analyses: Dict) -> Dict:
        """Facilitate discussion on a specific topic"""
        prompt = f"""
        Topic for discussion: {topic}
        
        Based on these principal analyses:
        {json.dumps(analyses, indent=2)}
        
        Generate a focused discussion between principals addressing these aspects:
        {json.dumps(aspects, indent=2)}
        
        Format the discussion to show:
        1. Each principal's perspective
        2. Points of agreement and disagreement
        3. Supporting evidence for positions
        4. Resolution of any conflicting viewpoints
        
        End with clear conclusions for each aspect.
        """
        
        try:
            first_principal = list(self.principals.values())[0]
            discussion = await first_principal.claude.get_response(
                messages=[{"role": "user", "content": prompt}]
            )
            print(discussion)
            return {"discussion": discussion, "aspects": aspects}
        except Exception as e:
            self.logger.error(f"Error in topic discussion: {e}")
            return {"error": str(e)}

    async def _build_consensus(self, discussion_points: Dict) -> Dict:
        """Build consensus among principals"""
        print("\n--- Step 3: Building Consensus ---")
        
        consensus_prompt = f"""
        Based on the principal discussions:
        {json.dumps(discussion_points, indent=2)}
        
        Generate a consensus document that includes:
        
        1. Unified Vision:
           - Agreed career direction
           - Core development priorities
           - Key success factors
        
        2. Strategic Alignment:
           - Short-term priorities (0-6 months)
           - Medium-term objectives (6-18 months)
           - Long-term goals (18+ months)
        
        3. Development Framework:
           - Critical skills to develop
           - Experience targets
           - Learning milestones
        
        4. Success Metrics:
           - Key performance indicators
           - Progress checkpoints
           - Adjustment triggers
        
        Format as a structured consensus document with clear action items.
        """
        
        try:
            first_principal = list(self.principals.values())[0]
            consensus = await first_principal.claude.get_response(
                messages=[{"role": "user", "content": consensus_prompt}]
            )
            
            print("\nConsensus Reached:")
            print("=" * 50)
            print(consensus)
            print("=" * 50)
            
            return {
                "consensus_document": consensus,
                "discussion_points": discussion_points,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error building consensus: {e}")
            return {"error": str(e)}

    async def _present_principal_insights(self, name: str, analysis: Dict):
        """Present a principal's key insights"""
        insight_prompt = f"""
        As {name}, present your key insights from this analysis:
        {json.dumps(analysis, indent=2)}
        
        The user has provided specific career vision responses:
        {analysis.get('career_vision_summary', '')}
        
        Focus on:
        1. Most significant observations from the actual responses
        2. Critical recommendations based on stated goals
        3. Areas needing attention to achieve stated vision
        4. Unique opportunities aligned with user's aspirations
        
        Present in a clear, professional manner, directly referencing the user's actual responses.
        """
        
        try:
            first_principal = list(self.principals.values())[0]
            insights = await first_principal.claude.get_response(
                messages=[{"role": "user", "content": insight_prompt}]
            )
            print(insights)
        except Exception as e:
            self.logger.error(f"Error presenting insights: {e}")

    async def _generate_roadmap_phase(self):
        """Phase 3: Career Roadmap Generation"""
        print("\n=== Phase 3: Your Career Roadmap ===")
        print("Based on our discussion, we're creating your personalized career roadmap.")
        
        roadmap_sections = [
            "Executive Summary",
            "Career Vision & Goals",
            "Skills Development Plan",
            "Action Steps & Timeline",
            "Resources & Support"
        ]
        
        report = {}
        for section in roadmap_sections:
            print(f"\nGenerating {section}...")
            report[section] = await self._generate_report_section(section)
        
        # Present the final roadmap
        await self._present_career_roadmap(report)
        
        # Save the report
        self.save_report(report)

    def save_report(self, report: Dict, filename: str = "career_roadmap.txt"):
        """Save the career roadmap to a file"""
        try:
            with open(filename, 'w') as f:
                f.write("=== Principals Network Career Roadmap ===\n\n")
                f.write(f"Created for: {self.user_info.get('name', 'User')}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                
                for section, content in report.items():
                    f.write(f"\n{section}\n")
                    f.write("=" * len(section) + "\n")
                    f.write(content + "\n")
                
            print(f"\nYour career roadmap has been saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving roadmap: {e}")
            
    async def _gather_basic_info(self):
        """Gather basic information about the user"""
        questions = {
            "name": {
                "question": "What's your name?",
                "validation": lambda x: len(x.strip()) > 0,
                "error": "Name cannot be empty.",
                "response_template": "Welcome {}, I'm looking forward to helping you explore your career aspirations and develop a clear path forward - shall we start by learning more about your current role and career interests?"
            },
            "current_role": {
                "question": "What's your current role or field of study?",
                "validation": lambda x: len(x.strip()) > 0,
                "error": "Please provide your current role or field."
            },
            "experience_years": {
                "question": "How many years of professional experience do you have?",
                "validation": lambda x: x.isdigit() and 0 <= int(x) <= 50,
                "error": "Please enter a valid number between 0 and 50."
            },
            "education": {
                "question": "What's your highest level of education and field of study? (e.g., BS Computer Science)",
                "validation": lambda x: len(x.strip()) > 0,
                "error": "Please provide your education details."
            },
            "industry": {
                "question": "Which industry do you currently work in or are most interested in?",
                "validation": lambda x: len(x.strip()) > 0,
                "error": "Please specify an industry."
            }
        }
        
        current_question_index = 0
        question_keys = list(questions.keys())
        
        while current_question_index < len(questions):
            key = question_keys[current_question_index]
            question_data = questions[key]
            
            while True:
                response = input(f"\n{question_data['question']}\nYou: ")
                
                if response.lower() == 'quit':
                    return
                elif response.lower() == 'back':
                    if current_question_index > 0:
                        current_question_index -= 1
                        prev_key = question_keys[current_question_index]
                        if prev_key in self.user_info:
                            del self.user_info[prev_key]
                    break
                
                # Validate response
                if question_data['validation'](response):
                    self.user_info[key] = response
                    
                    # For name question, use the response template
                    if key == "name":
                        print(f"\n{question_data['response_template'].format(response)}")
                    
                    current_question_index += 1
                    break
                else:
                    print(f"\nError: {question_data['error']}")
                    print("Please try again.")

    async def _build_context(self, key: str) -> Dict[str, Any]:
        """Build rich context for AI responses"""
        base_context = {
            "user_profile": self.user_info,
            "conversation_stage": self._get_conversation_stage(),
            "previous_insights": self._get_previous_insights(),
            "interaction_history": self._get_interaction_summary()
        }

        # Add specific context based on the question type
        context_builders = {
            "name": self._build_initial_context,
            "current_role": self._build_role_context,
            "industry": self._build_industry_context,
            "experience_years": self._build_experience_context,
            "education": self._build_education_context
        }

        if key in context_builders:
            if key == "current_role":
                base_context.update(await context_builders[key]())
            else:
                base_context.update(context_builders[key]())

        return base_context

    def _get_conversation_stage(self) -> Dict[str, Any]:
        """Determine the current stage of the conversation"""
        return {
            "phase": "initial_interview" if len(self.conversation_history) < 5 else "detailed_discussion",
            "questions_answered": len(self.conversation_history),
            "remaining_sections": self._get_remaining_sections(),
            "current_focus": self._get_current_focus()
        }

    def _get_previous_insights(self) -> Dict[str, Any]:
        """Gather insights from previous responses"""
        insights = {}
        for key in self.current_context:
            if key.endswith('_insight'):
                category = key.replace('_insight', '')
                insights[category] = {
                    "observation": self.current_context[key],
                    "timestamp": datetime.now().isoformat()
                }
        return insights

    def _get_interaction_summary(self) -> Dict[str, Any]:
        """Summarize the interaction so far"""
        return {
            "total_interactions": len(self.conversation_history),
            "key_topics_discussed": self._extract_key_topics(),
            "engagement_level": self._assess_engagement(),
            "response_patterns": self._analyze_response_patterns()
        }

    def _build_initial_context(self) -> Dict[str, Any]:
        """Build context for the initial interaction"""
        return {
            "interaction_type": "initial_greeting",
            "tone": "welcoming_professional",
            "objectives": [
                "establish_rapport",
                "create_trust",
                "set_expectations"
            ]
        }

    def _build_industry_context(self) -> Dict[str, Any]:
        """Build context for industry-related questions"""
        return {
            "current_industry": self.user_info.get('industry'),
            "related_sectors": self._get_related_sectors(),
            "industry_trends": self._get_industry_trends(),
            "growth_areas": self._get_growth_areas()
        }

    def _build_experience_context(self) -> Dict[str, Any]:
        """Build context for experience-related questions"""
        years = int(self.user_info.get('experience_years', 0))
        stage = "entry_level" if years < 2 else \
                "early_career" if years < 5 else \
                "mid_career" if years < 10 else \
                "senior"
        return {
            "years": years,
            "stage": stage,
            "typical_roles": self._get_typical_roles_for_experience(years),
            "development_priorities": self._get_development_priorities(years, stage)
        }

    def _build_education_context(self) -> Dict[str, Any]:
        """Build context for education-related questions"""
        education = self.user_info.get('education', '').lower()
        return {
            "education_level": self._determine_education_level(education),
            "field_of_study": self._determine_field_of_study(education),
            "typical_roles": self._get_typical_roles_for_education(education),
            "development_recommendations": self._get_education_recommendations(education)
        }

    async def _build_role_context(self) -> Dict[str, Any]:
        """Build context for role-related questions"""
        return {
            "career_stage": await self._infer_career_stage(),
            "industry_context": self._build_industry_context(),
            "role_progression": self._get_role_progression_path(),
            "market_trends": self._get_market_trends()
        }

    async def _infer_career_stage(self) -> Dict[str, Any]:
        """Sophisticated career stage inference based on multiple factors"""
        # Gather all relevant information
        info = {
            "experience": self._analyze_experience(),
            "role_progression": self._analyze_role_progression(),
            "skills_maturity": self._analyze_skills_maturity(),
            "leadership_indicators": self._analyze_leadership_indicators(),
            "career_trajectory": self._analyze_career_trajectory()
        }
        
        # Get Claude's analysis of career stage
        return await self._get_career_stage_analysis(info)

    def _analyze_experience(self) -> Dict[str, Any]:
        """Analyze experience-related questions"""
        years = int(self.user_info.get('experience_years', 0))
        
        # Determine career stage based on years
        if years < 2:
            stage = "entry_level"
            stage_description = "Early career professional focusing on skill development"
        elif years < 5:
            stage = "early_career"
            stage_description = "Building foundational experience and expertise"
        elif years < 10:
            stage = "mid_career"
            stage_description = "Established professional with solid experience"
        else:
            stage = "senior"
            stage_description = "Senior professional with extensive experience"
        
        # Calculate typical progression milestones
        milestones = {
            "next_role_timeline": "6-12 months" if years < 2 else
                                 "1-2 years" if years < 5 else
                                 "2-3 years",
            "skill_development_phase": "foundational" if years < 2 else
                                     "intermediate" if years < 5 else
                                     "advanced" if years < 10 else
                                     "expert",
            "leadership_track": "individual contributor" if years < 3 else
                              "team lead potential" if years < 7 else
                              "leadership track"
        }
        
        # Identify peer comparison and market position
        market_position = {
            "experience_percentile": self._calculate_experience_percentile(years),
            "typical_roles": self._get_typical_roles_for_experience(years),
            "market_demand": self._assess_market_demand_for_experience(years),
            "competitive_advantages": self._identify_competitive_advantages(years)
        }
        
        return {
            "years_experience": years,
            "career_stage": stage,
            "stage_description": stage_description,
            "progression_milestones": milestones,
            "market_position": market_position,
            "development_priorities": self._get_development_priorities(years, stage)
        }

    def _calculate_experience_percentile(self, years: int) -> str:
        """Calculate experience percentile based on industry averages"""
        if years < 2:
            return "0-25th"
        elif years < 5:
            return "25-50th"
        elif years < 10:
            return "50-75th"
        else:
            return "75-100th"

    def _get_typical_roles_for_experience(self, years: int) -> List[str]:
        """Get typical roles for the given years of experience"""
        if years < 2:
            return ["Junior Professional", "Associate", "Entry-level Specialist"]
        elif years < 5:
            return ["Professional", "Senior Associate", "Specialist"]
        elif years < 10:
            return ["Senior Professional", "Team Lead", "Manager", "Senior Specialist"]
        else:
            return ["Principal", "Director", "Senior Manager", "Expert"]

    def _assess_market_demand_for_experience(self, years: int) -> Dict[str, Any]:
        """Assess market demand for the experience level"""
        if years < 2:
            return {
                "demand_level": "high",
                "competition_level": "high",
                "growth_opportunities": "abundant",
                "market_dynamics": "entry-level positions with strong learning curve"
            }
        elif years < 5:
            return {
                "demand_level": "very_high",
                "competition_level": "moderate",
                "growth_opportunities": "significant",
                "market_dynamics": "sweet spot for career advancement"
            }
        elif years < 10:
            return {
                "demand_level": "high",
                "competition_level": "moderate",
                "growth_opportunities": "specialized",
                "market_dynamics": "leadership and expert positions"
            }
        else:
            return {
                "demand_level": "selective",
                "competition_level": "low",
                "growth_opportunities": "strategic",
                "market_dynamics": "executive and strategic positions"
            }

    def _identify_competitive_advantages(self, years: int) -> List[str]:
        """Identify competitive advantages based on experience"""
        advantages = []
        
        if years < 2:
            advantages = [
                "Fresh perspective",
                "Up-to-date technical knowledge",
                "Adaptability",
                "Strong learning potential"
            ]
        elif years < 5:
            advantages = [
                "Balanced technical and practical experience",
                "Proven track record",
                "Established work methodologies",
                "Growing professional network"
            ]
        elif years < 10:
            advantages = [
                "Deep domain expertise",
                "Leadership experience",
                "Strong professional network",
                "Project management skills"
            ]
        else:
            advantages = [
                "Strategic thinking",
                "Executive presence",
                "Industry influence",
                "Extensive network",
                "Crisis management experience"
            ]
        
        return advantages

    def _get_development_priorities(self, years: int, stage: str) -> List[Dict[str, Any]]:
        """Get development priorities based on experience and career stage"""
        if stage == "entry_level":
            return [
                {
                    "area": "Technical Skills",
                    "priority": "high",
                    "focus": "Building foundational skills and best practices"
                },
                {
                    "area": "Professional Development",
                    "priority": "high",
                    "focus": "Understanding industry standards and workflows"
                },
                {
                    "area": "Soft Skills",
                    "priority": "medium",
                    "focus": "Developing communication and teamwork abilities"
                }
            ]
        elif stage == "early_career":
            return [
                {
                    "area": "Technical Expertise",
                    "priority": "high",
                    "focus": "Deepening knowledge in specific areas"
                },
                {
                    "area": "Project Management",
                    "priority": "medium",
                    "focus": "Taking ownership of small to medium projects"
                },
                {
                    "area": "Leadership Skills",
                    "priority": "medium",
                    "focus": "Mentoring juniors and leading small teams"
                }
            ]
        elif stage == "mid_career":
            return [
                {
                    "area": "Leadership",
                    "priority": "high",
                    "focus": "Developing strategic thinking and team management"
                },
                {
                    "area": "Business Acumen",
                    "priority": "high",
                    "focus": "Understanding broader business impact"
                },
                {
                    "area": "Specialization",
                    "priority": "medium",
                    "focus": "Becoming a recognized expert in key areas"
                }
            ]
        else:  # senior
            return [
                {
                    "area": "Strategic Leadership",
                    "priority": "high",
                    "focus": "Driving organizational change and innovation"
                },
                {
                    "area": "Industry Influence",
                    "priority": "high",
                    "focus": "Building thought leadership and industry presence"
                },
                {
                    "area": "Executive Skills",
                    "priority": "high",
                    "focus": "Developing executive presence and strategic vision"
                }
            ]

    async def _show_personalized_response(self, key: str, response: str):
        """Get personalized response from Claude based on user input"""
        cache_key = f"{key}_{response.lower().strip()}"
        cached_response = self.response_cache.get(cache_key)
        
        if cached_response:
            print(f"\n{cached_response}.")
            self.current_context[f"{key}_insight"] = cached_response
            return

        # Build rich context
        context = await self._build_context(key)
        
        prompt = f"""
        You are a Principal at Principals Network, specializing in career development and guidance.
        
        Current Context:
        {json.dumps(context, indent=2)}
        
        User Response: "{response}"
        Question Type: {key}
        
        Based on this context, provide a personalized, insightful response that:
        1. Shows deep understanding of the user's situation
        2. Connects their response to broader career implications
        3. Demonstrates expertise in career development
        4. Provides forward-looking perspective
        
        Additional Guidelines:
        - Keep response to one impactful sentence
        - Be specific and actionable
        - Show understanding of current market dynamics
        - Maintain professional but encouraging tone
        - Base insights on latest industry trends and data
        
        Format: Provide a single, well-crafted sentence that captures key insights and next steps.
        """

        try:
            first_principal = list(self.principals.values())[0]
            response_text = await first_principal.claude.get_response(
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            cleaned_response = response_text.strip().rstrip('.')
            print(f"\n{cleaned_response}.")
            
            # Cache and store the response
            self.response_cache.set(cache_key, cleaned_response)
            self.current_context[f"{key}_insight"] = cleaned_response
            
            # Update conversation context
            self._update_conversation_context(key, cleaned_response)
            
        except Exception as e:
            self.logger.error(f"Error generating personalized response: {e}")
            print(f"\nThank you for sharing that information.")

    def _update_conversation_context(self, key: str, insight: str):
        """Update the conversation context with new insights"""
        if 'insights_progression' not in self.current_context:
            self.current_context['insights_progression'] = []
            
        self.current_context['insights_progression'].append({
            'timestamp': datetime.now().isoformat(),
            'question_type': key,
            'insight': insight,
            'conversation_stage': self._get_conversation_stage()
        })

    def _format_previous_insights(self) -> str:
        """Format previous insights for context"""
        insights = []
        for key in ['name_insight', 'current_role_insight', 'industry_insight', 
                   'experience_years_insight', 'education_insight']:
            if key in self.current_context:
                insights.append(f"- {key.replace('_insight', '')}: {self.current_context[key]}")
        return "\n".join(insights)

    def _get_experience_response(self, years: int) -> str:
        """Get personalized response based on years of experience"""
        if years < 2:
            return "Starting your career journey! This is an exciting time to shape your path."
        elif years < 5:
            return "You've built a good foundation. Let's focus on accelerating your growth."
        elif years < 10:
            return "You bring solid experience. We'll explore ways to leverage and expand your expertise."
        else:
            return "Your extensive experience is valuable. Let's focus on strategic career moves and leadership opportunities."

    def _show_current_answers(self):
        """Show current answers for review"""
        print("\n=== Current Answers ===")
        print("\nBasic Information:")
        for key, value in self.user_info.items():
            print(f"{key}: {value}")
        
        print("\nInterview Responses:")
        for entry in self.conversation_history:
            if entry.get("phase") == "interview":
                print(f"\n{entry['section']} - {entry['question']}")
                print(f"Answer: {entry['response']}")

    async def _generate_report_section(self, section: str) -> str:
        """Generate a specific section of the career roadmap"""
        prompt = f"""
        Based on the consensus and discussion:
        {json.dumps(self.current_context.get('consensus', {}), indent=2)}
        
        Generate the {section} section of the career roadmap.
        Make it detailed, actionable, and specific to the user's profile.
        """
        
        try:
            first_principal = list(self.principals.values())[0]
            return await first_principal.claude.get_response(
                messages=[{"role": "user", "content": prompt}]
            )
        except Exception as e:
            self.logger.error(f"Error generating report section: {e}")
            return f"Unable to generate {section}"

    async def _present_career_roadmap(self, report: Dict):
        """Present the career roadmap to the user"""
        print("\n=== Your Personalized Career Roadmap ===")
        for section, content in report.items():
            print(f"\n{section}")
            print("=" * len(section))
            print(content)
            
    def _analyze_response_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in user responses and interaction"""
        return {
            "response_characteristics": self._analyze_response_characteristics(),
            "topic_interests": self._analyze_topic_interests(),
            "confidence_indicators": self._analyze_confidence_patterns(),
            "growth_mindset": self._assess_growth_mindset(),
            "decision_patterns": self._analyze_decision_patterns()
        }

    def _analyze_response_characteristics(self) -> Dict[str, Any]:
        """Analyze characteristics of user responses"""
        responses = [entry["response"] for entry in self.conversation_history]
        
        return {
            "average_length": sum(len(r) for r in responses) / len(responses) if responses else 0,
            "detail_level": self._assess_detail_level(responses),
            "communication_style": self._identify_communication_style(responses),
            "key_themes": self._extract_recurring_themes(responses),
            "emotional_indicators": self._analyze_emotional_tone(responses)
        }

    def _analyze_topic_interests(self) -> Dict[str, Any]:
        """Analyze which topics generate more engagement"""
        topic_engagement = {}
        
        for entry in self.conversation_history:
            section = entry.get("section", "")
            response = entry.get("response", "")
            
            if section:
                if section not in topic_engagement:
                    topic_engagement[section] = {
                        "response_count": 0,
                        "avg_response_length": 0,
                        "detailed_responses": 0,
                        "enthusiasm_indicators": 0
                    }
                
                topic_engagement[section]["response_count"] += 1
                topic_engagement[section]["avg_response_length"] += len(response)
                topic_engagement[section]["detailed_responses"] += 1 if len(response.split()) > 20 else 0
                topic_engagement[section]["enthusiasm_indicators"] += self._count_enthusiasm_indicators(response)

        # Normalize the metrics
        for section in topic_engagement:
            count = topic_engagement[section]["response_count"]
            if count > 0:
                topic_engagement[section]["avg_response_length"] /= count

        return {
            "topic_engagement": topic_engagement,
            "high_interest_areas": self._identify_high_interest_areas(topic_engagement),
            "engagement_progression": self._analyze_engagement_progression()
        }

    def _analyze_confidence_patterns(self) -> Dict[str, Any]:
        """Analyze confidence indicators in responses"""
        confidence_indicators = {
            "high": ["definitely", "absolutely", "confident", "sure", "expert", "strong"],
            "medium": ["think", "believe", "probably", "likely", "somewhat"],
            "low": ["maybe", "not sure", "might", "possibly", "try"]
        }
        
        confidence_scores = []
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            score = 0
            
            for level, indicators in confidence_indicators.items():
                count = sum(1 for ind in indicators if ind in response)
                if level == "high":
                    score += count * 2
                elif level == "medium":
                    score += count
                else:
                    score -= count
                    
            confidence_scores.append(score)

        return {
            "confidence_progression": confidence_scores,
            "overall_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "confidence_by_topic": self._analyze_confidence_by_topic(),
            "areas_of_uncertainty": self._identify_uncertainty_areas()
        }

    def _assess_growth_mindset(self) -> Dict[str, Any]:
        """Assess indicators of growth mindset vs fixed mindset"""
        growth_indicators = {
            "learning_focus": self._analyze_learning_references(),
            "challenge_attitude": self._analyze_challenge_attitude(),
            "development_orientation": self._analyze_development_focus(),
            "feedback_receptivity": self._assess_feedback_mentions()
        }
        
        return {
            "indicators": growth_indicators,
            "overall_orientation": self._calculate_growth_orientation(growth_indicators),
            "development_areas": self._identify_development_interests(),
            "learning_preferences": self._analyze_learning_preferences()
        }

    def _analyze_decision_patterns(self) -> Dict[str, Any]:
        """Analyze decision-making patterns in responses"""
        return {
            "decision_style": self._identify_decision_style(),
            "risk_attitude": self._assess_risk_attitude(),
            "time_orientation": self._analyze_time_perspective(),
            "change_readiness": self._assess_change_readiness()
        }

    def _count_enthusiasm_indicators(self, response: str) -> int:
        """Count indicators of enthusiasm in a response"""
        indicators = ["!", "excited", "love", "passionate", "enjoy", "interested"]
        return sum(1 for ind in indicators if ind.lower() in response.lower())

    def _identify_high_interest_areas(self, topic_engagement: Dict) -> List[str]:
        """Identify topics with highest engagement"""
        scored_topics = [
            (topic, data["avg_response_length"] * 0.3 +
                    data["enthusiasm_indicators"] * 0.4 +
                    data["detailed_responses"] * 0.3)
            for topic, data in topic_engagement.items()
        ]
        
        return [topic for topic, score in sorted(scored_topics, key=lambda x: x[1], reverse=True)]

    def _analyze_engagement_progression(self) -> Dict[str, Any]:
        """Analyze how engagement changes throughout the conversation"""
        responses = [entry.get("response", "") for entry in self.conversation_history]
        
        engagement_metrics = []
        window_size = 3
        
        for i in range(len(responses) - window_size + 1):
            window = responses[i:i + window_size]
            metrics = {
                "avg_length": sum(len(r) for r in window) / window_size,
                "detail_level": self._assess_detail_level(window),
                "enthusiasm": sum(self._count_enthusiasm_indicators(r) for r in window)
            }
            engagement_metrics.append(metrics)

        return {
            "progression": engagement_metrics,
            "trend": self._calculate_engagement_trend(engagement_metrics),
            "peak_engagement_points": self._identify_peak_engagement(engagement_metrics)
        }

    async def _get_career_stage_analysis(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Get Claude's analysis of career stage"""
        prompt = f"""
        As a career development expert, analyze this professional's career stage based on:

        Detailed Information:
        {json.dumps(info, indent=2)}

        User Profile:
        - Current Role: {self.user_info.get('current_role')}
        - Experience: {self.user_info.get('experience_years')} years
        - Education: {self.user_info.get('education')}
        - Industry: {self.user_info.get('industry')}

        Provide a comprehensive career stage analysis in this JSON format:
        {{
            "career_stage": "early_career|mid_career|senior|executive|expert",
            "stage_characteristics": [],
            "development_phase": "building|advancing|transitioning|leading",
            "progression_indicators": [],
            "next_stage_requirements": [],
            "career_velocity": "accelerating|steady|plateaued",
            "stage_specific_opportunities": [],
            "risk_factors": [],
            "advancement_timeline": "immediate|6_months|1_year|2_plus_years",
            "stage_appropriate_roles": []
        }}

        Base the analysis on:
        1. Role complexity and scope
        2. Leadership and influence
        3. Technical/domain expertise
        4. Strategic impact
        5. Career velocity
        """

        try:
            first_principal = list(self.principals.values())[0]
            response = await first_principal.claude.get_response(
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in career stage analysis: {e}")
            return self._get_fallback_career_stage()

    def _get_fallback_career_stage(self) -> Dict[str, Any]:
        """Fallback career stage determination if API fails"""
        years = int(self.user_info.get('experience_years', 0))
        
        if years < 3:
            stage = "early_career"
        elif years < 8:
            stage = "mid_career"
        elif years < 15:
            stage = "senior"
        else:
            stage = "executive"
            
        return {
            "career_stage": stage,
            "development_phase": "building" if stage == "early_career" else "advancing",
            "career_velocity": "steady",
            "stage_specific_opportunities": [],
            "risk_factors": []
        }

    def _assess_role_complexity(self) -> str:
        """Assess complexity of current role"""
        role = self.user_info.get('current_role', '').lower()
        responses = [entry["response"] for entry in self.conversation_history]
        
        # Look for complexity indicators in responses
        complexity_indicators = {
            "high": ["strategic", "complex", "enterprise", "global", "architecture"],
            "medium": ["lead", "manage", "coordinate", "design", "develop"],
            "low": ["support", "assist", "maintain", "operate"]
        }
        
        scores = {level: 0 for level in complexity_indicators}
        for level, indicators in complexity_indicators.items():
            for indicator in indicators:
                if indicator in role:
                    scores[level] += 2
                for response in responses:
                    if indicator in response.lower():
                        scores[level] += 1
                        
        return max(scores.items(), key=lambda x: x[1])[0]

    def _assess_impact_scope(self) -> str:
        """Assess scope of impact in current role"""
        responses = [entry["response"] for entry in self.conversation_history]
        
        scope_indicators = {
            "global": ["global", "enterprise", "company-wide", "organization-wide"],
            "department": ["department", "team", "unit", "division"],
            "individual": ["individual", "personal", "own", "direct"]
        }
        
        scores = {scope: 0 for scope in scope_indicators}
        for scope, indicators in scope_indicators.items():
            for indicator in indicators:
                for response in responses:
                    if indicator in response.lower():
                        scores[scope] += 1
                        
        return max(scores.items(), key=lambda x: x[1])[0]

    def _get_remaining_sections(self) -> List[str]:
        """Get remaining interview sections"""
        all_sections = [
            "Basic Information",
            "Career Vision",
            "Skills & Experience",
            "Values & Preferences"
        ]
        
        # Get sections that have been covered
        covered_sections = set()
        for entry in self.conversation_history:
            if "section" in entry:
                covered_sections.add(entry["section"])
                
        return [section for section in all_sections if section not in covered_sections]

    def _get_current_focus(self) -> str:
        """Get the current focus of the conversation"""
        if not self.conversation_history:
            return "gathering_basic_info"
            
        last_entry = self.conversation_history[-1]
        if "section" in last_entry:
            return f"discussing_{last_entry['section'].lower().replace(' ', '_')}"
        
        return "transitioning_between_sections"

    def _extract_key_topics(self) -> List[str]:
        """Extract key topics from conversation history"""
        topics = set()
        for entry in self.conversation_history:
            if "section" in entry:
                topics.add(entry["section"])
        return list(topics)

    def _assess_engagement(self) -> str:
        """Assess user engagement level"""
        if not self.conversation_history:
            return "initial"
            
        responses = [entry.get("response", "") for entry in self.conversation_history]
        avg_length = sum(len(r) for r in responses) / len(responses) if responses else 0
        
        if avg_length > 100:
            return "high"
        elif avg_length > 50:
            return "medium"
        else:
            return "low"

    def _assess_detail_level(self, responses: List[str]) -> str:
        """Assess the level of detail in responses"""
        if not responses:
            return "unknown"
            
        avg_words = sum(len(r.split()) for r in responses) / len(responses)
        
        if avg_words > 30:
            return "high"
        elif avg_words > 15:
            return "medium"
        else:
            return "low"

    def _identify_communication_style(self, responses: List[str]) -> str:
        """Identify user's communication style"""
        if not responses:
            return "unknown"
            
        # Simple analysis of communication style
        technical_terms = ["technical", "system", "process", "analyze"]
        narrative_terms = ["feel", "think", "believe", "want"]
        
        technical_count = sum(1 for r in responses for term in technical_terms if term in r.lower())
        narrative_count = sum(1 for r in responses for term in narrative_terms if term in r.lower())
        
        if technical_count > narrative_count:
            return "analytical"
        elif narrative_count > technical_count:
            return "narrative"
        else:
            return "balanced"

    def _extract_recurring_themes(self, responses: List[str]) -> List[str]:
        """Extract recurring themes from responses"""
        # This would be better with NLP, but here's a simple version
        common_themes = {
            "technology": ["tech", "software", "digital", "data"],
            "leadership": ["lead", "manage", "direct", "guide"],
            "innovation": ["innovate", "create", "develop", "design"],
            "growth": ["learn", "grow", "improve", "develop"]
        }
        
        found_themes = []
        for theme, keywords in common_themes.items():
            if any(any(keyword in r.lower() for keyword in keywords) for r in responses):
                found_themes.append(theme)
                
        return found_themes

    def _analyze_emotional_tone(self, responses: List[str]) -> Dict[str, int]:
        """Analyze emotional tone of responses"""
        tone_indicators = {
            "positive": ["excited", "happy", "great", "love", "enjoy"],
            "neutral": ["think", "believe", "consider", "maybe"],
            "cautious": ["concerned", "worried", "unsure", "perhaps"]
        }
        
        tone_scores = {tone: 0 for tone in tone_indicators}
        for tone, indicators in tone_indicators.items():
            for response in responses:
                tone_scores[tone] += sum(1 for ind in indicators if ind in response.lower())
                
        return tone_scores

    def _calculate_engagement_trend(self, metrics: List[Dict]) -> str:
        """Calculate the trend in engagement over time"""
        if not metrics:
            return "stable"
            
        # Calculate trend based on average length and enthusiasm
        length_scores = [m["avg_length"] for m in metrics]
        enthusiasm_scores = [m["enthusiasm"] for m in metrics]
        
        # Calculate slopes
        length_trend = self._calculate_slope(length_scores)
        enthusiasm_trend = self._calculate_slope(enthusiasm_scores)
        
        # Determine overall trend
        if length_trend > 0.1 and enthusiasm_trend > 0:
            return "increasing"
        elif length_trend < -0.1 and enthusiasm_trend < 0:
            return "decreasing"
        else:
            return "stable"

    def _calculate_slope(self, values: List[float]) -> float:
        """Calculate the slope of a trend line"""
        if len(values) < 2:
            return 0
            
        x = list(range(len(values)))
        x_mean = sum(x) / len(x)
        y_mean = sum(values) / len(values)
        
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
        denominator = sum((xi - x_mean) ** 2 for xi in x)
        
        return numerator / denominator if denominator != 0 else 0

    def _identify_peak_engagement(self, metrics: List[Dict]) -> List[int]:
        """Identify points of peak engagement"""
        if not metrics:
            return []
            
        # Calculate composite engagement score for each point
        scores = []
        for metric in metrics:
            detail_score = 10 if metric["detail_level"] == "high" else 5 if metric["detail_level"] == "medium" else 0
            score = metric["avg_length"] * 0.4 + metric["enthusiasm"] * 0.4 + detail_score * 0.2
            scores.append(score)
            
        # Find local maxima
        peaks = []
        for i in range(1, len(scores) - 1):
            if scores[i] > scores[i-1] and scores[i] > scores[i+1]:
                peaks.append(i)
                
        return peaks

    def _analyze_confidence_by_topic(self) -> Dict[str, str]:
        """Analyze confidence levels by topic"""
        topic_confidence = {}
        
        for entry in self.conversation_history:
            if "section" not in entry:
                continue
                
            section = entry["section"]
            response = entry.get("response", "").lower()
            
            # Count confidence indicators
            high_confidence = sum(1 for term in ["definitely", "absolutely", "confident", "sure"] 
                                if term in response)
            low_confidence = sum(1 for term in ["maybe", "not sure", "might", "possibly"] 
                               if term in response)
            
            if high_confidence > low_confidence:
                confidence = "high"
            elif low_confidence > high_confidence:
                confidence = "low"
            else:
                confidence = "medium"
                
            topic_confidence[section] = confidence
            
        return topic_confidence

    def _identify_uncertainty_areas(self) -> List[str]:
        """Identify areas where the user shows uncertainty"""
        uncertainty_areas = []
        uncertainty_indicators = ["unsure", "not certain", "don't know", "unclear", "confused"]
        
        for entry in self.conversation_history:
            if "section" not in entry:
                continue
                
            response = entry.get("response", "").lower()
            if any(indicator in response for indicator in uncertainty_indicators):
                uncertainty_areas.append(entry["section"])
                
        return list(set(uncertainty_areas))

    def _analyze_learning_references(self) -> Dict[str, Any]:
        """Analyze references to learning and development in responses"""
        learning_indicators = {
            "active_learning": ["learn", "study", "training", "course", "education"],
            "self_development": ["improve", "grow", "develop", "progress", "advance"],
            "skill_building": ["practice", "master", "skill", "expertise", "proficiency"]
        }
        
        scores = {category: 0 for category in learning_indicators}
        contexts = {category: [] for category in learning_indicators}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for category, indicators in learning_indicators.items():
                for indicator in indicators:
                    if indicator in response:
                        scores[category] += 1
                        # Store context around the learning reference
                        contexts[category].append({
                            "indicator": indicator,
                            "section": entry.get("section", "unknown"),
                            "context": response
                        })
        
        return {
            "learning_focus_scores": scores,
            "learning_contexts": contexts,
            "overall_learning_orientation": "high" if sum(scores.values()) > 5 else 
                                         "medium" if sum(scores.values()) > 2 else "low"
        }

    def _analyze_challenge_attitude(self) -> Dict[str, Any]:
        """Analyze attitude towards challenges and difficult situations"""
        challenge_indicators = {
            "positive": ["challenge", "opportunity", "learn from", "overcome", "solve"],
            "growth": ["improve", "develop", "progress", "adapt", "change"],
            "resilience": ["persist", "try again", "bounce back", "keep going", "despite"]
        }
        
        attitude_scores = {category: 0 for category in challenge_indicators}
        evidence = {category: [] for category in challenge_indicators}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for category, indicators in challenge_indicators.items():
                for indicator in indicators:
                    if indicator in response:
                        attitude_scores[category] += 1
                        evidence[category].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        total_score = sum(attitude_scores.values())
        return {
            "attitude_scores": attitude_scores,
            "supporting_evidence": evidence,
            "overall_challenge_orientation": "positive" if total_score > 4 else 
                                          "neutral" if total_score > 2 else "cautious"
        }

    def _analyze_development_focus(self) -> Dict[str, Any]:
        """Analyze focus on personal and professional development"""
        development_areas = {
            "technical_skills": ["technical", "skills", "tools", "technology", "programming"],
            "soft_skills": ["communication", "leadership", "teamwork", "interpersonal"],
            "domain_knowledge": ["industry", "domain", "field", "sector", "market"],
            "career_growth": ["promotion", "advance", "career", "position", "role"]
        }
        
        focus_scores = {area: 0 for area in development_areas}
        development_mentions = {area: [] for area in development_areas}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for area, indicators in development_areas.items():
                for indicator in indicators:
                    if indicator in response:
                        focus_scores[area] += 1
                        development_mentions[area].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        # Calculate primary and secondary focus areas
        sorted_areas = sorted(focus_scores.items(), key=lambda x: x[1], reverse=True)
        primary_focus = sorted_areas[0][0] if sorted_areas else None
        secondary_focus = sorted_areas[1][0] if len(sorted_areas) > 1 else None
        
        return {
            "focus_scores": focus_scores,
            "development_mentions": development_mentions,
            "primary_focus": primary_focus,
            "secondary_focus": secondary_focus,
            "development_breadth": len([s for s in focus_scores.values() if s > 0])
        }

    def _assess_feedback_mentions(self) -> Dict[str, Any]:
        """Assess mentions and attitudes towards feedback and learning from others"""
        feedback_indicators = {
            "seeking_feedback": ["feedback", "advice", "guidance", "mentor", "learn from"],
            "openness": ["open to", "willing to", "appreciate", "value", "welcome"],
            "application": ["apply", "implement", "incorporate", "use", "based on"]
        }
        
        feedback_scores = {category: 0 for category in feedback_indicators}
        feedback_examples = {category: [] for category in feedback_indicators}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for category, indicators in feedback_indicators.items():
                for indicator in indicators:
                    if indicator in response:
                        feedback_scores[category] += 1
                        feedback_examples[category].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        total_feedback_score = sum(feedback_scores.values())
        return {
            "feedback_scores": feedback_scores,
            "feedback_examples": feedback_examples,
            "feedback_receptivity": "high" if total_feedback_score > 4 else 
                                  "medium" if total_feedback_score > 2 else "low"
        }

    def _calculate_growth_orientation(self, indicators: Dict[str, Any]) -> str:
        """Calculate overall growth orientation based on multiple indicators"""
        # Extract scores from each area
        learning_score = 2 if indicators["learning_focus"]["overall_learning_orientation"] == "high" else \
                        1 if indicators["learning_focus"]["overall_learning_orientation"] == "medium" else 0
                        
        challenge_score = 2 if indicators["challenge_attitude"]["overall_challenge_orientation"] == "positive" else \
                         1 if indicators["challenge_attitude"]["overall_challenge_orientation"] == "neutral" else 0
                         
        development_score = indicators["development_orientation"]["development_breadth"] / 2  # Normalize to 0-2 range
        
        feedback_score = 2 if indicators["feedback_receptivity"]["feedback_receptivity"] == "high" else \
                        1 if indicators["feedback_receptivity"]["feedback_receptivity"] == "medium" else 0
        
        total_score = learning_score + challenge_score + development_score + feedback_score
        max_possible_score = 8  # Sum of maximum possible scores from all areas
        
        # Calculate percentage and determine orientation
        growth_percentage = (total_score / max_possible_score) * 100
        
        if growth_percentage >= 75:
            return "strong_growth"
        elif growth_percentage >= 50:
            return "moderate_growth"
        elif growth_percentage >= 25:
            return "emerging_growth"
        else:
            return "fixed"

    def _identify_development_interests(self) -> List[Dict[str, Any]]:
        """Identify specific areas of development interest"""
        development_mentions = []
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            section = entry.get("section", "unknown")
            
            # Look for phrases indicating development interests
            interest_indicators = [
                "want to learn", "interested in", "would like to", 
                "plan to", "hope to", "aspire to"
            ]
            
            for indicator in interest_indicators:
                if indicator in response:
                    # Get the context around the indicator
                    start_idx = response.find(indicator)
                    context = response[max(0, start_idx-30):min(len(response), start_idx+50)]
                    
                    development_mentions.append({
                        "interest": context.strip(),
                        "section": section,
                        "confidence": "high" if "definitely" in response or "really" in response else "medium"
                    })
        
        return development_mentions

    def _analyze_learning_preferences(self) -> Dict[str, Any]:
        """Analyze preferred learning methods and styles"""
        learning_styles = {
            "hands_on": ["practice", "experience", "doing", "hands-on", "build"],
            "theoretical": ["study", "theory", "understand", "concept", "principle"],
            "collaborative": ["team", "group", "peer", "together", "collaborate"],
            "self_directed": ["self", "independent", "own pace", "personal", "individual"]
        }
        
        style_scores = {style: 0 for style in learning_styles}
        style_evidence = {style: [] for style in learning_styles}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for style, indicators in learning_styles.items():
                for indicator in indicators:
                    if indicator in response:
                        style_scores[style] += 1
                        style_evidence[style].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        # Determine primary and secondary learning styles
        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
        primary_style = sorted_styles[0][0] if sorted_styles else None
        secondary_style = sorted_styles[1][0] if len(sorted_styles) > 1 else None
        
        return {
            "style_scores": style_scores,
            "style_evidence": style_evidence,
            "primary_style": primary_style,
            "secondary_style": secondary_style,
            "learning_flexibility": len([s for s in style_scores.values() if s > 0])
        }

    def _identify_decision_style(self) -> Dict[str, Any]:
        """Identify user's decision-making style"""
        decision_indicators = {
            "analytical": ["analyze", "consider", "evaluate", "research", "data"],
            "intuitive": ["feel", "sense", "believe", "think", "gut"],
            "collaborative": ["discuss", "consult", "team", "together", "others"],
            "directive": ["decide", "know", "certain", "clear", "must"]
        }
        
        style_scores = {style: 0 for style in decision_indicators}
        style_evidence = {style: [] for style in decision_indicators}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for style, indicators in decision_indicators.items():
                for indicator in indicators:
                    if indicator in response:
                        style_scores[style] += 1
                        style_evidence[style].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        # Determine primary and secondary styles
        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
        primary_style = sorted_styles[0][0] if sorted_styles else None
        secondary_style = sorted_styles[1][0] if len(sorted_styles) > 1 else None
        
        return {
            "style_scores": style_scores,
            "style_evidence": style_evidence,
            "primary_style": primary_style,
            "secondary_style": secondary_style,
            "style_flexibility": len([s for s in style_scores.values() if s > 0])
        }

    def _assess_risk_attitude(self) -> Dict[str, Any]:
        """Assess attitude towards risk and uncertainty"""
        risk_indicators = {
            "risk_seeking": ["opportunity", "challenge", "new", "change", "innovative"],
            "risk_neutral": ["balance", "moderate", "consider", "evaluate", "assess"],
            "risk_averse": ["careful", "cautious", "safe", "secure", "stable"]
        }
        
        attitude_scores = {attitude: 0 for attitude in risk_indicators}
        evidence = {attitude: [] for attitude in risk_indicators}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for attitude, indicators in risk_indicators.items():
                for indicator in indicators:
                    if indicator in response:
                        attitude_scores[attitude] += 1
                        evidence[attitude].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        # Determine overall risk attitude
        max_score = max(attitude_scores.values())
        dominant_attitudes = [att for att, score in attitude_scores.items() if score == max_score]
        
        return {
            "attitude_scores": attitude_scores,
            "supporting_evidence": evidence,
            "dominant_attitudes": dominant_attitudes,
            "risk_orientation": dominant_attitudes[0] if len(dominant_attitudes) == 1 else "balanced"
        }

    def _analyze_time_perspective(self) -> Dict[str, Any]:
        """Analyze time orientation in decision making"""
        time_indicators = {
            "short_term": ["immediate", "soon", "now", "current", "today"],
            "medium_term": ["months", "year", "next", "upcoming", "soon"],
            "long_term": ["future", "years", "long-term", "eventually", "vision"]
        }
        
        perspective_scores = {perspective: 0 for perspective in time_indicators}
        time_references = {perspective: [] for perspective in time_indicators}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for perspective, indicators in time_indicators.items():
                for indicator in indicators:
                    if indicator in response:
                        perspective_scores[perspective] += 1
                        time_references[perspective].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        # Calculate dominant time perspective
        total_references = sum(perspective_scores.values())
        if total_references == 0:
            primary_orientation = "balanced"
        else:
            max_score = max(perspective_scores.values())
            dominant_perspectives = [p for p, s in perspective_scores.items() if s == max_score]
            primary_orientation = dominant_perspectives[0] if len(dominant_perspectives) == 1 else "balanced"
        
        return {
            "perspective_scores": perspective_scores,
            "time_references": time_references,
            "primary_orientation": primary_orientation,
            "time_balance_score": len([s for s in perspective_scores.values() if s > 0])
        }

    def _assess_change_readiness(self) -> Dict[str, Any]:
        """Assess readiness and attitude towards change"""
        change_indicators = {
            "proactive": ["initiate", "lead", "drive", "create", "start"],
            "adaptive": ["adjust", "adapt", "flexible", "learn", "grow"],
            "resistant": ["prefer", "comfortable", "familiar", "stable", "traditional"]
        }
        
        readiness_scores = {category: 0 for category in change_indicators}
        change_mentions = {category: [] for category in change_indicators}
        
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for category, indicators in change_indicators.items():
                for indicator in indicators:
                    if indicator in response:
                        readiness_scores[category] += 1
                        change_mentions[category].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        # Calculate overall change readiness
        proactive_adaptive_score = readiness_scores["proactive"] + readiness_scores["adaptive"]
        resistant_score = readiness_scores["resistant"]
        
        if proactive_adaptive_score > resistant_score * 2:
            readiness_level = "high"
        elif proactive_adaptive_score > resistant_score:
            readiness_level = "moderate"
        else:
            readiness_level = "low"
        
        return {
            "readiness_scores": readiness_scores,
            "change_mentions": change_mentions,
            "readiness_level": readiness_level,
            "change_orientation": "proactive" if readiness_scores["proactive"] > readiness_scores["adaptive"]
                                else "adaptive" if readiness_scores["adaptive"] > readiness_scores["resistant"]
                                else "cautious"
        }

    def _determine_education_level(self, education: str) -> str:
        """Determine education level based on the education string"""
        education_levels = {
            "phd": ["phd", "doctorate", "doctor of"],
            "masters": ["masters", "ms", "ma", "mba", "msc"],
            "bachelors": ["bachelors", "bs", "ba", "bsc"],
            "associate": ["associate", "as", "aa"],
            "certification": ["certification", "certificate", "diploma"],
            "self_taught": ["self taught", "self-taught", "bootcamp"]
        }
        
        for level, indicators in education_levels.items():
            if any(indicator in education for indicator in indicators):
                return level
        
        return "unknown"

    def _determine_field_of_study(self, education: str) -> str:
        """Determine field of study based on the education string"""
        study_fields = {
            "computer_science": ["computer science", "cs", "software", "programming"],
            "engineering": ["engineering", "engineer"],
            "business": ["business", "management", "mba", "finance", "economics"],
            "science": ["physics", "chemistry", "biology", "mathematics", "math"],
            "arts": ["art", "design", "music", "creative"],
            "humanities": ["psychology", "sociology", "philosophy", "history"]
        }
        
        for field, indicators in study_fields.items():
            if any(indicator in education for indicator in indicators):
                return field
        
        return "unknown"

    def _get_typical_roles_for_education(self, education: str) -> List[str]:
        """Get typical roles based on education level and field"""
        roles_by_education = {
            "phd": [
                "Principal Scientist",
                "Research Director",
                "Chief Technology Officer",
                "Senior Research Scientist"
            ],
            "masters": [
                "Senior Engineer",
                "Project Manager",
                "Technical Lead",
                "Senior Analyst"
            ],
            "bachelors": [
                "Software Engineer",
                "Business Analyst",
                "Project Coordinator",
                "Development Engineer"
            ],
            "associate": [
                "Junior Developer",
                "Technical Support",
                "Associate Engineer",
                "Junior Analyst"
            ],
            "certification": [
                "Technical Specialist",
                "Support Specialist",
                "Junior Developer",
                "Technical Associate"
            ],
            "self_taught": [
                "Developer",
                "Technical Support",
                "Junior Engineer",
                "Support Specialist"
            ]
        }
        
        return roles_by_education.get(self._determine_education_level(education), ["Entry Level Professional", "Junior Specialist"])

    def _get_education_recommendations(self, education: str) -> List[Dict[str, Any]]:
        """Get education and development recommendations"""
        base_recommendations = [
            {
                "type": "formal_education",
                "recommendations": []
            },
            {
                "type": "certifications",
                "recommendations": []
            },
            {
                "type": "skill_development",
                "recommendations": []
            }
        ]
        
        # Add formal education recommendations
        if self._determine_education_level(education) in ["self_taught", "certification"]:
            base_recommendations[0]["recommendations"].append({
                "focus": "Consider formal degree program",
                "rationale": "Strengthen theoretical foundation",
                "timeline": "2-4 years"
            })
        elif self._determine_education_level(education) == "associate":
            base_recommendations[0]["recommendations"].append({
                "focus": "Bachelor's degree completion",
                "rationale": "Expand career opportunities",
                "timeline": "2-3 years"
            })
        elif self._determine_education_level(education) == "bachelors":
            base_recommendations[0]["recommendations"].append({
                "focus": "Master's degree in specialization",
                "rationale": "Deepen expertise and advance career",
                "timeline": "2-3 years"
            })
        
        # Add certification recommendations based on field
        if self._determine_field_of_study(education) == "computer_science":
            base_recommendations[1]["recommendations"].extend([
                {
                    "focus": "Cloud certifications (AWS/Azure/GCP)",
                    "rationale": "Essential for modern development",
                    "timeline": "3-6 months"
                },
                {
                    "focus": "Security certifications",
                    "rationale": "Growing importance in tech",
                    "timeline": "6-12 months"
                }
            ])
        elif self._determine_field_of_study(education) == "business":
            base_recommendations[1]["recommendations"].extend([
                {
                    "focus": "Project Management (PMP/Agile)",
                    "rationale": "Essential for career growth",
                    "timeline": "6-12 months"
                },
                {
                    "focus": "Business Analysis (CBAP)",
                    "rationale": "Enhance analytical skills",
                    "timeline": "6-12 months"
                }
            ])
        
        # Add skill development recommendations
        base_recommendations[2]["recommendations"].extend([
            {
                "focus": "Leadership and management",
                "rationale": "Essential for career advancement",
                "timeline": "Ongoing"
            },
            {
                "focus": "Latest industry trends",
                "rationale": "Stay current in field",
                "timeline": "Ongoing"
            }
        ])
        
        return base_recommendations

    def _analyze_education_skill_alignment(self, education: str) -> Dict[str, Any]:
        """Analyze alignment between education and required skills"""
        education_levels = {
            "phd": ["phd", "doctorate", "doctor of"],
            "masters": ["masters", "ms", "ma", "mba", "msc"],
            "bachelors": ["bachelors", "bs", "ba", "bsc"],
            "associate": ["associate", "as", "aa"],
            "certification": ["certification", "certificate", "diploma"],
            "self_taught": ["self taught", "self-taught", "bootcamp"]
        }
        
        study_fields = {
            "computer_science": ["computer science", "cs", "software", "programming"],
            "engineering": ["engineering", "engineer"],
            "business": ["business", "management", "mba", "finance", "economics"],
            "science": ["physics", "chemistry", "biology", "mathematics", "math"],
            "arts": ["art", "design", "music", "creative"],
            "humanities": ["psychology", "sociology", "philosophy", "history"]
        }
        
        # Identify education level and field
        education_level = "unknown"
        for level, indicators in education_levels.items():
            if any(indicator in education for indicator in indicators):
                education_level = level
                break
                
        study_field = "unknown"
        for field, indicators in study_fields.items():
            if any(indicator in education for indicator in indicators):
                study_field = field
                break
        
        # Define core skills for the field
        field_core_skills = {
            "computer_science": [
                "programming",
                "algorithms",
                "data structures",
                "software design"
            ],
            "engineering": [
                "technical design",
                "problem solving",
                "analytical thinking",
                "project management"
            ],
            "business": [
                "business analysis",
                "strategy",
                "management",
                "finance"
            ]
        }
        
        # Get core skills for the field
        core_skills = field_core_skills.get(study_field, ["professional skills", "industry knowledge"])
        
        # Analyze skill gaps
        skill_gaps = []
        if study_field in field_core_skills:
            current_skills = set(core_skills)
            required_skills = set(self._get_required_skills_for_role(self.user_info.get('current_role')))
            skill_gaps = list(required_skills - current_skills)
        
        return {
            "core_skills": core_skills,
            "skill_gaps": skill_gaps,
            "education_sufficiency": "high" if len(skill_gaps) <= 2 else "medium" if len(skill_gaps) <= 4 else "low",
            "recommended_focus_areas": skill_gaps[:3]  # Top 3 skill gaps to focus on
        }

    def _get_required_skills_for_role(self, role: str) -> List[str]:
        """Get required skills for a given role"""
        # Basic role-based skill requirements
        role_skills = {
            "developer": [
                "programming",
                "software design",
                "testing",
                "version control"
            ],
            "manager": [
                "leadership",
                "project management",
                "communication",
                "strategy"
            ],
            "analyst": [
                "data analysis",
                "problem solving",
                "reporting",
                "business understanding"
            ]
        }
        
        # Find matching role
        for key in role_skills:
            if key in role.lower():
                return role_skills[key]
        
        # Default skills for unknown roles
        return [
            "professional communication",
            "problem solving",
            "teamwork",
            "technical proficiency"
        ]

    def _analyze_leadership_indicators(self) -> Dict[str, Any]:
        """Analyze indicators of leadership experience and potential"""
        leadership_categories = {
            "direct_leadership": ["led", "managed", "directed", "supervised", "headed"],
            "indirect_leadership": ["influenced", "guided", "mentored", "coached", "facilitated"],
            "project_leadership": ["coordinated", "organized", "spearheaded", "initiated", "drove"],
            "thought_leadership": ["innovated", "strategized", "envisioned", "pioneered", "transformed"]
        }
        
        leadership_scores = {category: 0 for category in leadership_categories}
        leadership_evidence = {category: [] for category in leadership_categories}
        
        # Analyze responses for leadership indicators
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for category, indicators in leadership_categories.items():
                for indicator in indicators:
                    if indicator in response:
                        leadership_scores[category] += 1
                        leadership_evidence[category].append({
                            "context": response,
                            "section": entry.get("section", "unknown")
                        })
        
        # Calculate overall leadership level
        total_score = sum(leadership_scores.values())
        leadership_level = "high" if total_score > 6 else \
                          "medium" if total_score > 3 else \
                          "emerging"
        
        # Identify primary leadership style
        if total_score > 0:
            primary_style = max(leadership_scores.items(), key=lambda x: x[1])[0]
        else:
            primary_style = "undefined"
        
        # Analyze potential based on language and context
        potential_indicators = {
            "high": ["aspire", "goal", "vision", "future", "growth"],
            "medium": ["interested", "learning", "developing", "improving"],
            "low": ["unsure", "hesitant", "uncomfortable", "avoid"]
        }
        
        potential_scores = {level: 0 for level in potential_indicators}
        for entry in self.conversation_history:
            response = entry.get("response", "").lower()
            for level, indicators in potential_indicators.items():
                for indicator in indicators:
                    if indicator in response:
                        potential_scores[level] += 1
        
        # Determine leadership potential
        if potential_scores["high"] > potential_scores["medium"] + potential_scores["low"]:
            leadership_potential = "high"
        elif potential_scores["high"] + potential_scores["medium"] > potential_scores["low"]:
            leadership_potential = "medium"
        else:
            leadership_potential = "developing"
        
        return {
            "leadership_scores": leadership_scores,
            "leadership_evidence": leadership_evidence,
            "leadership_level": leadership_level,
            "primary_style": primary_style,
            "leadership_potential": leadership_potential,
            "development_areas": [cat for cat, score in leadership_scores.items() if score == 0],
            "strengths": [cat for cat, score in leadership_scores.items() if score > 1]
        }

    def _analyze_career_trajectory(self) -> Dict[str, Any]:
        """Analyze career trajectory based on past experiences and aspirations"""
        # This method should return a detailed analysis of the user's career path
        # It could include factors such as promotions, role changes, industry shifts, etc.
        # You can use NLP or other machine learning techniques to analyze this data
        return {
            "career_path": self.conversation_history,
            "current_role": self.user_info.get('current_role'),
            "industry": self.user_info.get('industry'),
            "aspirations": self.user_info.get('aspirations')
        }

    def _analyze_role_progression(self) -> Dict[str, Any]:
        """Analyze career progression pattern"""
        current_role = self.user_info.get('current_role', '').lower()
        
        # Define role categories and their indicators
        role_categories = {
            "leadership": ["manager", "director", "lead", "head", "chief", "supervisor"],
            "technical": ["engineer", "developer", "architect", "specialist", "analyst"],
            "strategic": ["strategist", "consultant", "advisor", "principal"],
            "operational": ["coordinator", "associate", "assistant", "support"]
        }
        
        # Analyze current role
        role_alignment = {category: any(term in current_role for term in indicators)
                         for category, indicators in role_categories.items()}
        
        # Determine role level
        level_indicators = {
            "senior": ["senior", "principal", "lead", "head", "chief"],
            "mid": ["manager", "specialist", "experienced"],
            "junior": ["junior", "associate", "assistant", "entry"]
        }
        
        role_level = next((level for level, indicators in level_indicators.items()
                          if any(ind in current_role for ind in indicators)), "mid")
        
        # Analyze progression indicators
        progression_indicators = {
            "rapid": ["fast track", "accelerated", "promoted", "advanced"],
            "steady": ["consistent", "stable", "regular"],
            "gradual": ["developing", "learning", "growing"]
        }
        
        # Analyze responses for progression indicators
        responses = [entry.get("response", "").lower() for entry in self.conversation_history]
        progression_mentions = {
            speed: sum(1 for resp in responses for ind in indicators if ind in resp)
            for speed, indicators in progression_indicators.items()
        }
        
        # Determine progression speed
        if progression_mentions["rapid"] > progression_mentions["steady"]:
            progression_speed = "rapid"
        elif progression_mentions["steady"] > progression_mentions["gradual"]:
            progression_speed = "steady"
        else:
            progression_speed = "gradual"
        
        return {
            "current_role_type": [cat for cat, aligned in role_alignment.items() if aligned],
            "role_level": role_level,
            "progression_speed": progression_speed,
            "progression_indicators": progression_mentions,
            "role_complexity": self._assess_role_complexity(),
            "scope_of_impact": self._assess_impact_scope()
        }

    def _analyze_skills_maturity(self) -> Dict[str, Any]:
        """Analyze maturity level of skills"""
        responses = [entry.get("response", "").lower() for entry in self.conversation_history]
        
        # Analyze different skill categories
        technical_skills = self._assess_technical_skills(responses)
        soft_skills = self._assess_soft_skills(responses)
        leadership_skills = self._assess_leadership_skills(responses)
        domain_expertise = self._assess_domain_expertise(responses)
        
        # Calculate overall maturity level
        skill_scores = {
            "technical": len(technical_skills.get("primary_areas", [])),
            "soft": len(soft_skills.get("strengths", [])),
            "leadership": 2 if leadership_skills.get("leadership_level") == "high" else
                        1 if leadership_skills.get("leadership_level") == "medium" else 0,
            "domain": 2 if domain_expertise.get("expertise_level") == "expert" else
                     1 if domain_expertise.get("expertise_level") == "advanced" else 0
        }
        
        total_score = sum(skill_scores.values())
        
        # Determine overall maturity level
        if total_score > 6:
            maturity_level = "expert"
        elif total_score > 4:
            maturity_level = "advanced"
        elif total_score > 2:
            maturity_level = "intermediate"
        else:
            maturity_level = "foundational"
            
        # Identify development priorities
        development_priorities = []
        if skill_scores["technical"] < 2:
            development_priorities.append("technical_skills")
        if skill_scores["soft"] < 2:
            development_priorities.append("soft_skills")
        if skill_scores["leadership"] < 1:
            development_priorities.append("leadership_skills")
        if skill_scores["domain"] < 1:
            development_priorities.append("domain_expertise")
        
        return {
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "leadership_skills": leadership_skills,
            "domain_expertise": domain_expertise,
            "overall_maturity": maturity_level,
            "skill_scores": skill_scores,
            "development_priorities": development_priorities,
            "skill_gaps": self._identify_skill_gaps(responses)
        }

    def _assess_technical_skills(self, responses: List[str]) -> Dict[str, Any]:
        """Assess technical skills mentioned in responses"""
        technical_categories = {
            "programming": ["coding", "programming", "development", "software", "engineering"],
            "data": ["analytics", "data", "analysis", "statistics", "metrics"],
            "infrastructure": ["systems", "infrastructure", "architecture", "cloud", "devops"],
            "security": ["security", "privacy", "protection", "compliance", "risk"]
        }
        
        skill_scores = {category: 0 for category in technical_categories}
        skill_mentions = {category: [] for category in technical_categories}
        
        for response in responses:
            for category, keywords in technical_categories.items():
                for keyword in keywords:
                    if keyword in response:
                        skill_scores[category] += 1
                        skill_mentions[category].append(response)
        
        return {
            "skill_scores": skill_scores,
            "skill_mentions": skill_mentions,
            "primary_areas": [cat for cat, score in skill_scores.items() if score > 1],
            "technical_level": "high" if sum(skill_scores.values()) > 8 else
                             "medium" if sum(skill_scores.values()) > 4 else
                             "basic"
        }

    def _assess_soft_skills(self, responses: List[str]) -> Dict[str, Any]:
        """Assess soft skills mentioned in responses"""
        soft_skill_categories = {
            "communication": ["communicate", "present", "explain", "write", "speak"],
            "leadership": ["lead", "guide", "mentor", "manage", "direct"],
            "collaboration": ["team", "collaborate", "work together", "partner", "coordinate"],
            "problem_solving": ["solve", "analyze", "resolve", "improve", "optimize"]
        }
        
        skill_scores = {category: 0 for category in soft_skill_categories}
        skill_evidence = {category: [] for category in soft_skill_categories}
        
        for response in responses:
            for category, indicators in soft_skill_categories.items():
                for indicator in indicators:
                    if indicator in response:
                        skill_scores[category] += 1
                        skill_evidence[category].append(response)
        
        return {
            "skill_scores": skill_scores,
            "skill_evidence": skill_evidence,
            "strengths": [cat for cat, score in skill_scores.items() if score > 1],
            "development_areas": [cat for cat, score in skill_scores.items() if score == 0]
        }

    def _assess_domain_expertise(self, responses: List[str]) -> Dict[str, Any]:
        """Assess domain-specific expertise"""
        current_role = self.user_info.get('current_role', '').lower()
        industry = self.user_info.get('industry', '').lower()
        
        # Extract domain-specific keywords
        domain_keywords = set()
        if current_role:
            domain_keywords.update(current_role.split())
        if industry:
            domain_keywords.update(industry.split())
        
        expertise_mentions = []
        context_mentions = []
        
        for response in responses:
            for keyword in domain_keywords:
                if keyword in response:
                    expertise_mentions.append(keyword)
                    context_mentions.append(response)
        
        # Calculate expertise level
        expertise_level = "expert" if len(set(expertise_mentions)) > 5 else \
                         "advanced" if len(set(expertise_mentions)) > 3 else \
                         "intermediate" if len(set(expertise_mentions)) > 1 else \
                         "basic"
        
        return {
            "domain_keywords": list(domain_keywords),
            "expertise_mentions": expertise_mentions,
            "context": context_mentions,
            "expertise_level": expertise_level,
            "domain_focus": len(set(expertise_mentions)) / len(responses) if responses else 0
        }

    def _identify_skill_gaps(self, responses: List[str]) -> List[str]:
        """Identify skill gaps based on responses"""
        # This method should return a list of skill gaps identified in the responses
        # You can implement your own logic to identify skill gaps based on the content of the responses
        return []

    def _assess_leadership_skills(self, responses: List[str]) -> Dict[str, Any]:
        """Assess leadership skills and experience from responses"""
        leadership_indicators = {
            "team_leadership": ["led team", "managed team", "team lead", "supervised", "directed"],
            "project_leadership": ["led project", "project lead", "coordinated", "spearheaded", "drove"],
            "strategic_leadership": ["strategy", "vision", "direction", "executive", "leadership"],
            "mentorship": ["mentor", "coach", "guide", "teach", "develop others"]
        }
        
        skill_scores = {category: 0 for category in leadership_indicators}
        leadership_evidence = {category: [] for category in leadership_indicators}
        
        for response in responses:
            for category, indicators in leadership_indicators.items():
                for indicator in indicators:
                    if indicator in response.lower():
                        skill_scores[category] += 1
                        leadership_evidence[category].append(response)
        
        # Calculate overall leadership level
        total_score = sum(skill_scores.values())
        leadership_level = "high" if total_score > 6 else \
                          "medium" if total_score > 3 else \
                          "emerging"
        
        # Identify primary leadership areas
        primary_areas = [cat for cat, score in skill_scores.items() if score > 1]
        development_areas = [cat for cat, score in skill_scores.items() if score == 0]
        
        return {
            "skill_scores": skill_scores,
            "leadership_evidence": leadership_evidence,
            "leadership_level": leadership_level,
            "primary_areas": primary_areas,
            "development_areas": development_areas,
            "total_leadership_score": total_score
        }

    def _get_role_progression_path(self) -> Dict[str, Any]:
        """Get potential career progression paths based on current role"""
        current_role = self.user_info.get('current_role', '').lower()
        experience_years = int(self.user_info.get('experience_years', 0))
        
        # Define common career paths for different role types
        career_paths = {
            "engineer": {
                "track_1": ["Junior Engineer", "Engineer", "Senior Engineer", "Lead Engineer", "Principal Engineer"],
                "track_2": ["Engineer", "Team Lead", "Engineering Manager", "Director of Engineering", "CTO"],
                "track_3": ["Engineer", "Solutions Architect", "Enterprise Architect", "Chief Architect"]
            },
            "developer": {
                "track_1": ["Junior Developer", "Developer", "Senior Developer", "Lead Developer", "Principal Developer"],
                "track_2": ["Developer", "Team Lead", "Development Manager", "Director of Development", "CTO"],
                "track_3": ["Developer", "Solutions Architect", "Enterprise Architect", "Chief Architect"]
            },
            "analyst": {
                "track_1": ["Junior Analyst", "Analyst", "Senior Analyst", "Lead Analyst", "Principal Analyst"],
                "track_2": ["Analyst", "Team Lead", "Analytics Manager", "Director of Analytics", "Chief Analytics Officer"],
                "track_3": ["Analyst", "Data Scientist", "Senior Data Scientist", "Chief Data Scientist"]
            },
            "manager": {
                "track_1": ["Team Lead", "Manager", "Senior Manager", "Director", "VP", "C-Level"],
                "track_2": ["Manager", "Program Manager", "Portfolio Manager", "Director of Programs", "COO"],
                "track_3": ["Manager", "Strategy Manager", "Head of Strategy", "Chief Strategy Officer"]
            }
        }
        
        # Determine role type
        role_type = next((rtype for rtype in career_paths.keys() if rtype in current_role), "generic")
        
        if role_type == "generic":
            # Generic progression path
            career_paths["generic"] = {
                "track_1": ["Junior Professional", "Professional", "Senior Professional", "Lead Professional", "Principal"],
                "track_2": ["Professional", "Team Lead", "Manager", "Director", "Executive"],
                "track_3": ["Professional", "Specialist", "Senior Specialist", "Expert", "Thought Leader"]
            }
            role_type = "generic"
        
        # Determine current level based on experience
        current_level = 0
        if experience_years > 15:
            current_level = 4
        elif experience_years > 10:
            current_level = 3
        elif experience_years > 5:
            current_level = 2
        elif experience_years > 2:
            current_level = 1
        
        # Get next steps for each track
        progression_tracks = {}
        for track, path in career_paths[role_type].items():
            try:
                current_position = next(i for i, role in enumerate(path) 
                                     if any(term in role.lower() for term in current_role.split()))
            except StopIteration:
                current_position = min(current_level, len(path) - 1)
            
            next_steps = path[current_position + 1:] if current_position < len(path) - 1 else []
            progression_tracks[track] = {
                "current_position": path[current_position],
                "next_steps": next_steps,
                "timeline": [f"{2 * (i + 1)} years" for i in range(len(next_steps))]
            }

        return {
            "role_type": role_type,
            "progression_tracks": progression_tracks,
            "recommended_track": self._determine_recommended_track(progression_tracks),
            "development_needs": self._identify_progression_requirements(progression_tracks)
        }

    def _determine_recommended_track(self, progression_tracks: Dict[str, Any]) -> str:
        """Determine the most suitable progression track based on user profile"""
        # Analyze responses for indicators of preferred career direction
        responses = [entry.get("response", "").lower() for entry in self.conversation_history]
        
        # Track preference indicators
        track_indicators = {
            "track_1": ["technical", "expert", "specialist", "individual contributor", "hands-on"],
            "track_2": ["management", "leadership", "team", "people", "organization"],
            "track_3": ["architecture", "strategy", "innovation", "transformation", "vision"]
        }
        
        # Count indicators for each track
        track_scores = {track: 0 for track in track_indicators}
        for track, indicators in track_indicators.items():
            for response in responses:
                track_scores[track] += sum(1 for ind in indicators if ind in response)
        
        # Return track with highest score, defaulting to track_1 if no clear preference
        return max(track_scores.items(), key=lambda x: x[1])[0]

    def _identify_progression_requirements(self, progression_tracks: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify requirements for progression in each track"""
        recommended_track = self._determine_recommended_track(progression_tracks)
        track_data = progression_tracks[recommended_track]
        
        if not track_data.get("next_steps"):
            return []
        
        next_role = track_data["next_steps"][0]
        
        # Define requirements based on next role
        requirements = []
        
        if "manager" in next_role.lower() or "lead" in next_role.lower():
            requirements.extend([
                {
                    "category": "Leadership",
                    "skills": ["Team Management", "Decision Making", "Delegation", "Performance Management"],
                    "timeline": "6-12 months"
                },
                {
                    "category": "Soft Skills",
                    "skills": ["Communication", "Conflict Resolution", "Mentoring", "Strategic Thinking"],
                    "timeline": "3-6 months"
                }
            ])
        
        if "senior" in next_role.lower() or "principal" in next_role.lower():
            requirements.extend([
                {
                    "category": "Technical Expertise",
                    "skills": ["System Design", "Architecture", "Best Practices", "Technical Strategy"],
                    "timeline": "12-18 months"
                },
                {
                    "category": "Business Acumen",
                    "skills": ["Project Management", "Resource Planning", "Business Strategy", "Stakeholder Management"],
                    "timeline": "6-12 months"
                }
            ])
        
        if "architect" in next_role.lower():
            requirements.extend([
                {
                    "category": "Architecture Skills",
                    "skills": ["System Architecture", "Integration Patterns", "Scalability", "Security"],
                    "timeline": "12-24 months"
                },
                {
                    "category": "Technical Leadership",
                    "skills": ["Technical Vision", "Architecture Governance", "Technology Strategy"],
                    "timeline": "12-18 months"
                }
            ])
        
        return requirements

    def _get_market_trends(self) -> Dict[str, Any]:
        """Get relevant market trends based on user's role and industry"""
        current_role = self.user_info.get('current_role', '').lower()
        industry = self.user_info.get('industry', '').lower()
        
        # Define common market trends
        general_trends = {
            "technology": [
                "AI and Machine Learning integration",
                "Cloud-native development",
                "DevOps and automation",
                "Cybersecurity focus"
            ],
            "business": [
                "Digital transformation",
                "Remote work adaptation",
                "Data-driven decision making",
                "Sustainability initiatives"
            ],
            "workforce": [
                "Skill-based hiring",
                "Continuous learning emphasis",
                "Work-life balance focus",
                "Diversity and inclusion"
            ]
        }
        
        # Role-specific trends
        role_trends = {}
        if "engineer" in current_role or "developer" in current_role:
            role_trends = {
                "technical": [
                    "Microservices architecture",
                    "Containerization and orchestration",
                    "Serverless computing",
                    "Edge computing"
                ],
                "methodologies": [
                    "Agile and DevOps integration",
                    "GitOps practices",
                    "Infrastructure as Code",
                    "Test-Driven Development"
                ]
            }
        elif "analyst" in current_role:
            role_trends = {
                "analytics": [
                    "Real-time analytics",
                    "Predictive modeling",
                    "Data visualization",
                    "Big data processing"
                ],
                "tools": [
                    "AutoML platforms",
                    "Business intelligence tools",
                    "Data governance frameworks",
                    "Cloud analytics"
                ]
            }
        elif "manager" in current_role or "lead" in current_role:
            role_trends = {
                "leadership": [
                    "Remote team management",
                    "Agile leadership",
                    "Cross-functional collaboration",
                    "Employee experience focus"
                ],
                "operations": [
                    "Digital workflow optimization",
                    "Automated reporting",
                    "Resource optimization",
                    "Risk management"
                ]
            }
        
        # Industry-specific trends
        industry_trends = self._get_industry_specific_trends(industry)
        
        return {
            "general_trends": general_trends,
            "role_trends": role_trends,
            "industry_trends": industry_trends,
            "impact_assessment": self._assess_trend_impact(),
            "opportunity_areas": self._identify_trend_opportunities()
        }

    def _get_industry_specific_trends(self, industry: str) -> Dict[str, List[str]]:
        """Get trends specific to the user's industry"""
        industry_trends = {
            "technology": {
                "innovation": [
                    "Edge computing adoption",
                    "Quantum computing research",
                    "5G applications",
                    "Blockchain integration"
                ],
                "practices": [
                    "Zero-trust security",
                    "Green IT initiatives",
                    "API-first development",
                    "Low-code platforms"
                ]
            },
            "finance": {
                "technology": [
                    "Open banking",
                    "Blockchain finance",
                    "AI-driven trading",
                    "RegTech solutions"
                ],
                "practices": [
                    "ESG investing",
                    "Digital payments",
                    "Automated compliance",
                    "Personalized banking"
                ]
            },
            "healthcare": {
                "technology": [
                    "Telemedicine",
                    "AI diagnostics",
                    "IoT medical devices",
                    "Digital health records"
                ],
                "practices": [
                    "Remote patient monitoring",
                    "Personalized medicine",
                    "Preventive healthcare",
                    "Healthcare analytics"
                ]
            }
        }
        
        # Find matching industry or return generic trends
        for key in industry_trends:
            if key in industry:
                return industry_trends[key]
        
        return {
            "general": [
                "Digital transformation",
                "Data-driven operations",
                "Customer experience focus",
                "Sustainability initiatives"
            ],
            "technology": [
                "Cloud adoption",
                "Process automation",
                "Cybersecurity measures",
                "Mobile-first approach"
            ]
        }

    def _assess_trend_impact(self) -> Dict[str, Any]:
        """Assess the potential impact of trends on the user's career"""
        current_role = self.user_info.get('current_role', '').lower()
        experience_years = int(self.user_info.get('experience_years', 0))
        
        impact_areas = {
            "skills": {
                "impact": "high" if experience_years < 5 else "medium",
                "focus_areas": [
                    "Technical skill adaptation",
                    "New methodology adoption",
                    "Tool proficiency"
                ],
                "timeline": "6-12 months"
            },
            "role_evolution": {
                "impact": "medium" if "manager" in current_role else "high",
                "focus_areas": [
                    "Role responsibility changes",
                    "New capability requirements",
                    "Team structure adaptation"
                ],
                "timeline": "12-24 months"
            },
            "career_opportunities": {
                "impact": "high",
                "focus_areas": [
                    "New role emergence",
                    "Skill premium changes",
                    "Industry convergence"
                ],
                "timeline": "18-36 months"
            }
        }
        
        return impact_areas

    def _identify_trend_opportunities(self) -> List[Dict[str, Any]]:
        """Identify specific opportunities based on market trends"""
        current_role = self.user_info.get('current_role', '').lower()
        
        opportunities = []
        
        # Technical opportunities
        if any(role in current_role for role in ["engineer", "developer", "technical"]):
            opportunities.extend([
                {
                    "category": "Technical Evolution",
                    "opportunities": [
                        "Cloud architecture expertise",
                        "AI/ML integration skills",
                        "DevOps practices mastery"
                    ],
                    "timeline": "6-12 months"
                }
            ])
        
        # Leadership opportunities
        if any(role in current_role for role in ["manager", "lead", "senior"]):
            opportunities.extend([
                {
                    "category": "Leadership Development",
                    "opportunities": [
                        "Digital transformation leadership",
                        "Remote team management",
                        "Innovation program leadership"
                    ],
                    "timeline": "12-18 months"
                }
            ])
        
        # General opportunities
        opportunities.extend([
            {
                "category": "Skill Development",
                "opportunities": [
                    "Data literacy",
                    "Digital collaboration",
                    "Business acumen"
                ],
                "timeline": "3-6 months"
            },
            {
                "category": "Industry Evolution",
                "opportunities": [
                    "Cross-industry expertise",
                    "Emerging technology adoption",
                    "Process optimization"
                ],
                "timeline": "12-24 months"
            }
        ])
        
        return opportunities

    def _get_related_sectors(self) -> List[str]:
        """Get sectors related to the user's industry"""
        industry = self.user_info.get('industry', '').lower()
        
        # Define industry relationships
        industry_relations = {
            "technology": [
                "Software Development",
                "Cloud Computing",
                "Cybersecurity",
                "Data Analytics",
                "Artificial Intelligence"
            ],
            "finance": [
                "Banking",
                "Investment Management",
                "Insurance",
                "Financial Technology",
                "Risk Management"
            ],
            "healthcare": [
                "Medical Technology",
                "Biotechnology",
                "Healthcare IT",
                "Pharmaceuticals",
                "Medical Devices"
            ],
            "consulting": [
                "Management Consulting",
                "IT Consulting",
                "Strategy Consulting",
                "Digital Transformation",
                "Business Advisory"
            ],
            "education": [
                "EdTech",
                "Online Learning",
                "Educational Services",
                "Training & Development",
                "Academic Research"
            ]
        }
        
        # Find matching industry or return generic sectors
        for key in industry_relations:
            if key in industry:
                return industry_relations[key]
        
        return [
            "Digital Services",
            "Professional Services",
            "Technology Solutions",
            "Business Services",
            "Innovation & Research"
        ]

    def _get_industry_trends(self) -> List[Dict[str, Any]]:
        """Get current trends in the user's industry"""
        industry = self.user_info.get('industry', '').lower()
        
        # Define industry-specific trends
        industry_trends = {
            "technology": [
                {
                    "trend": "AI and Machine Learning",
                    "impact": "high",
                    "timeline": "immediate",
                    "adoption_stage": "rapid growth"
                },
                {
                    "trend": "Cloud Computing",
                    "impact": "high",
                    "timeline": "current",
                    "adoption_stage": "mainstream"
                },
                {
                    "trend": "Cybersecurity",
                    "impact": "high",
                    "timeline": "ongoing",
                    "adoption_stage": "critical"
                }
            ],
            "finance": [
                {
                    "trend": "Digital Banking",
                    "impact": "high",
                    "timeline": "immediate",
                    "adoption_stage": "mainstream"
                },
                {
                    "trend": "Blockchain",
                    "impact": "medium",
                    "timeline": "emerging",
                    "adoption_stage": "early"
                },
                {
                    "trend": "RegTech",
                    "impact": "high",
                    "timeline": "current",
                    "adoption_stage": "growing"
                }
            ],
            "healthcare": [
                {
                    "trend": "Telemedicine",
                    "impact": "high",
                    "timeline": "immediate",
                    "adoption_stage": "rapid growth"
                },
                {
                    "trend": "AI Diagnostics",
                    "impact": "high",
                    "timeline": "emerging",
                    "adoption_stage": "early"
                },
                {
                    "trend": "Digital Health Records",
                    "impact": "high",
                    "timeline": "current",
                    "adoption_stage": "mainstream"
                }
            ]
        }
        
        # Find matching industry or return generic trends
        for key in industry_trends:
            if key in industry:
                return industry_trends[key]
        
        return [
            {
                "trend": "Digital Transformation",
                "impact": "high",
                "timeline": "immediate",
                "adoption_stage": "critical"
            },
            {
                "trend": "Remote Work",
                "impact": "high",
                "timeline": "current",
                "adoption_stage": "mainstream"
            },
            {
                "trend": "Data Analytics",
                "impact": "high",
                "timeline": "ongoing",
                "adoption_stage": "growing"
            }
        ]

    def _get_growth_areas(self) -> List[Dict[str, Any]]:
        """Get growth areas in the user's industry"""
        industry = self.user_info.get('industry', '').lower()
        
        # Define industry-specific growth areas
        growth_areas = {
            "technology": [
                {
                    "area": "AI/ML Engineering",
                    "growth_rate": "high",
                    "skill_demand": "very high",
                    "opportunity_level": "excellent"
                },
                {
                    "area": "Cloud Architecture",
                    "growth_rate": "high",
                    "skill_demand": "high",
                    "opportunity_level": "excellent"
                },
                {
                    "area": "DevSecOps",
                    "growth_rate": "high",
                    "skill_demand": "high",
                    "opportunity_level": "very good"
                }
            ],
            "finance": [
                {
                    "area": "FinTech Development",
                    "growth_rate": "high",
                    "skill_demand": "high",
                    "opportunity_level": "excellent"
                },
                {
                    "area": "Blockchain Development",
                    "growth_rate": "medium",
                    "skill_demand": "growing",
                    "opportunity_level": "good"
                },
                {
                    "area": "Risk Analytics",
                    "growth_rate": "high",
                    "skill_demand": "high",
                    "opportunity_level": "very good"
                }
            ],
            "healthcare": [
                {
                    "area": "Health Informatics",
                    "growth_rate": "high",
                    "skill_demand": "high",
                    "opportunity_level": "excellent"
                },
                {
                    "area": "Digital Health",
                    "growth_rate": "high",
                    "skill_demand": "high",
                    "opportunity_level": "excellent"
                },
                {
                    "area": "Healthcare Analytics",
                    "growth_rate": "high",
                    "skill_demand": "high",
                    "opportunity_level": "very good"
                }
            ]
        }
        
        # Find matching industry or return generic growth areas
        for key in growth_areas:
            if key in industry:
                return growth_areas[key]
        
        return [
            {
                "area": "Digital Transformation",
                "growth_rate": "high",
                "skill_demand": "high",
                "opportunity_level": "excellent"
            },
            {
                "area": "Data Analytics",
                "growth_rate": "high",
                "skill_demand": "high",
                "opportunity_level": "very good"
            },
            {
                "area": "Project Management",
                "growth_rate": "medium",
                "skill_demand": "steady",
                "opportunity_level": "good"
            }
        ]
            