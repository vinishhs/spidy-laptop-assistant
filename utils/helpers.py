import re

def clean_text(text: str) -> str:
    """Removes punctuation and lowercases the text for parsing."""
    text = text.lower()
    return re.sub(r'[^\w\s]', '', text).strip()

def fuzzy_match(intent: str, command: str, threshold=85) -> bool:
    """
    Returns true if the intent is found inside the command using simple matching.
    For more complex systems, you'd use difflib.SequenceMatcher or thefuzz.
    """
    try:
        from thefuzz import fuzz
        # fuzz.token_set_ratio is resilient to filler words and out of order words
        ratio = fuzz.token_set_ratio(intent, command)
        if ratio >= threshold:
            return True
    except ImportError:
        pass
        
    import difflib
    intent_words = intent.split()
    command_words = command.split()
    
    # Standard subset matching
    if intent in command:
        return True
        
    # Difflib checking for misspelled/STT weirdness
    for word in command_words:
        matches = difflib.get_close_matches(word, intent_words, n=1, cutoff=threshold)
        if matches:
            return True
    return False

def parse_percentage(text: str) -> int:
    """Extracts a percentage number from text. Default to 50 if none found."""
    match = re.search(r'(\d+)\s*(percent|%)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Fallback for just a number
    match_num = re.search(r'(\d+)', text)
    if match_num:
        val = int(match_num.group(1))
        # Assuming typical values between 0 and 100 for volume/brightness
        if 0 <= val <= 100:
            return val
    return 50 # Default safe fallback
