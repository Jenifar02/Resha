import datetime
import streamlit as st
from google import genai

# Page Configuration
st.set_page_config(
    page_title="Resha - AI Academic & Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fetch API Key safely from Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# Custom UI Styling (Green, Yellow & White Theme)
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
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = "Researcher"

# Time-Based Dynamic Greeting Function
def get_time_greeting():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# Sidebar Structure
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
    if uploaded_file:
        st.success(f"📄 Loaded: **{uploaded_file.name}**")

    st.markdown('<div class="sidebar-section">CONTROLS</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initial Hero Welcome UI
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
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Submission Handling
if user_prompt := st.chat_input("Ask Resha a research query..."):
    if not api_key:
        st.error("API Key missing! Please make sure GEMINI_API_KEY is configured in Streamlit Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Resha is synthesizing research and fetching sources..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""
                    You are Resha, an academic research assistant. Provide thorough, well-structured, professional answers to the query.
                    At the end of your response, always include a dedicated section titled '**Key References & Sources**' listing standard academic literature/sources or verified web references for verification.
                    
                    Query: {user_prompt}
                    """
                    
                    # Target Active Model Endpoints
                    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash"]
                    bot_reply = None
                    last_err = None

                    for model_id in candidate_models:
                        try:
                            response = client.models.generate_content(
                                model=model_id,
                                contents=prompt
                            )
                            if response and response.text:
                                bot_reply = response.text
                                break
                        except Exception as e:
                            last_err = e
                            continue

                    if bot_reply:
                        st.markdown(bot_reply)
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    else:
                        st.error(f"Unable to connect to Gemini API. Error details: {last_err}")
                except Exception as ex:
                    st.error(f"Configuration Error: {ex}")
