import re
import os

# Keep these constants
ILLEGAL_WINDOWS_CHARS = '<>:"/\\|?*'
PIPE_CHAR = '|'
SAFE_PIPE_CHAR = '\u2502'  # U+2502

# Keep these basic utility functions
def replace_illegal_chars(name: str, replacement: str = " - ") -> str:
    """Replace illegal Windows filename characters with a replacement string"""
    for ch in ILLEGAL_WINDOWS_CHARS:
        name = name.replace(ch, replacement)
    return name

def display_pipe_safe(name: str) -> str:
    """Replace pipe characters with a display-safe alternative"""
    return name.replace(PIPE_CHAR, " - ")

def save_pipe_safe(name: str) -> str:
    """Replace pipe characters with a safe Unicode alternative for saving"""
    return name.replace(PIPE_CHAR, SAFE_PIPE_CHAR)

def make_safe_filename(name: str) -> str:
    """
    Convert a string to a safe filename by removing illegal characters
    and applying title case.
    
    Args:
        name: The name to convert
        
    Returns:
        A safe filename
    """
    if not name:
        return ""
    
    # Replace illegal characters with spaces
    result = replace_illegal_chars(name)
    
    # Apply title case
    result = title_case_and_cleanup(result)
    
    # Remove leading/trailing whitespace
    result = result.strip()
    
    return result

def normalize_name_for_matching(name: str, stemmer=None) -> str:
    """
    Normalize a name for matching purposes.
    
    Args:
        name: The name to normalize
        stemmer: Optional Porter stemmer for word stemming
        
    Returns:
        Normalized name for matching
    """
    from Python.ui.name_processor import NameProcessor
    
    # Create a name processor (without sets since we're just normalizing)
    name_processor = NameProcessor()
    
    # Get the normalized name - handle stemmer parameter
    if hasattr(name_processor, 'get_match_name_with_stemmer'):
        return name_processor.get_match_name_with_stemmer(name, stemmer)
    else:
        # Fall back to the regular method if the stemmer-aware one doesn't exist
        return name_processor.get_match_name(name)

def title_case_and_cleanup(name: str) -> str:
    """
    Apply proper title case and clean up the name.
    Handles apostrophes and special cases correctly.
    
    Args:
        name: The name to process
        
    Returns:
        Name in title case with clean spacing
    """
    if not name:
        return ""
    
    # First, normalize spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Split the name into words
    words = name.split()
    
    # Define words that should not be capitalized (unless first or last word)
    non_cap_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 
                     'to', 'from', 'by', 'of', 'in', 'with', 'as'}
    
    # Process each word
    for i, word in enumerate(words):
        # Skip empty words
        if not word:
            continue
        
        # Always capitalize first and last word
        if i == 0 or i == len(words) - 1 or word.lower() not in non_cap_words:
            # Handle apostrophes correctly - don't capitalize after apostrophe
            if "'" in word:
                parts = word.split("'")
                # Capitalize first part
                if parts[0]:
                    parts[0] = parts[0][0].upper() + parts[0][1:].lower()
                # Keep second part lowercase if it's a suffix like 's
                if len(parts) > 1 and parts[1] and len(parts[1]) <= 2:
                    parts[1] = parts[1].lower()
                elif len(parts) > 1 and parts[1]:
                    parts[1] = parts[1][0].upper() + parts[1][1:].lower()
                
                words[i] = "'".join(parts)
            else:
                # Normal word - capitalize first letter
                if word:
                    words[i] = word[0].upper() + word[1:].lower()
        else:
            # Non-capitalized word (like "of", "the", etc.)
            words[i] = word.lower()
    
    # Join the words back together
    name = ' '.join(words)
    
    # Handle special cases like "iPhone", "macOS", etc.
    special_cases = {
        "Iphone": "iPhone",
        "Ipad": "iPad",
        "Ipod": "iPod",
        "Macos": "macOS",
        "Ios": "iOS",
        "Tvos": "tvOS",
        "Watchos": "watchOS"
    }
    
    for wrong, right in special_cases.items():
        name = re.sub(r'\b' + wrong + r'\b', right, name)
    
    return name



