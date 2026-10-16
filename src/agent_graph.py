from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from src.config import GEMINI_API_KEY
from src.prompts import AGENT_SYSTEM_PROMPT
from src.tools import run_python_analysis


def get_agent_app():
    """
    Létrehozza és visszaadja a LangGraph alapú adatelemző agentet a Gemini Flash-Lite modellel.
    Az agent a thread_id alapján megjegyzi a korábbi üzeneteket, így a követő kérdéseket is érti.
    """
    # 1. Inicializáljuk a Gemini Flash-Lite modellt a LangChain-ben
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=GEMINI_API_KEY
    )

    # 2. Összegyűjtjük az agent eszközeit
    tools = [run_python_analysis]

    # 3. Memória: a beszélgetés állapotát thread_id szerint tárolja (processzen belül)
    memory = MemorySaver()

    # 4. Létrehozzuk a LangGraph ReAct agentet
    agent_app = create_react_agent(
        model=model,
        tools=tools,
        prompt=AGENT_SYSTEM_PROMPT,
        checkpointer=memory,
    )

    return agent_app