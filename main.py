import asyncio
from src.core.conversation_coordinator import ConversationCoordinator
from src.agents.vision_agent import VisionAgent
from src.agents.background_agent import BackgroundAgent

async def main():
    # Initialize the conversation coordinator
    coordinator = ConversationCoordinator()
    
    # Add principals (agents)
    vision_agent = VisionAgent("Vision Principal")
    background_agent = BackgroundAgent("Background Principal")
    
    coordinator.add_principal(vision_agent)
    coordinator.add_principal(background_agent)
    
    # Start the conversation
    await coordinator.start_conversation()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 