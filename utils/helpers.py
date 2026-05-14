import re

def clean_text(text: str) -> str:
    """Removes punctuation and lowercases the text for parsing."""
    text = text.lower()
    return re.sub(r'[^\w\s]', '', text).strip()

def fuzzy_match(intent: str, command: str, threshold=0.85) -> bool:
    """
    Standardizes thresholds to prevent difflib crashes and performs 
    fuzzy string matching between an intent and a command.
    """
    # 1. FORCE NORMALIZE: Ensure threshold is strictly 0.0 - 1.0 for difflib
    norm_threshold = threshold if threshold <= 1.0 else threshold / 100.0
    
    # 2. Preparation: Lowercase and strip whitespace
    intent = intent.lower().strip()
    command = command.lower().strip()
    
    # Simple direct match first
    if intent in command:
        return True

    # 3. thefuzz matching (uses 0-100 scale)
    try:
        from thefuzz import fuzz
        fuzz_threshold = norm_threshold * 100
        # token_set_ratio is best for variable voice commands
        ratio = fuzz.token_set_ratio(intent, command)
        if ratio >= fuzz_threshold:
            return True
    except ImportError:
        pass
        
    # 4. difflib matching (uses 0.0-1.0 scale)
    import difflib
    intent_words = intent.split()
    command_words = command.split()
    
    for word in command_words:
        # Crucial: Use norm_threshold to satisfy difflib's [0.0, 1.0] requirement
        matches = difflib.get_close_matches(word, intent_words, n=1, cutoff=norm_threshold)
        if matches:
            return True
            
    return False

def parse_percentage(text: str) -> int:
    """Extracts a percentage number from text. Default to 50 if none found."""
    # Matches "50 percent" or "50%"
    match = re.search(r'(\d+)\s*(percent|%)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Fallback for just a standalone number
    match_num = re.search(r'(\d+)', text)
    if match_num:
        val = int(match_num.group(1))
        # Assuming typical values between 0 and 100 for volume/brightness
        if 0 <= val <= 100:
            return val
            
    return 50 # Default safe fallback