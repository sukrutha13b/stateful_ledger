import streamlit as st
from ledger.schema import Claim, Paragraph


BADGE_MAP = {
    "grounded": ("(Green)", "Confirmed by multiple sources"),
    "contested": ("(Amber)", "Multiple valid positions exist"),
    "unverified": ("(Red)", "No grounding found - treat as model inference"),
}

TAG_STYLES = {
    "established": ("[fact]", "gray"),
    "reasoned": ("[reasoned]", "blue"),
    "inferred": ("[inferred]", "orange"),
}


def render_claim_badge(claim: Claim) -> str:
    """Return the emoji badge for a claim's classification."""
    badge, _ = BADGE_MAP.get(claim.classification, ("(Red)", "Unknown"))
    return badge


def render_paragraph_with_claims(paragraph: Paragraph, turn_index: int):
    """
    Render a paragraph with inline claim badges and step_type tag.
    """
    # Paragraph text
    st.markdown(paragraph.text)

    # Step type tag
    if paragraph.step_type:
        tag_text, tag_color = TAG_STYLES.get(
            paragraph.step_type, ("[unknown]", "gray")
        )
        st.caption(f":{tag_color}[{tag_text}]")

    # Claim badges
    if paragraph.claims:
        badge_line = " ".join(
            f"{render_claim_badge(c)} `{c.text[:50]}...`"
            if len(c.text) > 50 else f"{render_claim_badge(c)} `{c.text}`"
            for c in paragraph.claims
        )
        st.markdown(badge_line, unsafe_allow_html=True)

        # Expand contested claims
        for claim in paragraph.claims:
            if claim.classification == "contested" and claim.perspectives:
                render_contested_expander(claim, turn_index)

            if claim.overconfidence_flag:
                render_overconfidence_flag(claim)


def render_contested_expander(claim: Claim, turn_index: int):
    """
    Render an expander for a contested claim showing alternative perspectives.
    """
    with st.expander(f"(Amber) Perspectives on: \"{claim.text[:60]}...\""):
        st.markdown("""
        This claim is framed one way here.
        23 alternative framings exist:
        """)
        for i, perspective in enumerate(claim.perspectives, 1):
            st.markdown(f" **Framing {i}:** {perspective}")

        st.caption("The system does not indicate which framing is correct.")
        st.button(
            "Mark as reviewed",
            key=f"reviewed_{claim.claim_id}_{turn_index}"
        )


def render_overconfidence_flag(claim: Claim):
    """
    Render a perspective flag for an overconfident claim.
    """
    st.warning(f"""
    (Amber) **PERSPECTIVE FLAG**

    This claim is presented as settled, but it represents one position
    in an active debate. Alternative framings:

    {"".join(f' {p}' + chr(10) for p in claim.perspectives)}

    The system does not indicate which framing is correct.
    """)
