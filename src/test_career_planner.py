import asyncio
from src.core.conversation_coordinator import ConversationCoordinator
from src.agents.vision_principal import VisionPrincipal
from src.agents.background_principal import BackgroundPrincipal
from src.agents.financial_principal import FinancialPrincipal

async def test_career_planning_session():
    coordinator = ConversationCoordinator()
    
    # Add principals
    coordinator.add_principal(VisionPrincipal())
    coordinator.add_principal(BackgroundPrincipal())
    coordinator.add_principal(FinancialPrincipal())
    
    # Start conversation
    await coordinator.start_conversation()

if __name__ == "__main__":
    asyncio.run(test_career_planning_session()) 