import streamlit as st

def render_navigation_sidebar():
    with st.sidebar:
        st.title("Gemini")
        if st.button("New Chat", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
        st.button("Library", use_container_width=True)
        st.button("Video", use_container_width=True)
        st.button("Search Chats", use_container_width=True)
        
        st.divider()
        st.subheader("Recent")
        
        user_queries = [msg.get("user_prompt", "") for msg in st.session_state.get("ledger", {}).get("turn_history", [])]
        if not user_queries:
            st.caption("No recent queries.")
        else:
            for i, query in enumerate(reversed(user_queries)):
                display_text = query[:30] + "..." if len(query) > 30 else query
                st.button(display_text, key=f"recent_query_{i}", use_container_width=True)
