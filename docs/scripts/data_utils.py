import pandas as pd


def transform_attendance(column):
    """
    Standardize attendance responses to 'Onsite' or 'Online',
    case-insensitive and whitespace-tolerant.
    """
    mapping = {
        'in person': 'Onsite',
        'online': 'Online'
    }
    return column.apply(
        lambda x: mapping.get(str(x).strip().lower(), x)
        if pd.notnull(x) else x
    )


def extract_surname(name):
    """
    Extracts the surname from a full name, correctly handling known surname prefixes.
    """
    parts = name.split()
    # Reverse the name parts to start checking from the end
    parts.reverse()
    surname_parts = [parts[0]]  # Start with the last part of the name

    # Define a list of common surname prefixes
    # in case you want to sort by surname
    surname_prefixes = ['van', 'van der', 'de', 'le', 'la', 'van de', 'Van', 'Van der', 'Van Der', 'Van De', 'De']

    # Check if the preceding part is a known prefix and add it to the surname if so
    for part in parts[1:]:
        if part.lower() in surname_prefixes:
            surname_parts.append(part)
        else:
            break  # Stop if a part is not a known prefix

    # Return the surname, which is the last name part and any prefixes, reversed back to the correct order
    return ' '.join(reversed(surname_parts))


def sort_participant_data(data,
                          name="Name",
                          surname="Surname",
                          affiliation="Affiliation",
                          attendance="Attendance"):
    """
    Clean and sort participant data.

    Parameters
    ----------
    data : pd.DataFrame
        Must contain columns: [name, surname, affiliation, attendance]
    name : str
        Column name for first names.
    surname : str
        Column name for surnames.
    affiliation : str
        Column name for institutional affiliation.
    attendance : str
        Column name for attendance type.

    Returns
    -------
    data_sorted : pd.DataFrame
        Sorted DataFrame with columns ['No.', 'Participant',
                                       'Affiliation', 'Attendance']
    """

    # Standardize attendance values
    data[attendance] = transform_attendance(data[attendance])

    # Create Participant column
    data['Participant'] = (
            data[name].fillna('').str.strip()
            + ' '
            + data[surname].fillna('').str.strip()
    ).str.strip()

    # Drop redundant name columns
    data = data.drop(columns=[name, surname])

    # Add surname for sorting
    data['Surname'] = data['Participant'].apply(extract_surname)

    # Sort
    data = data.sort_values(by='Surname').reset_index(drop=True)

    # Add numbering
    data['No.'] = data.index + 1

    # Final selection
    data_sorted = data[['No.', 'Participant', affiliation, attendance]]

    return data_sorted


def build_participants_htmlold(data_sorted):
    """
    Build HTML page content with participants table.

    Parameters
    ----------
    data_sorted : pd.DataFrame
        Cleaned and sorted participant DataFrame.

    Returns
    -------
    html_content : str
        The generated HTML page content.
    """
    html_table = data_sorted.to_html(
        index=False, border=0, classes='participants-table', escape=False
    )

    html_content = f"""---
        layout: default
        title: Participants
        order: 5
        ---
        <h2>Workshop Participants</h2>
        {html_table}
        """
    return html_content

def build_participants_html(data_sorted, images=None, menu_items=None):
    """
    Build Participants page with an optional mini-menu and optional Statistics images.
    - If `images` is provided (str or list[str]), a single Statistics section is shown.
    - The mini-menu includes 'Statistics' only once (if images) and 'Participants' only once.
    """
    # front matter
    front = """---
layout: default
title: Participants
order: 5
---
"""

    # normalize images to list
    if isinstance(images, str):
        images = [images]

    # ------ build menu with dedup ------
    items = list(menu_items) if menu_items else []
    # ensure 'Participants' exists once
    items.append(("Participants", "#participants"))

    # add 'Statistics' iff we have images AND it's not already present
    if images:
        items.append(("Statistics", "#statistics"))

    # dedupe by href (case-insensitive) preserving order
    seen = set()
    deduped = []
    for label, href in items:
        key = (label.strip().lower(), href.strip().lower())
        if key not in seen:
            seen.add(key)
            deduped.append((label, href))

    # render menu only if there's at least one item
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

    # ------ statistics section (single section, many images) ------
    stats_block = ""
    if images:
        imgs = "\n".join(
            f'<p align="center"><img src="{img}" width="1000"></p><br>'
            for img in images
        )
        stats_block = f"""
<h2 id="statistics">Statistics</h2>
{imgs}
"""

    # ------ participants table ------
    table_html = data_sorted.to_html(index=False, border=0, classes="participants-table", escape=False)
    participants_block = f"""
<h2 id="participants">Workshop Participants</h2>
{table_html}
"""

    return front + menu_block + stats_block + participants_block
