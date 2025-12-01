import asyncio
import uuid
import warnings

from dotenv import load_dotenv

from google.adk import Runner
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.plugins import LoggingPlugin
from google.adk.sessions import DatabaseSessionService
from google.genai.types import Content, Part

from fit_flow.agent import orchestrator_agent

load_dotenv()
warnings.filterwarnings(action='ignore')

APP_NAME="second_grab"
USER_ID=f"user_{uuid.uuid4().hex[:8]}"
SESSION_ID=f"session_{uuid.uuid4().hex[:8]}"

DB_URL="sqlite:///./second_grab_memory.db"

memory_service=(InMemoryMemoryService())
session_service=DatabaseSessionService(db_url=DB_URL)
artifact_service=InMemoryArtifactService

async def setup_session():
    try:
        session=await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
    except Exception as err:
        print(f"An Error has occurred: {err}")
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'.")
    return session

# Economizing on context by compacting memory
second_grab_app = App(
    name=APP_NAME,
    root_agent=orchestrator_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # Trigger compaction every 3 invocations
        overlap_size=1,  # Keep 1 previous turn for context
    ),
    plugins=[
        LoggingPlugin()
    ]
)

# When using compaction, the agent and app_name are not to be provided
# They are provided already by the app
# Added generic plugin for observability
runner=Runner(
    # agent=orchestrator_agent,
    # app_name=APP_NAME,
    app=second_grab_app,
    session_service=session_service,
    memory_service=memory_service
)

async def call_agent_async(
        query: str,
        instance_runner,
        user_id,
        session_id
):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>>User Query: {query}")

    # Prepare the User's message in ADK format
    content=Content( role='user', parts=[Part(text=query)] )

    default_response="Agent did not produce a final response."
    final_response_text=default_response

    # Execute agent logic and yield event by iterating through events to
    # find the final answer
    async for event in instance_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
    ):
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
        if event.content.parts and event.content.parts[0].function_call:
           print(f"{event.author} calling: {event.content.parts[0].function_call.name}...")

        # is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:  # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")



# Define the main chat loop
async def main():
    # Ensure a session is created before starting the chat
    session = await setup_session()
    print("\nWelcome to the Second Grab! Type '/bye' to exit.")

    while True:
        try:
            user_query = input("You: ")
        except EOFError:  # Handle Ctrl+D
            print("\nSecond Grab: Detected EOF. Exiting.")
            break
        if user_query.lower() == "/bye":
            print("Second Grab: Goodbye!")
            break
        await call_agent_async(
            user_query,
            instance_runner=runner,
            user_id=session.user_id,
            session_id=session.id
        )

# Uncomment the following lines if running as a standard Python script (.py file):
if __name__ == "__main__":
    try:
        asyncio.run(main())

    except Exception as e:
        print(f"An error occurred: {e}")