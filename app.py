import datetime
import streamlit as st
from google import genai
from google.genai import types

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

# Page Configuration - Standard Light Theme
st.set_page_config(
    page_title="Resha - AI Academic & Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Priority model fallbacks requested by API error message
CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]

# Session State Initialization
defaults = {
    "messages": [],
    "user_name": "Researcher",
    "document_name": None,
    "document_text": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def get_time_greeting():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def extract_text_from_upload(uploaded_file):
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".pdf"):
            if pypdf is None:
                st.sidebar.error("PDF support requires 'pypdf' package.")
                return ""
            reader = pypdf.PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        elif name.endswith(".docx"):
            if DocxDocument is None:
                st.sidebar.error("DOCX support requires 'python-docx' package.")
                return ""
            doc = DocxDocument(uploaded_file)
            return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
    return ""

def build_system_instruction():
    instruction = (
        "You are Resha, a professional academic and research assistant. "
        "Provide thorough, well-structured, accurate answers to research questions. "
        "At the end of every response, include a dedicated section titled "
        "'**Key References & Sources**' listing relevant academic literature or credible sources."
    )
    if st.session_state.document_text:
        instruction += (
            f"\n\nContext from loaded document '{st.session_state.document_name}':\n\n"
            f"{st.session_state.document_text[:12000]}"
        )
    return instruction

# Standard Streamlit Sidebar (No custom CSS blocking visibility)
with st.sidebar:
    st.title("🔬 Resha")
    st.caption("AI Academic & Research Assistant")
    st.divider()

    user_name_input = st.text_input("👤 Your Name", value=st.session_state.user_name)
    if user_name_input:
        st.session_state.user_name = user_name_input

    if st.button("✨ New Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.subheader("Document Context")
    uploaded_file = st.file_uploader("Upload PDF/DOCX", type=["pdf", "docx"])

    if uploaded_file is not None:
        if st.session_state.document_name != uploaded_file.name:
            with st.spinner("Processing document..."):
                extracted = extract_text_from_upload(uploaded_file)
            st.session_state.document_name = uploaded_file.name
            st.session_state.document_text = extracted
            
        if st.session_state.document_text:
            st.success(f"📄 Loaded: **{uploaded_file.name}**")
            st.caption(f"{len(st.session_state.document_text):,} characters loaded")
        else:
            st.warning(f"📄 Text extraction failed.")
    elif st.session_state.document_name is not None:
        st.session_state.document_name = None
        st.session_state.document_text = None

    st.divider()
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main Interface Welcome
if not st.session_state.messages:
    greeting = get_time_greeting()
    st.title(f"{greeting}, {st.session_state.user_name}.")
    st.markdown("Where shall we push the boundaries of knowledge today?")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**📚 Evidence Synthesis**\n\nExtract literature insights and citations.")
    with col2:
        st.info("**🧬 Concept & Math**\n\nDeconstruct complex formulas & algorithms.")
    with col3:
        st.info("**🖋️ Academic Writing**\n\nRefine research abstracts and language.")

# Render Chat
for message in st.session_state.messages:
    avatar = "🔬" if message["role"] == "assistant" else "🧑‍🎓"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Handle Chat Input
if user_prompt := st.chat_input("Ask Resha a research query..."):
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        st.error("API Key missing! Please configure GEMINI_API_KEY in Streamlit Secrets.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="🔬"):
        placeholder = st.empty()
        with st.spinner("Resha is thinking..."):
            client = genai.Client(api_key=api_key)

            # 1. Dynamically find available models from API if candidate fails
            target_models = list(CANDIDATE_MODELS)
            try:
                available_models = [m.name.replace("models/", "") for m in client.models.list()]
                # Add flash models found in user's API key scope
                flash_models = [m for m in available_models if "flash" in m]
                for fm in flash_models:
                    if fm not in target_models:
                        target_models.append(fm)
            except Exception:
                pass

            contents = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

            bot_reply, last_err = None, None

            # 2. Iterate through candidate models dynamically
            for model_id in target_models:
                try:
                    response = client.models.generate_content(
                        model=model_id,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=build_system_instruction()
                        )
                    )
                    if response and response.text:
                        bot_reply = response.text
                        break
                except Exception as e:
                    last_err = e
                    continue

        if bot_reply:
            placeholder.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        else:
            placeholder.error(f"API Error: {last_err}")
            st.session_state.messages.pop()
