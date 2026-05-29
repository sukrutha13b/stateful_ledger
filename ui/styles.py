import streamlit as st

def apply_styles():
    st.markdown("""<style>
/* Make col_ledger sticky/scrollable */
[data-testid="column"]:nth-child(2) {
    position: sticky;
    top: 0;
    max-height: 100vh;
    overflow-y: auto;
    border-left: 1px solid #e0e0e0;
    padding-left: 1rem;
}

/* Sentence tag styling */
.tag-reasoned {
    background-color: #e8f5e9;
    border-bottom: 2px solid #4caf50;
    padding: 1px 2px;
    border-radius: 2px;
}
.tag-inferred {
    background-color: #fff8e1;
    border-bottom: 2px dashed #ff9800;
    padding: 1px 2px;
    border-radius: 2px;
}
.tag-grounded    { background: #e3f2fd; border-bottom: 2px solid #2196f3; }
.tag-contested   { background: #fce4ec; border-bottom: 2px solid #e91e63; }
.tag-unverified  { background: #f3e5f5; border-bottom: 2px dotted #9c27b0; }
</style>""", unsafe_allow_html=True)
