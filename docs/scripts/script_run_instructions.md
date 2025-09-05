---
published: false
---

# Quick build guide

1) **Update data**
   - Edit CSVs in `docs/input_data/` (e.g., `participant_list_web.csv`, schedule CSV).
   - Make sure column names match what the scripts expect **or** update the script(s) to your column names.

2) **Build pages & assets**
   - From repo root, run the needed scripts:
     ```bash
     # pages
     python docs/scripts/build_participants_page.py
     python docs/scripts/build_schedule_page.py    # if you have one

     # assets (logos, nametags, plots like participant stats)
     python docs/scripts/build_logo.py
     python docs/scripts/build_nametags.py
     python docs/scripts/plot_participant_stats.py
     ```
   - Ensure each script reads the correct input file(s) and that your CSVs contain the required columns.

3) **Publish**
   ```bash
   git add -A
   git commit -m "update pages and assets"
   git push
