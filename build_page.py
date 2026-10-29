"""Writes index.html (run prepare_data.py and build_national.py first)."""
import json
f = json.load(open('facts.json'))
def row(title, text, specs):
    figs = ''.join(f'<div class="chart" data-spec="specs/{s}.json"></div>' for s in specs)
    return f'<section class="row"><div class="words"><h2>{title}</h2>{text}</div><div class="figs">{figs}</div></section>'
part = lambda t, s: f'<div class="part"><h2>{t}</h2><p>{s}</p></div>'
body = ''.join([
 part('Part 1: Who gives their time', 'Festivals, markets and clubs run on volunteers. Here is who volunteers across Australia.'),
 row('Where Australians volunteer', '<p>About <strong>22.6%</strong> of Australians aged 15 and over volunteered through an organisation in 2025. Tasmania leads at 27.5%, and Victoria is lowest at 21.8%.</p><p>Every state and territory fell since 2020, and the ACT fell most, from 30.9% to 22.0%.</p>', ['map4-states', 'map5-states-change', 'chart12-state-dumbbell']),
 row('Cities, towns and the bush', '<p>People in remote areas are the most likely to volunteer (34.0%), compared with 20.9% in major cities. Small communities lean on their neighbours.</p><p>Volunteering through organisations has fallen from 36.2% in 2010 to 22.6% in 2025.</p>', ['chart13-remoteness', 'chart14-trend']),
 row('Who volunteers, and for what', '<p>People aged 35 to 54 volunteer most, and women aged 35 to 44 lead at 30.5%.</p><p>Sport is the biggest cause at 33.3% of volunteers, followed by religious groups and community or cultural groups, which include many festivals.</p>', ['chart15-age-gender', 'chart16-org-dumbbell']),
 row('What stops people', '<p>The top reason is <strong>no time</strong>: 47% of non-volunteers say so, rising to 57.7% for ages 25 to 44. Half of volunteers say they started because someone they knew was involved or asked them (50.3%).</p><p>Some small figures carry a high margin of error, so read them as a guide.</p>', ['chart17-why-not']),
 part('Part 2: What is on in one city', f'Brisbane City Council lists {f["N"]:,} events between {f["first"]} and {f["last"]}. Here is where, when and for whom they happen.'),
 row('Where events happen', f'<p>About {f["park"]}% of events are held in parks and {f["lib"]}% in libraries, so most of the city\'s social life happens in shared public space.</p><p>Look for the darker squares on the second map: events cluster around the CBD and a handful of suburban centres.</p>', ['map1-venues', 'map2-density']),
 row('When they happen', f'<p>The busiest day is <strong>{f["busy"]}</strong> with {f["busyN"]} events. Only {f["wkend"]}% start on a weekend, so this is a weekday city.</p><p>The maps on the right split the same venues by weekday and weekend.</p>', ['chart4-calendar', 'chart5-time-of-day', 'map3-weekday-weekend']),
 row('What kinds of events', f'<p>{f["topCat"]} is the biggest group at {f["topCatPct"]}% of events. Only {f["festN"]} listings are tagged as festivals, so big celebrations sit on top of a much larger base of everyday community activity.</p><p>Click a kind in the stream chart to follow it through the weeks.</p>', ['chart8-categories', 'chart7-stream', 'chart9-age', 'chart10-venue-matrix']),
 row('What it takes to join', f'<p><strong>{f["free"]}%</strong> of events are free, so cost is rarely a barrier. Booking is a bigger hurdle for some kinds of event than others.</p>', ['chart6-cost-waffle', 'chart11-booking'])])
html = f'''<!DOCTYPE html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Who makes community events happen? Volunteering across Australia and a month of events in Brisbane</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=Source+Serif+4:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css"></head>
<body><header class="hero"><h1>Who makes community events happen?</h1>
<p class="lede">Festivals get the headlines, but community life runs on volunteers and thousands of smaller gatherings. First, who gives their time across Australia. Then, what that looks like in one city.</p></header>
<main>{body}</main>
<footer>
<p><strong>Data source 1.</strong> Volunteering: Australian Bureau of Statistics, General Social Survey 2025 (released 6 May 2026), as reported in Volunteering Australia, <em>Volunteering Statistics: General Social Survey 2025</em> (May 2026), Tables 2, 6, 7, 10, 11 and 13 (ABS Tables 6.3, 7.3, 10.3, 11.3, 13.3). Formal volunteering means unpaid work through an organisation. Survey results are estimates.</p>
<p><strong>Data source 2.</strong> Events: Brisbane City Council, <em>Events</em> dataset (brisbane-city-council-events), data.brisbane.qld.gov.au, downloaded [DOWNLOAD DATE]. The export holds the next 2,000 listed events, so the last day is partly cut off. Long-running exhibitions were removed, and events without map coordinates are left out of the maps. The author grouped the council's tags into eight kinds of event.</p>
<p><strong>Boundaries.</strong> Australian state and territory outlines: [ADD SOURCE AND LICENCE OF states.geojson].</p>
<p><strong>Author:</strong> [Your name], FIT3179 Data Visualisation 2, Monash University, [date]. AI tools were used to help write the code and text of this page.</p></footer>
<script src="https://cdn.jsdelivr.net/npm/vega@5.30.0"></script><script src="https://cdn.jsdelivr.net/npm/vega-lite@5.21.0"></script><script src="https://cdn.jsdelivr.net/npm/vega-embed@6.26.0"></script>
<script>
document.querySelectorAll('.chart[data-spec]').forEach(function (el) {{
  vegaEmbed(el, el.dataset.spec, {{ actions: false, renderer: 'svg' }}).catch(function (e) {{
    el.innerHTML = '<p class="note">Could not load ' + el.dataset.spec + '. Open this page from a web server or GitHub Pages, not by double-clicking the file.</p>'; }});
}});
</script></body></html>'''
open('index.html', 'w').write(html)
