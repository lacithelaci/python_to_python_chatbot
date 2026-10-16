import os
import shutil
import time
import uuid

import streamlit as st
from src.agent_graph import get_agent_app

CHART_PATH = "chart.png"  # Ide menti a grafikont az agent
CHART_HISTORY_DIR = "chart_history"  # Ide másoljuk az előzmények számára

# Oldal konfiguráció
st.set_page_config(
    page_title="Ügyfélszolgálati Adatelemző Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Ügyfélszolgálati Adatelemző AI Agent")
st.markdown(
    "Tégy fel kérdéseket az ügyfélszolgálati adatokról természetes nyelven! "
    "Az agent önállóan ír Pandas kódot és elemzi az adatokat."
)


def extract_text(content) -> str:
    """Kinyeri a tiszta szöveget az LLM válaszából (str, list vagy dict esetén is)."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", "")
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type", "text") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(p for p in parts if p)
    return str(content)


def save_chart_to_history():
    """Ha az agent generált grafikont, átmásolja egyedi néven, és visszaadja az útvonalát."""
    if not os.path.exists(CHART_PATH):
        return None
    os.makedirs(CHART_HISTORY_DIR, exist_ok=True)
    new_path = os.path.join(CHART_HISTORY_DIR, f"chart_{int(time.time() * 1000)}.png")
    shutil.copy(CHART_PATH, new_path)
    return new_path


# Agent inicializálása (cache-elve, hogy ne töltődjön újra minden üzenetnél)
@st.cache_resource
def load_agent():
    return get_agent_app()


try:
    with st.spinner("Agent előkészítése és modell betöltése..."):
        agent_app = load_agent()
except Exception as e:
    st.error(f"Hiba az agent indulásakor: {e}")
    st.stop()

# Chat előzmények tárolása a Streamlit session state-ben
if "messages" not in st.session_state:
    st.session_state.messages = []

# Minden böngészőmunkamenet saját beszélgetési szálat kap az agent memóriájában
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Korábbi üzenetek kirajzolása a képernyőre (grafikonnal együtt)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        image_path = message.get("image")
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption="Az agent által generált grafikon")

# Felhasználói beviteli mező alul
if prompt := st.chat_input("Írd meg a kérdésed (pl. Melyik csapat teljesített a legjobban?):"):
    # Felhasználó üzenetének hozzáadása és megjelenítése
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent válasz generálása
    with st.chat_message("assistant"):
        with st.spinner("Agent gondolkodik és elemez..."):
            try:
                # A régi grafikont töröljük, hogy ne jelenjen meg tévesen az új válasznál
                if os.path.exists(CHART_PATH):
                    os.remove(CHART_PATH)

                # Meghívjuk a LangGraph agentet
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                response = agent_app.invoke({"messages": [("user", prompt)]}, config=config)

                # Az utolsó üzenet az agent végső válasza
                messages = response.get("messages", [])
                if messages:
                    assistant_response = extract_text(messages[-1].content)
                else:
                    assistant_response = "Nem érkezett válasz az agenttől."

                st.markdown(assistant_response)

                # Ha az agent generált grafikont, megjelenítjük és eltároljuk az előzményekhez
                image_path = save_chart_to_history()
                if image_path:
                    st.image(image_path, caption="Az agent által generált grafikon")

                # Eltároljuk az asszisztens válaszát is
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "image": image_path,
                })

            except Exception as e:
                error_msg = f"Hiba történt a futtatás során: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})