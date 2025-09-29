import streamlit as st

def add_word_to_list(word):
    if word.strip() and word.strip() not in st.session_state.search_words:
        st.session_state.search_words.append(word.strip())

def remove_word(word):
    if word in st.session_state.search_words:
        st.session_state.search_words.remove(word)


def mock_search(words):
    """Mock search function - replace with your actual search logic"""
    results = {}
    for word in words:
        # Simulate search results
        results[word] = {
            'definitions': [
                f"Definition 1 for '{word}': A detailed explanation of the term.",
                f"Definition 2 for '{word}': Another perspective on the meaning."
            ],
            'synonyms': [f"synonym1_{word}", f"synonym2_{word}", f"synonym3_{word}"],
            'examples': [
                f"Example sentence 1 using '{word}' in context.",
                f"Example sentence 2 demonstrating '{word}' usage."
            ],
            'related_terms': [f"related1_{word}", f"related2_{word}"]
        }
    return results