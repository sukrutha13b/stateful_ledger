import streamlit as st

def apply_styles():
    st.markdown("""<style>
/* Safe column styling - prevents layout collapsing while keeping clear separation */
[data-testid="column"]:nth-child(2) {
    border-left: 1px solid #3C4043;
    padding-left: 1.5rem;
}

/* Premium Sentence tag styling with high-contrast colored text and soft background tint */
.tag-reasoned {
    background-color: rgba(76, 175, 80, 0.15) !important;
    color: #81c784 !important;
    border-bottom: 2px solid #4caf50 !important;
    padding: 2px 4px !important;
    border-radius: 4px !important;
    display: inline-block;
    margin: 1px 0;
}

.tag-inferred {
    background-color: rgba(255, 152, 0, 0.15) !important;
    color: #ffb74d !important;
    border-bottom: 2px dashed #ff9800 !important;
    padding: 2px 4px !important;
    border-radius: 4px !important;
    display: inline-block;
    margin: 1px 0;
}

.tag-grounded {
    background-color: rgba(33, 150, 243, 0.15) !important;
    color: #64b5f6 !important;
    border-bottom: 2px solid #2196f3 !important;
    padding: 2px 4px !important;
    border-radius: 4px !important;
    display: inline-block;
    margin: 1px 0;
}

.tag-contested {
    background-color: rgba(233, 30, 99, 0.15) !important;
    color: #f06292 !important;
    border-bottom: 2px solid #e91e63 !important;
    padding: 2px 4px !important;
    border-radius: 4px !important;
    display: inline-block;
    margin: 1px 0;
}

.tag-unverified {
    background-color: rgba(156, 39, 176, 0.15) !important;
    color: #ba68c8 !important;
    border-bottom: 2px dotted #9c27b0 !important;
    padding: 2px 4px !important;
    border-radius: 4px !important;
    display: inline-block;
    margin: 1px 0;
}
</style>""", unsafe_allow_html=True)

