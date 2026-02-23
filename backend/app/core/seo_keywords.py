"""SEO keyword corpus and helpers."""
from __future__ import annotations


BASE_KEYWORDS = [
    "graminhub",
    "rural marketplace",
    "village supplier network",
    "construction materials supplier",
    "cement supplier",
    "balu supplier",
    "sand supplier",
    "gitti supplier",
    "stone chips supplier",
    "brick supplier",
    "sariya supplier",
    "steel supplier",
    "aggregate supplier",
    "ready mix concrete",
    "jcb booking",
    "excavator booking",
    "loader booking",
    "road roller booking",
    "tractor trolley booking",
    "tipper truck booking",
    "truck booking",
    "mini truck booking",
    "tempo booking",
    "car booking",
    "travel booking",
    "bus booking",
    "equipment rental",
    "generator rental",
    "water tanker rental",
    "crane rental",
    "borewell machine rental",
    "soil filling service",
    "local transport service",
    "whatsapp booking supplier",
    "supplier near me",
    "supplier contact number",
]

HINDI_KEYWORDS = [
    "सीमेंट सप्लायर",
    "बालू सप्लायर",
    "गिट्टी सप्लायर",
    "ईंट सप्लायर",
    "सरिया सप्लायर",
    "ट्रक बुकिंग",
    "कार बुकिंग",
    "ट्रैवल बुकिंग",
    "जेसीबी बुकिंग",
    "एक्सकेवेटर किराया",
    "उपकरण किराया",
    "निर्माण सामग्री",
    "गांव सप्लायर",
    "लोकल सप्लायर",
]

LOCATION_TERMS = [
    "near me",
    "in india",
    "in uttar pradesh",
    "in bihar",
    "in jharkhand",
    "in madhya pradesh",
    "in chhattisgarh",
    "in rajasthan",
    "in delhi ncr",
    "in lucknow",
    "in varanasi",
    "in sonbhadra",
]

INTENT_TERMS = [
    "price",
    "rate",
    "contact",
    "booking",
    "service",
    "whatsapp",
]


def _unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        normalized = " ".join(item.split()).strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(item.strip())
    return ordered


def build_seo_keywords(limit: int = 260) -> list[str]:
    generated: list[str] = []
    generated.extend(BASE_KEYWORDS)
    generated.extend(HINDI_KEYWORDS)

    for base in BASE_KEYWORDS:
        for location in LOCATION_TERMS:
            generated.append(f"{base} {location}")

    for base in BASE_KEYWORDS:
        for intent in INTENT_TERMS:
            generated.append(f"{base} {intent}")

    keywords = _unique_keep_order(generated)
    return keywords[:limit]


SEO_KEYWORDS = build_seo_keywords(limit=260)
SEO_META_KEYWORDS = ", ".join(SEO_KEYWORDS)
