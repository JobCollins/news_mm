from unstructured.cleaners.core import (
    clean,
)

import re


def remove_html_tags(text):
    html_tag_pattern = r"<[^>]+>"
    return re.sub(html_tag_pattern, "", text)


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()

def clean_full(text: str) -> str:
    """
    Cleans the given text by applying the following set of operations:
    - clean (e.g whitespaces)
    - clean_ordered_bullets (eg. bullets)
    - replace_unicode_quotes (eg. quotes)
    - clean_non_ascii_chars (eg. non-ascii characters)
    - remove_punctuation (eg. punctuation)

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    text = clean(
        text=text, lowercase=True, extra_whitespace=True, dashes=True, bullets=True
    )
    return text