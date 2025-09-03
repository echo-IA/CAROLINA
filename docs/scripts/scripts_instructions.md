# Building the Website Pages

1) **Update data**
   - Edit your CSVs in `docs/input_data/` (e.g., `participant_list_web.csv`, schedule CSV).
   - Make sure column names match what the scripts expect **or** adjust the script(s) accordingly.

2) **Build pages**
   - Run the script(s) from the repo root:
     ```bash
     python docs/scripts/build_participants_page.py
     # (and any other builder, e.g.)
     # python docs/scripts/build_schedule_page.py
     ```

3) **Publish**
   ```bash
   git add -A
   git commit -m "update pages"
   git push
