import re
from rapidfuzz import fuzz

FOOD_KEYWORDS = [
    "biryani",
    "fried rice",
    "pizza",
    "burger",
    "shawarma",
    "butter chicken",
    "paneer butter masala",
    "masala dosa",
    "idli vada"
]

PROTEIN_KEYWORDS = [
    "chicken",
    "mutton",
    "egg",
    "paneer",
    "prawn"
]

TYPE_KEYWORDS = [
    "veg",
    "non-veg"
]
def fuzzy_extract(query, keywords, threshold=80):
    best_match = None
    best_score = 0
    for keyword in keywords:
        score = fuzz.partial_ratio(
            query.lower(),
            keyword.lower()
        )
        if score > best_score:
            best_score = score
            best_match = keyword

    if best_score >= threshold:
        return best_match
    return None

def extract_filters_rule_based(query: str):
    query = query.lower()
    filters = {
        "name": None,
        "protein": None,
        "restaurant": None,
        "type": None,
        "max_price": None,
        "min_price": None,
        "intent": None
    }

    under_match = re.search(
        r"under\s+(\d+)",
        query
    )
    if under_match:
        filters["max_price"] = int(
            under_match.group(1)
        )
    below_match = re.search(
        r"below\s+(\d+)",
        query
    )
    if below_match:
        filters["max_price"] = int(
            below_match.group(1)
        )

    above_match = re.search(
        r"above\s+(\d+)",
        query
    )

    if above_match:
        filters["min_price"] = int(
            above_match.group(1)
        )

    detected_type = fuzzy_extract(
        query,
        TYPE_KEYWORDS,
        threshold=85
    )
    if detected_type:
        filters["type"] = detected_type
    detected_protein = fuzzy_extract(
        query,
        PROTEIN_KEYWORDS,
        threshold=80
    )
    if detected_protein:
        filters["protein"] = detected_protein
    detected_food = fuzzy_extract(
        query,
        FOOD_KEYWORDS,
        threshold=75
    )
    if detected_food:
        filters["name"] = detected_food

    return filters