import re

def find_word_position(text, reference_text, word):
    # Normalize whitespace in all inputs
    text = re.sub(r'\s+', ' ', text)
    reference_text = re.sub(r'\s+', ' ', reference_text)
    word = re.sub(r'\s+', ' ', word)

    text_lower = text.lower()
    reference_lower = reference_text.lower()
    word_lower = word.lower()

    # Find the reference text, ignoring whitespace differences
    ref_match = re.search(re.escape(reference_lower).replace(r'\ ', r'\s+'), text_lower)
    if not ref_match:
        return None, None

    ref_start, ref_end = ref_match.span()

    # Adjust ref_end to account for possible whitespace differences
    ref_end = ref_start + len(reference_text)

    # Find the word within the reference text range
    word_pattern = re.escape(word_lower).replace(r'\ ', r'\s+')
    word_match = re.search(word_pattern, text_lower[ref_start:ref_end])

    if not word_match:
        return ref_start, ref_end
    else:
        word_start = ref_start + word_match.start()
        word_end = ref_start + word_match.end()
        return word_start, word_end
