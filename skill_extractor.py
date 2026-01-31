import spacy
import re

# Load English tokenizer, tagger, parser and NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading language model for the spaCy POS tagger\n"
        "(don't worry, this will only happen once)")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Predefined skill list (can be expanded)
SKILL_LIST = [
    "python", "java", "c++", "javascript", "html", "css", "sql", "react", "flask", 
    "django", "node.js", "aws", "azure", "docker", "kubernetes", "git", "machine learning",
    "deep learning", "nlp", "spacy", "tensorflow", "pytorch", "pandas", "numpy", 
    "scikit-learn", "data analysis", "tableau", "power bi", "communication", "leadership",
    "problem solving", "agile", "scrum", "project management", "linux", "bash"
]

def extract_skills(text):
    """
    Extracts skills from the given text using NLP and a predefined skill list.
    """
    doc = nlp(text.lower())
    extracted_skills = set()

    # 1. Direct matching from SKILL_LIST
    # Tokenize the text and SKILL_LIST for better matching
    text_tokens = [token.text for token in doc]
    
    for skill in SKILL_LIST:
        # Check if single-word skill is in tokens
        if " " not in skill:
            if skill in text_tokens:
                extracted_skills.add(skill)
        else:
            # Check if multi-word skill is in the raw text
            if skill in text.lower():
                extracted_skills.add(skill)

    # 2. Extract Noun Chunks (potential technical terms) - optional enhancement
    # for chunk in doc.noun_chunks:
    #     clean_chunk = chunk.text.lower().strip()
    #     if clean_chunk in SKILL_LIST:
    #         extracted_skills.add(clean_chunk)

    return list(extracted_skills)
