def find_word_position(text, reference_text, word):
    text_lower = text.lower()
    reference_lower = reference_text.lower()
    word_lower = word.lower()

    ref_start = text_lower.find(reference_lower)
    if ref_start == -1:
        return None, None

    ref_end = ref_start + len(reference_text)
    
    word_start = text_lower.find(word_lower, ref_start, ref_end)
    
    if word_start == -1:
        return ref_start, ref_end
    else:
        return word_start, word_start + len(word)
