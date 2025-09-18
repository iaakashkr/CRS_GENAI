# import re

# def detect_labeled_location(query, location_map):
#     found = set()
#     for loc_type, names in location_map.items():
#         pattern = re.compile(rf'\b{loc_type}\s+([\w\- ]+)\b', re.IGNORECASE)
#         for match in pattern.finditer(query):
#             labeled_name = match.group(1).strip().lower()
#             known_names = [n.lower() for n in names]
#             if labeled_name in known_names:
#                 found.add((labeled_name, loc_type))
#             else:
#                 found.add((labeled_name, "invalid"))
#     return found

# def match_locations(query, location_map):
#     matches = []
#     lowered_query = query.lower()
#     for location_type, names in location_map.items():
#         for name in names:
#             if name.lower() in lowered_query:
#                 matches.append((name, location_type))
#     return matches

# def rephrase_query(query, matches, location_map):
#     labeled = detect_labeled_location(query, location_map)
#     matches = sorted(matches, key=lambda x: -len(x[0]))
#     for name, loc_type in matches:
#         name_lc = name.lower()
#         if (name_lc, loc_type) in labeled:
#             continue
#         if (name_lc, "invalid") in labeled:
#             continue
#         already_labeled_pattern = re.compile(rf'\b{loc_type}\s+{re.escape(name)}\b', re.IGNORECASE)
#         if already_labeled_pattern.search(query):
#             continue
#         name_pattern = re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)
#         query = name_pattern.sub(f"{loc_type} {name}", query)
        
#     return query

# def rephrase_question(question):
#     LOCATION_MAP = {
#         "area": ['Adoni Area','Ahamedpur Area','Ahmednagar Area'],
#         "division" : ['Aurangabad Division','Azamgarh Division'],
#         "state": ['Andhra Pradesh','Karnataka','Tamil Nadu'],
#         "zone": ['AP -TS Zone','Aurangabad Zone'],
#         "district": ['Adilabad','Ahmednagar','Ajmer'],
#         "sub-district": ['Adoni','Afzalpur'],
#         "branch": ['AHAMEDPUR-2','ARAKONAM-2']
#     }
#     matches = match_locations(question, LOCATION_MAP)
#     return rephrase_query(question, matches, LOCATION_MAP)

# def add_missing_keywords(query):
#     if re.search(r'\btotal disbursement\b', query, re.IGNORECASE) and "amount" not in query.lower():
#         query = re.sub(r'\btotal disbursement\b', 'total disbursement amount', query, flags=re.IGNORECASE)
#     months_map = {
#         "jan": "January", "feb": "February", "mar": "March",
#         "apr": "April", "may": "May", "jun": "June",
#         "jul": "July", "aug": "August", "sep": "September",
#         "oct": "October", "nov": "November", "dec": "December"
#     }
#     for abbr, full in months_map.items():
#         query = re.sub(rf'\b{abbr}\b', full, query, flags=re.IGNORECASE)
#     rephrased_question = re.sub(
#         r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
#         r'Month \1 \2', query, flags=re.IGNORECASE
#     )

#     return rephrased_question


import re

# ---------------- Location Handling ----------------
def detect_labeled_location(query, location_map):
    """Detect locations in query with labels, mark unknowns as 'invalid'"""
    found = set()
    for loc_type, names in location_map.items():
        pattern = re.compile(rf'\b{loc_type}\s+([\w\- ]+)\b', re.IGNORECASE)
        for match in pattern.finditer(query):
            labeled_name = match.group(1).strip().lower()
            known_names = [n.lower() for n in names]
            if labeled_name in known_names:
                found.add((labeled_name, loc_type))
            else:
                found.add((labeled_name, "invalid"))
    return found

def match_locations(query, location_map):
    """Return all exact location matches in query"""
    matches = []
    lowered_query = query.lower()
    for location_type, names in location_map.items():
        for name in names:
            if name.lower() in lowered_query:
                matches.append((name, location_type))
    return matches

def label_locations_in_query(query, location_map):
    """Main function to label locations in the query"""
    matches = match_locations(query, location_map)
    labeled = detect_labeled_location(query, location_map)
    matches = sorted(matches, key=lambda x: -len(x[0]))  # longer names first

    for name, loc_type in matches:
        name_lc = name.lower()
        if (name_lc, loc_type) in labeled or (name_lc, "invalid") in labeled:
            continue

        already_labeled_pattern = re.compile(rf'\b{loc_type}\s+{re.escape(name)}\b', re.IGNORECASE)
        if already_labeled_pattern.search(query):
            continue

        name_pattern = re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)
        query = name_pattern.sub(f"{loc_type} {name}", query)

    return query

# ---------------- Keyword Handling ----------------
def add_missing_keywords(query):
    """Add missing business keywords & normalize month names"""
    if re.search(r'\btotal disbursement\b', query, re.IGNORECASE) and "amount" not in query.lower():
        query = re.sub(r'\btotal disbursement\b', 'total disbursement amount', query, flags=re.IGNORECASE)

    months_map = {
        "jan": "January", "feb": "February", "mar": "March",
        "apr": "April", "may": "May", "jun": "June",
        "jul": "July", "aug": "August", "sep": "September",
        "oct": "October", "nov": "November", "dec": "December"
    }
    for abbr, full in months_map.items():
        query = re.sub(rf'\b{abbr}\b', full, query, flags=re.IGNORECASE)

    query = re.sub(
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
        r'Month \1 \2', query, flags=re.IGNORECASE
    )
    return query

# ---------------- Orchestrator ----------------
def rephrase_question(question):
    LOCATION_MAP = {
        "area": ['Adoni Area','Ahamedpur Area','Ahmednagar Area'],
        "division" : ['Aurangabad Division','Azamgarh Division'],
        "state": ['Andhra Pradesh','Karnataka','Tamil Nadu'],
        "zone": ['AP -TS Zone','Aurangabad Zone'],
        "district": ['Adilabad','Ahmednagar','Ajmer'],
        "sub-district": ['Adoni','Afzalpur'],
        "branch": ['AHAMEDPUR-2','ARAKONAM-2']
    }

    # 1️⃣ Label locations
    question = label_locations_in_query(question, LOCATION_MAP)

    # 2️⃣ Add missing keywords & normalize
    question = add_missing_keywords(question)

    return question
