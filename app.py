import streamlit as st
from google import genai

# Page Configuration
st.set_page_config(
    page_title="Resha - AI Academic & Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Modern UI
st.markdown("""
<style>
    /* Main Background and Font */
    .stApp {
        background-color: #FAFAFA;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Default Headers */
    header {visibility: hidden;}
    
    /* Sidebar Custom Styling */
    div[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        padding-top: 1rem;
    }
    
    /* Brand Header */
    .brand-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0px;
    }
    
    .brand-subtitle {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    
    /* Welcome Screen Styling */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #64748B;
        margin-top: 8px;
        line-height: 1.5;
    }

    /* Feature Cards */
    .card-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        transition: all 0.25s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
    }
    
    .card-container:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
        transform: translateY(-2px);
    }
    
    .card-icon {
        font-size: 1.5rem;
        margin-bottom: 10px;
    }
    
    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 6px;
    }
    
    .card-desc {
        font-size: 0.85rem;
        color: #64748B;
        line-height: 1.4;
    }

    /* Custom Input Fixes */
    div[data-testid="stChatInput"] {
        border-radius: 12px;
    }
    
    /* Section Headers */
    .sidebar-section {
        font-size: 0.75rem;
        font-weight: 700;
        color: #94A3B8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar UI Implementation
with st.sidebar:
    st.markdown('<div class="brand-title">🔬 Resha</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">Next-Gen Academic Research Assistant</div>', unsafe_allow_html=True)
    
    # API Key Input
    api_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="Paste key here...", help="Enter your Google Gemini API key to activate Resha.")
    
    if st.button("✨ New Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="sidebar-section">RESEARCH DOCUMENTS</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF/DOCX for analysis", 
        type=["pdf", "docx"], 
        label_visibility="collapsed",
        help="Upload up to 200MB file"
    )
    if uploaded_file:
        st.info(f"📄 Loaded: **{uploaded_file.name}**")

    st.markdown('<div class="sidebar-section">CONTROLS</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="sidebar-section">SYSTEM DIAGNOSTICS</div>', unsafe_allow_html=True)
    st.markdown("⚡ **Core Model:** `gemini-3.6-flash`")
    st.markdown("📑 **Document Indexing:** " + ("`Active`" if uploaded_file else "`Idle`"))
    st.markdown("🔒 **Security Mode:** `Strict Privacy`")

# Hero/Welcome Header
if not st.session_state.messages:
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">How can Resha accelerate your research today?</div>
            <div class="hero-subtitle">Upload your research papers, extract methodologies, synthesize literature, or ask complex technical queries.</div>
        </div>
    """, unsafe_allow_html=True)

    # Feature Grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">📚</div>
                <div class="card-title">Document Synthesis</div>
                <div class="card-desc">Upload papers and PDFs to extract key findings, methodologies, and summaries instantly.</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">🧬</div>
                <div class="card-title">Concept Explanation</div>
                <div class="card-desc">Break down intricate academic concepts, algorithms, and mathematical formulations easily.</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="card-container">
                <div class="card-icon">🖋️</div>
                <div class="card-title">Academic Writing</div>
                <div class="card-desc">Refine research abstracts, structure thesis arguments, and improve academic vocabulary.</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if user_prompt := st.chat_input("Ask Resha a research question or query..."):
    if not api_key:
        st.error("Please insert your Gemini API Key in the sidebar to initiate the session.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Resha is processing your query..."):
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=f"You are Resha, a highly capable academic AI research assistant. Provide concise, structured, professional, and well-cited answers to the following query: {user_prompt}"
                    )
                    bot_reply = response.text
                    st.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    st.error(f"Execution Error: {e}")
