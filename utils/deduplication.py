def deduplicate_missing_info(existing_registry: list[dict], new_items: list[dict]) -> list[dict]:
    """
    Deduplicates new missing info items against the existing registry 
    by semantic similarity via string matching on description field for MVP.
    """
    # MVP deduplication: exact substring or highly similar text matching
    # A more advanced version would use embedding similarity.
    deduplicated = []
    
    for new_item in new_items:
        new_desc = new_item.get("description", "").lower().strip()
        
        is_duplicate = False
        for existing in existing_registry:
            ex_desc = existing.get("description", "").lower().strip()
            # If new description is a substantial substring or vice versa
            if (len(new_desc) > 10 and len(ex_desc) > 10) and (new_desc in ex_desc or ex_desc in new_desc):
                is_duplicate = True
                break
                
        if not is_duplicate:
            deduplicated.append(new_item)
            
    return deduplicated
