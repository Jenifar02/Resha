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

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Resha - AI Academic & Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Preferred model order. The app tries each in turn (and remembers whichever
# one last worked) so a single deprecated / rate-limited model never breaks
# the whole chatbot.
CANDIDATE_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"]

# ---------------------------------------------------------------------------
# Custom UI Styling (Green, Yellow & White Theme)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #FAFCFA;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Top Header Line */
    header {visibility: hidden;}

    /* Sidebar Custom Styling */
    div[data-testid="stSidebar"] {
        background-color: #064E3B !important;
        border-right: 3px solid #10B981;
        padding-top: 1rem;
    }

    div[data-testid="stSidebar"] *,
    div[data-testid="stSidebar"] label {
        color: #ECFDF5 !important;
    }

    .brand-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #FACC15 !important;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 2px;
    }

    .brand-subtitle {
        font-size: 0.85rem;
        color: #A7F3D0 !important;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }

    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #FACC15 !important;
        color: #064E3B !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
    }

    /* Hero Banner UI */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1.5rem 1rem;
        max-width: 850px;
        margin: 0 auto;
    }

    .hero-greeting {
        font-size: 2.3rem;
        font-weight: 800;
        color: #065F46;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #374151;
        margin-top: 10px;
        line-height: 1.6;
    }

    /* Card Containers */
    .card-container {
        background: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-top: 4px solid #10B981;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
    }

    .card-container:hover {
        border-color: #FACC15;
        border-top: 4px solid #FACC15;
        transform: translateY(-3px);
    }

    .card-icon {
        font-size: 1.5rem;
        margin-bottom: 10px;
        background: #FEF9C3;
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
    }

    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #064E3B;
        margin-bottom: 6px;
    }

    .card-desc {
        font-size: 0.88rem;
        color: #4B5563;
        line-height: 1.45;
    }

    .sidebar-section {
        font-size: 0.75rem;
        font-weight: 800;
        color: #FACC15 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 1.3rem;
        margin-bottom: 0.6rem;
    }

    .sidebar-footer {
        position: fixed;
        bottom: 12px;
        font-size: 0.72rem;
        color: #A7F3D0 !important;
        opacity: 0.75;
    }

    /* -----------------------------------------------------------------
       Visible "open sidebar" button — this is the small arrow Streamlit
       renders in the top-left corner once the sidebar is collapsed. By
       default it's a faint grey icon that's easy to miss; restyle it as
       a clear branded circular button so it's obvious how to bring the
       sidebar back.
    ----------------------------------------------------------------- */
    [data-testid="collapsedControl"] {
        background-color: #064E3B !important;
        border: 2px solid #FACC15 !important;
        border-radius: 50% !important;
        padding: 6px !important;
        top: 14px !important;
        left: 14px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.15s ease, border-color 0.15s ease;
        z-index: 999999 !important;
    }

    [data-testid="collapsedControl"]:hover {
        transform: scale(1.1);
        border-color: #FFFFFF !important;
    }

    [data-testid="collapsedControl"] svg {
        fill: #FACC15 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
defaults = {
    "messages": [],
    "user_name": "Researcher",
    "chat": None,
    "chat_model": None,
    "document_name": None,
    "document_text": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_time_greeting():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


def extract_text_from_upload(uploaded_file):
    """Pull raw text out of an uploaded PDF or DOCX so it can be used as
    context for the chat. Returns '' if extraction fails or the right
    library isn't installed."""
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".pdf"):
            if pypdf is None:
                st.sidebar.error("PDF support needs the 'pypdf' package (see requirements.txt).")
                return ""
            reader = pypdf.PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        elif name.endswith(".docx"):
            if DocxDocument is None:
                st.sidebar.error("DOCX support needs the 'python-docx' package (see requirements.txt).")
                return ""
            doc = DocxDocument(uploaded_file)
            return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        st.sidebar.error(f"Couldn't read that file: {e}")
    return ""


def build_system_instruction():
    instruction = (
        "You are Resha, a professional academic and research assistant. "
        "Provide thorough, well-structured, accurate answers to research questions. "
        "Use clear headings and concise paragraphs where helpful. "
        "At the end of every response, include a dedicated section titled "
        "'**Key References & Sources**' listing relevant academic literature or "
        "credible sources the user can consult for verification."
    )
    if st.session_state.document_text:
        instruction += (
            f"\n\nThe user has uploaded a reference document titled "
            f"'{st.session_state.document_name}'. Use the following extracted "
            f"content as additional context whenever it's relevant to their "
            f"question:\n\n{st.session_state.document_text[:12000]}"
        )
    return instruction


def history_to_genai_content(messages):
    history = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        history.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    return history


def reset_chat_session():
    st.session_state.chat = None
    st.session_state.chat_model = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand-title">🔬 Resha</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">AI Academic & Research Assistant</div>', unsafe_allow_html=True)

    user_name_input = st.text_input("👤 Your Profile Name", value=st.session_state.user_name)
    if user_name_input:
        st.session_state.user_name = user_name_input

    if st.button("✨ New Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        reset_chat_session()
        st.rerun()

    st.markdown('<div class="sidebar-section">RESEARCH DOCUMENTS</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF/DOCX", type=["pdf", "docx"], label_visibility="collapsed")

    if uploaded_file is not None:
        if st.session_state.document_name != uploaded_file.name:
            with st.spinner("Reading document..."):
                extracted = extract_text_from_upload(uploaded_file)
            st.session_state.document_name = uploaded_file.name
            st.session_state.document_text = extracted
            reset_chat_session()  # rebuild so the new context is included
        if st.session_state.document_text:
            st.success(f"📄 Loaded: **{uploaded_file.name}**")
            st.caption(f"{len(st.session_state.document_text):,} characters available as context")
        else:
            st.warning(f"📄 **{uploaded_file.name}** uploaded, but no text could be extracted.")
    elif st.session_state.document_name is not None:
        st.session_state.document_name = None
        st.session_state.document_text = None
        reset_chat_session()

    st.markdown('<div class="sidebar-section">CONTROLS</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        reset_chat_session()
        st.rerun()

    st.markdown('<div class="sidebar-footer">Powered by Google Gemini</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Initial Hero Welcome UI
# ---------------------------------------------------------------------------
if not st.session_state.messages:
    greeting = get_time_greeting()
    st.markdown(f"""
        <div class="hero-container">
            <div class="hero-greeting">{greeting}, {st.session_state.user_name}.</div>
            <div class="hero-subtitle">Where shall we push the boundaries of knowledge today? Upload papers, analyze citations, or synthesize complex research topics.</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">📚</div>
                <div class="card-title">Evidence Synthesis</div>
                <div class="card-desc">Extract structured literature insights, academic references, and reliable citations.</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">🧬</div>
                <div class="card-title">Concept & Math</div>
                <div class="card-desc">Deconstruct intricate formulas, algorithms, and methodologies with step-by-step clarity.</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">🖋️</div>
                <div class="card-title">Academic Writing</div>
                <div class="card-desc">Refine research abstracts, thesis frameworks, and academic language effectively.</div>
            </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Render Existing Chat History
# ---------------------------------------------------------------------------
for message in st.session_state.messages:
    avatar = "🔬" if message["role"] == "assistant" else "🧑‍🎓"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---------------------------------------------------------------------------
# User Chat Submission Handling
# ---------------------------------------------------------------------------
if user_prompt := st.chat_input("Ask Resha a research query..."):
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        st.error("API Key missing! Please make sure GEMINI_API_KEY is configured in Streamlit Secrets.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="🔬"):
        placeholder = st.empty()
        with st.spinner("Resha is synthesizing research and fetching sources..."):
            client = genai.Client(api_key=api_key)
            history_for_new_session = st.session_state.messages[:-1]

            # Try the model that worked last time first, then fall back
            # through the rest of the candidate list if needed.
            models_to_try = []
            if st.session_state.chat_model:
                models_to_try.append(st.session_state.chat_model)
            models_to_try += [m for m in CANDIDATE_MODELS if m not in models_to_try]

            bot_reply, last_err = None, None
            for model_id in models_to_try:
                try:
                    if st.session_state.chat is None or st.session_state.chat_model != model_id:
                        st.session_state.chat = client.chats.create(
                            model=model_id,
                            config=types.GenerateContentConfig(
                                system_instruction=build_system_instruction()
                            ),
                            history=history_to_genai_content(history_for_new_session),
                        )
                        st.session_state.chat_model = model_id

                    response = st.session_state.chat.send_message(user_prompt)
                    if response and response.text:
                        bot_reply = response.text
                        break
                except Exception as e:
                    last_err = e
                    reset_chat_session()
                    continue

        if bot_reply:
            placeholder.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        else:
            placeholder.error(f"Unable to connect to Gemini API. Error details: {last_err}")
            st.session_state.messages.pop()  # drop the unanswered user turn
