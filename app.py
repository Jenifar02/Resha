import datetime
import streamlit as st
import google.generativeai as genai

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

# Page Configuration
st.set_page_config(
    page_title="Resha - AI Academic & Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom UI Styling
st.markdown("""
<style>
    .stApp {
        background-color: #FAFCFA;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    header {visibility: hidden;}

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
        font-size: 0.72rem;
        color: #A7F3D0 !important;
        opacity: 0.75;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State
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

# Sidebar UI
with st.sidebar:
    st.markdown('<div class="brand-title">🔬 Resha</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">AI Academic & Research Assistant</div>', unsafe_allow_html=True)

    user_name_input = st.text_input("👤 Your Profile Name", value=st.session_state.user_name)
    if user_name_input:
        st.session_state.user_name = user_name_input

    if st.button("✨ New Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="sidebar-section">RESEARCH DOCUMENTS</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF/DOCX", type=["pdf", "docx"], label_visibility="collapsed")

    if uploaded_file is not None:
        if st.session_state.document_name != uploaded_file.name:
            with st.spinner("Processing document..."):
                extracted = extract_text_from_upload(uploaded_file)
            st.session_state.document_name = uploaded_file.name
            st.session_state.document_text = extracted
            
        if st.session_state.document_text:
            st.success(f"📄 Loaded: **{uploaded_file.name}**")
            st.caption(f"{len(st.session_state.document_text):,} characters ready as context")
        else:
            st.warning(f"📄 **{uploaded_file.name}** uploaded, but text extraction failed.")
    elif st.session_state.document_name is not None:
        st.session_state.document_name = None
        st.session_state.document_text = None

    st.markdown('<div class="sidebar-section">CONTROLS</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="sidebar-footer">Powered by Google Gemini</div>', unsafe_allow_html=True)

# Hero UI
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

# Render Existing Chat History
for message in st.session_state.messages:
    avatar = "🔬" if message["role"] == "assistant" else "🧑‍🎓"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# User Input Handling
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
        with st.spinner("Resha is synthesizing research..."):
            try:
                genai.configure(api_key=api_key)
                
                # Instruction and Context Setup
                system_instruction = "You are Resha, a professional academic and research assistant. Provide thorough, well-structured, accurate answers. Include a '**Key References & Sources**' section at the end."
                if st.session_state.document_text:
                    system_instruction += f"\n\nDocument Context ({st.session_state.document_name}):\n" + st.session_state.document_text[:10000]

                # Direct API Call with Stable Model
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction
                )
                
                # Build chat history for API
                chat_history = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg["content"]]})

                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_prompt)

                if response and response.text:
                    placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    placeholder.error("No response generated from model.")
            except Exception as ex:
                placeholder.error(f"API Error Details: {ex}")
                st.session_state.messages.pop()
