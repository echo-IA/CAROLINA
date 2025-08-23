# docs/scripts/data_utils.py
import re
import pandas as pd


def transform_attendance(column: pd.Series) -> pd.Series:
    """
    Standardize attendance to 'Onsite' or 'Online' (case/space tolerant).
    """
    mapping = {
        'in person': 'Onsite',
        'online': 'Online',
    }
    return column.apply(
        lambda x: mapping.get(str(x).strip().lower(), x) if pd.notnull(x) else x
    )


def normalize_affiliation(column: pd.Series) -> pd.Series:
    """
    Normalize common affiliation variants/typos.
    - UCL -> University College London
    - Princeton / prnceton -> Princeton University
    - Northeastern / northeadetrn -> Northeastern University
    """
    s = column.fillna("").astype(str).str.strip()

    # Apply case-insensitive regex replacements
    replacements = {
        r'(?i)^\s*ucl\s*$': 'University College London',
        r'(?i)^\s*university\s+college\s+london\s*$': 'University College London',

        r'(?i)^\s*pr(?:i)?nceton(?:\s+(?:univ(?:ersity)?))?\s*$': 'Princeton University',
        r'(?i)^\s*prnceton\s*$': 'Princeton University',

        r'(?i)^\s*northeastern(?:\s+(?:univ(?:ersity)?))?\s*$': 'Northeastern University',
        r'(?i)^\s*northeadetrn\s*$': 'Northeastern University',
    }
    for pat, repl in replacements.items():
        s = s.str.replace(pat, repl, regex=True)

    # Title-case simple one-word entries like 'princeton' that slipped through
    s = s.replace({'': None})
    return s


def extract_surname(name: str) -> str:
    """
    Extract surname from a full name, handling common prefixes.
    """
    parts = str(name).split()
    if not parts:
        return ""
    parts.reverse()
    surname_parts = [parts[0]]

    prefixes = {
        'van', 'van der', 'van de', 'de', 'le', 'la',
        'van', 'Van', 'Van der', 'Van Der', 'Van De', 'De'
    }
    for part in parts[1:]:
        if part.lower() in {p.lower() for p in prefixes}:
            surname_parts.append(part)
        else:
            break
    return ' '.join(reversed(surname_parts))


def sort_participant_data(
    data: pd.DataFrame,
    name: str = "Name",
    surname: str = "Surname",
    affiliation: str = "Affiliation",
    attendance: str = "Attendance",
    exclude_surnames=None,
) -> pd.DataFrame:
    """
    Clean and sort participant data, normalize affiliations,
    standardize attendance, and exclude specified surnames.

    Returns columns: ['No.', 'Participant', 'Affiliation', 'Attendance']
    """
    if exclude_surnames is None:
        exclude_surnames = ["Tierney"]  # exclude Tierney by default (case-insensitive)

    # Standardize attendance values
    if attendance in data.columns:
        data[attendance] = transform_attendance(data[attendance])

    # Normalize affiliations
    if affiliation in data.columns:
        data[affiliation] = normalize_affiliation(data[affiliation])

    # Build Participant column
    data['Participant'] = (
        data.get(name, "").fillna("").astype(str).str.strip()
        + " "
        + data.get(surname, "").fillna("").astype(str).str.strip()
    ).str.strip()

    # Drop the original name columns if present
    drop_cols = [c for c in [name, surname] if c in data.columns]
    if drop_cols:
        data = data.drop(columns=drop_cols)

    # Compute Surname for sorting & filtering
    data['Surname'] = data['Participant'].apply(extract_surname)

    # Exclude undesired surnames (case-insensitive)
    if exclude_surnames:
        excl = {s.lower() for s in exclude_surnames}
        data = data[~data['Surname'].str.lower().isin(excl)]

    # Sort by surname
    data = data.sort_values(by='Surname', kind='mergesort').reset_index(drop=True)

    # Numbering
    data['No.'] = data.index + 1

    # Final selection
    cols = ['No.', 'Participant', affiliation, attendance]
    cols = [c for c in cols if c in data.columns]
    data_sorted = data[cols]

    return data_sorted


def build_participants_htmlold(data_sorted: pd.DataFrame) -> str:
    html_table = data_sorted.to_html(index=False, border=0, classes='participants-table', escape=False)
    return f"""---
        layout: default
        title: Participants
        order: 5
        ---
        <h2>Workshop Participants</h2>
        {html_table}
        """


def build_participants_html(data_sorted: pd.DataFrame, images=None, menu_items=None) -> str:
    front = """---
layout: default
title: Participants
order: 5
---
"""
    if isinstance(images, str):
        images = [images]

    items = list(menu_items) if menu_items else []
    items.append(("Participants", "#participants"))
    if images:
        items.append(("Statistics", "#statistics"))

    seen, deduped = set(), []
    for label, href in items:
        key = (label.strip().lower(), href.strip().lower())
        if key not in seen:
            seen.add(key)
            deduped.append((label, href))

    menu_block = ""
    if deduped:
        items_html = "\n".join(f'  <li><a href="{href}">{label}</a></li>' for label, href in deduped)
        menu_block = f"""
<details>
  <summary><strong>Mini menu</strong></summary>
  <ul>
{items_html}
  </ul>
</details>
<br>
"""

    stats_block = ""
    if images:
        imgs = "\n".join(f'<p align="center"><img src="{img}" width="1000"></p><br>' for img in images)
        stats_block = f"""
<h2 id="statistics">Statistics</h2>
{imgs}
"""

    table_html = data_sorted.to_html(index=False, border=0, classes="participants-table", escape=False)
    participants_block = f"""
<h2 id="participants">Workshop Participants</h2>
{table_html}
"""

    return front + menu_block + stats_block + participants_block
