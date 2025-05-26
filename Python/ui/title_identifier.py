import os
from Python.ui.name_utils import replace_illegal_chars
from Python.ui.name_processor import NameProcessor

def identify_title_for_executable(exec_path, source_dirs, folder_exclude_set, release_groups_set):
    """
    For a given executable, walk up the directory tree, skipping folder_exclude_set dirs,
    and return the best candidate directory and its transformed name.
    If the root/source dir is reached, use a fallback naming rule.
    """
    exec_path = os.path.abspath(exec_path)
    exec_dir = os.path.dirname(exec_path)
    source_dirs = [os.path.abspath(d) for d in source_dirs]
    
    # Create a name processor
    name_processor = NameProcessor(
        release_groups_set=release_groups_set,
        folder_exclude_set=folder_exclude_set
    )
    
    # Process the executable path
    result = name_processor.process_executable(exec_path)
    
    return {
        'candidate_dir': result['candidate_dir'],
        'transformed_name': result['display_name'],
        'fallback': result['is_fallback']
    }

def get_good_name(path, exclfls=None, rabsol=None, absol=None, rlspfx=None, rlsifx=None, triend=None, rlsgrps=None):
    """
    Multi-stage name extraction and cleaning inspired by AHK GETGOODNAME.
    - path: full path to executable or directory
    - exclfls, rabsol, absol: exclusion lists (set or list)
    - rlspfx: list of delimiters to split for tag culling
    - rlsifx, triend, rlsgrps: lists of known suffixes/groups to remove
    Returns: (cleaned_name, abbreviation)
    """
    import os
    import re
    # Helper: sanitize a segment
    def strip_var(name):
        name = name.replace(',', '').replace('/', '')
        name = name.replace('&', 'and')
        for ch in ['!', '$', '%', '@', '+', '~', '#', ';', '`', '"']:
            name = name.replace(ch, '')
        name = re.sub(r'[_()\[\]{}\'\-\s\.]', '', name)
        return name

    # 1. Reverse traverse path, sanitize, and select best candidate
    segments = [seg for seg in os.path.normpath(path).split(os.sep) if seg]
    candidate = None
    for seg in reversed(segments):
        sanitized = strip_var(seg)
        if not sanitized:
            continue
        if exclfls and sanitized in exclfls:
            continue
        if rabsol and any(sanitized in r for r in rabsol):
            continue
        if absol and any(sanitized in a for a in absol):
            continue
        candidate = seg
        break
    if not candidate:
        candidate = segments[-1] if segments else ''
    name = candidate

    # 2. Remove version/release tags (using delimiters)
    if rlspfx:
        for delim in rlspfx:
            parts = name.split(delim)
            if len(parts) > 1:
                name = parts[0]
                break
    # Remove version/release tags with regex
    version_patterns = [
        r'(build|bld|release|ver|version|v|earlyaccess|alpha|beta|dev|developer|prerelease)(?:\s*[0-9]+(?:\s*[0-9]+)*[a-z]*)?$',
        r'(demo|trial|playtest|preview|remaster(?:ed)?|hd)$',
    ]
    for pattern in version_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    # 3. Remove known suffixes
    for suffix_list in [rlsifx, triend, rlsgrps]:
        if suffix_list:
            for suffix in suffix_list:
                if name.lower().endswith(suffix.lower()):
                    name = name[: -len(suffix)]

    # 4. Clean up whitespace and delimiters
    name = re.sub(r'[._\-]+', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()

    # 5. Generate abbreviation (first letter of each word)
    abbr = ''.join(word[0] for word in name.split() if word)

    return name, abbr 





