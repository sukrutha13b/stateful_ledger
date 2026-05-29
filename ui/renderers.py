import streamlit as st
import re

def render_tagged_response(sentence_tags: list[dict], raw_response: str, grounding_result: dict = None) -> str:
    """Convert sentence_tags list to an HTML string with inline tag spans."""
    
    # Simple MVP approach: if grounding is completed, apply those tags instead of internal ones
    # Otherwise apply internal reasoned/inferred tags
    
    use_grounding = grounding_result and grounding_result.get("status") == "completed"
    
    if not sentence_tags and not use_grounding:
        return raw_response
        
    html_parts = []
    
    if use_grounding:
        claims = grounding_result.get("claims", [])
        # Very crude MVP text mapping - typically you'd replace substrings in raw_response
        # For this prototype, we'll just format the claims if available
        for claim in claims:
            cls_type = claim.get("classification", "Unverified")
            text = claim.get("claim_text", "")
            
            if cls_type == "Grounded":
                css_class = "tag-grounded"
                icon = ""
                tooltip = "Grounded by search"
            elif cls_type == "Contested":
                css_class = "tag-contested"
                icon = "(Red)"
                tooltip = "Multiple perspectives exist"
            else:
                css_class = "tag-unverified"
                icon = ""
                tooltip = "No search evidence"
                
            span = (
                f'<span class="{css_class}" '
                f'title="{tooltip}">'
                f'{text}'
                f'<sup style="font-size:0.65em; margin-left:2px;">{icon}</sup>'
                f'</span> '
            )
            html_parts.append(span)
    else:
        for tag_obj in sentence_tags:
            text     = tag_obj.get("text", "")
            tag      = tag_obj.get("tag", "Inferred")
            reasoning = tag_obj.get("reasoning", "")
    
            css_class = "tag-reasoned" if tag == "Reasoned" else "tag-inferred"
            icon      = "" if tag == "Reasoned" else "~"
            tooltip   = reasoning.replace('"', '&quot;')
    
            span = (
                f'<span class="{css_class}" '
                f'title="{tooltip}" '
                f'data-tag="{tag}">'
                f'{text}'
                f'<sup style="font-size:0.65em; margin-left:2px;">{icon}</sup>'
                f'</span> '
            )
            html_parts.append(span)

    return "".join(html_parts)
