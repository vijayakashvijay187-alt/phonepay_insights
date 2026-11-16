"""Place-name cleanup and approximate state centroids for the map view."""


def canonical_place(name: str | None) -> str | None:
    """Fold path slugs and JSON labels onto one lowercase form."""
    if name is None:
        return None
    text = name.strip().lower().replace("-", " ").replace("&", " and ")
    text = " ".join(text.split())
    if not text:
        return None
    return text


# Approximate geographic centers, used only to place states on a scatter map.
STATE_CENTROIDS: dict[str, tuple[float, float]] = {
    "andaman and nicobar islands": (11.74, 92.66),
    "andhra pradesh": (15.91, 79.74),
    "arunachal pradesh": (28.22, 94.73),
    "assam": (26.20, 92.94),
    "bihar": (25.10, 85.31),
    "chandigarh": (30.73, 76.78),
    "chhattisgarh": (21.28, 81.87),
    "dadra and nagar haveli and daman and diu": (20.27, 73.02),
    "delhi": (28.70, 77.10),
    "goa": (15.30, 74.12),
    "gujarat": (22.26, 71.19),
    "haryana": (29.06, 76.09),
    "himachal pradesh": (31.10, 77.17),
    "jammu and kashmir": (33.28, 75.34),
    "jharkhand": (23.61, 85.28),
    "karnataka": (15.32, 75.71),
    "kerala": (10.85, 76.27),
    "ladakh": (34.23, 77.56),
    "lakshadweep": (10.57, 72.64),
    "madhya pradesh": (22.97, 78.66),
    "maharashtra": (19.75, 75.71),
    "manipur": (24.66, 93.91),
    "meghalaya": (25.47, 91.37),
    "mizoram": (23.16, 92.94),
    "nagaland": (26.16, 94.56),
    "odisha": (20.95, 85.10),
    "puducherry": (11.94, 79.81),
    "punjab": (31.15, 75.34),
    "rajasthan": (27.02, 74.22),
    "sikkim": (27.53, 88.51),
    "tamil nadu": (11.13, 78.66),
    "telangana": (18.11, 79.02),
    "tripura": (23.94, 91.99),
    "uttar pradesh": (26.85, 80.95),
    "uttarakhand": (30.07, 79.02),
    "west bengal": (22.99, 87.86),
}
