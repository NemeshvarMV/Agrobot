import difflib
from langdetect import detect
from .models import SymptomEntry

try:
    from googletrans import Translator
    translator = Translator()
except Exception:
    translator = None

try:
    import language_tool_python
    tool = language_tool_python.LanguageTool('en-US')
except Exception:
    tool = None

SUPPORTED_LANGS = ["en", "ta", "hi", "kn", "te", "ml"]


def detect_language(text):
    try:
        lang = detect(text)
        if lang not in SUPPORTED_LANGS:
            return "en"
        return lang
    except Exception:
        return "en"

def translate_to_en(text, src_lang):#-->transate to eng for searching in db

    if src_lang.startswith("en"):
        return text
    if translator:
        try:
            return translator.translate(text, src="auto", dest="en").text
        except Exception:
            pass
    return text

def translate_from_en(text, dest_lang): #--> translte to farmer prefrd lng
    if dest_lang.startswith("en"):
        return text
    if translator:
        try:
            return translator.translate(text, src="en", dest=dest_lang).text
        except Exception:
            pass
    return text

def grammar_check(text):
    if tool:
        try:
            matches = tool.check(text)
            return language_tool_python.utils.correct(text, matches)
        except Exception:
            return text
    return text


def find_closest_symptoms(text):

    text = text.lower()
    tokens = text.split()
    matches = []

    db_entries = SymptomEntry.objects.all()
    for entry in db_entries:
        symptom = entry.symptom.lower()

        if symptom in text:
            matches.append(entry)
            continue


        ratio = difflib.SequenceMatcher(None, text, symptom).ratio()
        if ratio > 0.6:
            matches.append(entry)
            continue

        for token in tokens:
            token_ratio = difflib.SequenceMatcher(None, token, symptom).ratio()
            if token_ratio > 0.6:
                matches.append(entry)
                break

    return list(set(matches))


def construct_sentence_from_db(entry):
    causes = entry.possible_causes or "Not available"
    treatments = entry.treatments.replace("|", "; ") if entry.treatments else "Not available"
    sentence = (
        f"Symptom detected: {entry.symptom}.\n"
        f"Possible causes include: {causes}.\n"
        f"Suggested treatments: {treatments}."
    )
    return grammar_check(sentence)


def generate_response_from_text(user_text):
    lang = detect_language(user_text)
    en_text = translate_to_en(user_text, lang)
    matches = find_closest_symptoms(en_text)
    if not matches:
        response = "Sorry, I couldn't recognize the symptoms. Please describe the leaf color, spots, or other visible signs."
    else:
        response_parts = []
        for entry in matches:
            sentence = construct_sentence_from_db(entry)
            response_parts.append(sentence)
        response = "\n\n".join(response_parts)
    response = translate_from_en(response, lang)
    return response

