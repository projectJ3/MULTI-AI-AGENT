import streamlit as st
import requests

from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

st.set_page_config(page_title="Multi AI Agent", layout="centered")
st.title("Multi AI Agent using Groq and Tavily New")

system_prompt = st.text_area("Define your AI Agent: ", height=70)
selected_model = st.selectbox("Select your AI model: ", settings.ALLOWED_MODEL_NAMES)

allow_web_search = st.checkbox("Allow web search")

user_query = st.text_area("Enter your query : ", height=150)

API_URL = "http://127.0.0.1:9999/chat"

if st.button("Ask Agent") and user_query.strip():

    payload = {
        "model_name": selected_model,
        "system_prompt": system_prompt,
        "messages": [user_query],
        "allow_search": allow_web_search
    }

    try:
        logger.info("Sending request to backend")
        # add short timeout to fail fast if backend is down
        response = requests.post(API_URL, json=payload, timeout=8)

        if response.status_code == 200:
            # be defensive parsing JSON
            try:
                data = response.json()
            except Exception:
                logger.error("Backend returned non-JSON response: %s", response.text)
                st.error("Backend returned invalid response (non-JSON). See logs for details.")
            else:
                agent_response = data.get("response", "")
                logger.info("Successfully received response from backend")
                st.subheader("Agent Response")
                st.markdown(agent_response.replace("\n", "<br>"), unsafe_allow_html=True)
        else:
            # log status and body to help debugging
            logger.error("Backend returned error: %s - %s", response.status_code, response.text)
            st.error(f"Backend Error: {response.status_code} — see logs for details")

    except requests.exceptions.RequestException as req_e:
        # network-related exceptions (ConnectionError, Timeout, etc.)
        logger.exception("Network error while sending request to backend")
        # pass the real exception into CustomException so UI shows the cause
        st.error(str(CustomException("Failed to communicate to backend", error_detail=req_e)))

    except Exception as e:
        # catch-all: log full traceback and show detailed error
        logger.exception("Error occurred while sending request to backend")
        st.error(str(CustomException("Failed to communicate to backend", error_detail=e)))
