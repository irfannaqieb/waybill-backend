import spacy
import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\+?\d[\d\s\-]{7,}\d")

nlp = spacy.load("en_core_web_sm")

PII_ENTITIES = {"PERSON", "ORG", "GPE", "LOC", "DATE"}


def redact_pii(text: str):
    # regex based redaction first
    text = EMAIL.sub("[REDACTED_EMAIL]", text)
    text = PHONE.sub("[REDACTED_PHONE]", text)

    doc = nlp(text)
    redacted_text = text

    for ent in reversed(doc.ents):
        if ent.label_ in PII_ENTITIES:
            redacted_text = (
                redacted_text[: ent.start_char]
                + f"REDACTED_{ent.label_}"
                + redacted_text[ent.end_char :]
            )
    return redacted_text
