import streamlit as st
import re

def render_tagged_response(sentence_tags: list[dict], raw_response: str, grounding_result: dict = None) -> str:
    """Convert sentence_tags list to an HTML string with inline tag spans, preserving full layout."""
    
    use_grounding = grounding_result and grounding_result.get("status") == "completed"
    
    if not sentence_tags and not use_grounding:
        # Just convert basic markdown for uniform appearance
        html = raw_response
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        return f'<div style="white-space: pre-wrap; font-family: inherit; line-height: 1.6; color: #E2E2E2;">{html}</div>'
        
    # Normalize markdown bold and italic to HTML tags so they render inside span blocks
    def md_to_html(text: str) -> str:
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        return text

    # Helper to compare strings by removing non-alphanumeric characters
    def clean_str(s: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

    lines = raw_response.split("\n")
    processed_lines = []
    
    # We will match each line to a tag or claim
    if use_grounding:
        claims = grounding_result.get("claims", [])
        for line in lines:
            if not line.strip():
                processed_lines.append("")
                continue
                
            matched = False
            cleaned_line = clean_str(line)
            
            for claim in claims:
                text = claim.get("claim_text", "")
                cls_type = claim.get("classification", "Unverified")
                
                if cleaned_line and (clean_str(text) in cleaned_line or cleaned_line in clean_str(text)):
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
                        
                    html_line = md_to_html(line)
                    span = (
                        f'<span class="{css_class}" '
                        f'title="{tooltip}">'
                        f'{html_line}'
                        f'<sup style="font-size:0.65em; margin-left:2px;">{icon}</sup>'
                        f'</span>'
                    )
                    processed_lines.append(span)
                    matched = True
                    break
            
            if not matched:
                processed_lines.append(md_to_html(line))
    else:
        for line in lines:
            if not line.strip():
                processed_lines.append("")
                continue
                
            matched = False
            cleaned_line = clean_str(line)
            
            for tag_obj in sentence_tags:
                text     = tag_obj.get("text", "")
                tag      = tag_obj.get("tag", "Inferred")
                reasoning = tag_obj.get("reasoning", "")
                
                if cleaned_line and (clean_str(text) in cleaned_line or cleaned_line in clean_str(text)):
                    css_class = "tag-reasoned" if tag == "Reasoned" else "tag-inferred"
                    icon      = "" if tag == "Reasoned" else "~"
                    tooltip   = reasoning.replace('"', '&quot;')
                    
                    html_line = md_to_html(line)
                    span = (
                        f'<span class="{css_class}" '
                        f'title="{tooltip}" '
                        f'data-tag="{tag}">'
                        f'{html_line}'
                        f'<sup style="font-size:0.65em; margin-left:2px;">{icon}</sup>'
                        f'</span>'
                    )
                    processed_lines.append(span)
                    matched = True
                    break
            
            if not matched:
                processed_lines.append(md_to_html(line))

    # Wrap the entire output in a pre-wrap div to preserve vertical spacing and indentation
    final_html = "\n".join(processed_lines)
    return f'<div style="white-space: pre-wrap; font-family: inherit; line-height: 1.6; color: #E2E2E2;">{final_html}</div>'

