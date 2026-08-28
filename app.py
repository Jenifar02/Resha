import streamlit as st
from google import genai

st.set_page_config(page_title="Research Assistant Chatbot", page_icon="🔬")
st.title("🔬 Research Assistant Chatbot")
st.caption("Powered by Google Gemini API")

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("Please enter your Gemini API Key in the sidebar to start.", icon="🔑")
else:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input("Ask a research question..."):
        st.chat_message("user").markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing research query..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=f"You are an academic research assistant: {user_prompt}"
                    )
                    bot_reply = response.text
                    st.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    st.error(f"Error details: {e}")
                    st.error(f"Error details: {e}")
