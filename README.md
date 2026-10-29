# Who makes community events happen? (FIT3179 Data Visualisation 2)
Run locally: `python -m http.server 8000` in this folder, then open http://localhost:8000 (charts load JSON, so double-clicking index.html will not work).
Rebuild: `python prepare_data.py`, `python build_national.py`, then `python build_page.py`.
Sources: see the page footer. National numbers in build_national.py are typed from the Volunteering Australia GSS 2025 report; Brisbane numbers are computed from source/brisbane-city-council-events.csv.
Kinds of event: first matching rule wins (see RULES in prepare_data.py).
