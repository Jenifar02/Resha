import datetime
import streamlit as st
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="Resha - AI Academic & Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load API Key from Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# Custom CSS with Green, Yellow & White Theme
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #FAFCFA;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header & Toggle styling */
    header {visibility: hidden;}
    
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="baseButton-header"] {
        background-color: #064E3B !important;
        color: #FACC15 !important;
        border: 2px solid #FACC15 !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        visibility: visible !important;
        display: flex !important;
        z-index: 999999 !important;
    }
    button[data-testid="stSidebarCollapseButton"]:hover,
    button[data-testid="baseButton-header"]:hover {
        background-color: #FACC15 !important;
        color: #064E3B !important;
    }

    /* Sidebar Styling (Deep Emerald Green) */
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
    
    /* Primary Buttons */
    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #FACC15 !important;
        color: #064E3B !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: #EAB308 !important;
        box-shadow: 0 4px 12px rgba(250, 204, 21, 0.3);
    }

    /* Hero Banner */
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
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #374151;
        margin-top: 10px;
        line-height: 1.6;
    }

    /* Feature Cards */
    .card-container {
        background: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-top: 4px solid #10B981;
        border-radius: 12px;
        padding: 20px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    
    .card-container:hover {
        border-color: #FACC15;
        border-top: 4px solid #FACC15;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.15);
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

# Time-based Dynamic Greeting Generator
def get_time_greeting():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# Sidebar Implementation
with st.sidebar:
    st.markdown('<div class="brand-title">🔬 Resha</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">AI Academic & Research Assistant</div>', unsafe_allow_html=True)
    
    # Profile Name Config
    user_name_input = st.text_input("👤 Your Profile Name", value=st.session_state.user_name)
    if user_name_input:
        st.session_state.user_name = user_name_input
    
    if st.button("✨ New Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="sidebar-section">RESEARCH DOCUMENTS</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF/DOCX", 
        type=["pdf", "docx"], 
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.success(f"📄 Loaded: **{uploaded_file.name}**")

    st.markdown('<div class="sidebar-section">CONTROLS</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Dynamic Greeting Header (Claude Style)
if not st.session_state.messages:
    greeting = get_time_greeting()
    st.markdown(f"""
        <div class="hero-container">
            <div class="hero-greeting">{greeting}, {st.session_state.user_name}.</div>
            <div class="hero-subtitle">Where shall we push the boundaries of knowledge today? Upload papers, explore citations, or dive into complex academic research.</div>
        </div>
    """, unsafe_allow_html=True)

    # Feature Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">📚</div>
                <div class="card-title">Evidence-Based Research</div>
                <div class="card-desc">Ask queries and receive verified insights complete with web source links and literature evidence.</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">🧬</div>
                <div class="card-title">Concept & Math Synthesis</div>
                <div class="card-desc">Break down intricate formulas, algorithms, and methodologies into structured, clear explanations.</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">🖋️</div>
                <div class="card-title">Academic Writing Assistant</div>
                <div class="card-desc">Formulate literature reviews, refine abstracts, and structure thesis arguments with precision.</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if user_prompt := st.chat_input("Ask Resha a research query..."):
    if not api_key:
        st.error("API Key missing! Please configure GEMINI_API_KEY in Streamlit Secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Resha is synthesizing research and fetching sources..."):
                try:
                    client = genai.Client(api_key=api_key)
                    # Enable Google Search Grounding for Source Links
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=f"You are Resha, an advanced academic research assistant. Provide detailed, well-structured answers. Always provide reference web links or citations at the end so the user can verify the sources: {user_prompt}",
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())]
                        )
                    )
                    
                    bot_reply = response.text
                    st.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    st.error(f"Execution Error: {e}")
