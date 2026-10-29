"""Builds data/*.json, specs/*.json and index.html from the Brisbane City Council events CSV."""
import json, math, collections
import pandas as pd

SRC = 'source/brisbane-city-council-events.csv'
W, H = 640, 480
CATS = ['Festivals & culture', 'Arts & music', 'Fitness & wellbeing', 'Nature & green', 'Workshops & tours', 'Library', 'Family', 'Other']
COLS = ['#c2306b', '#7a4bd1', '#138a8a', '#5aa02c', '#f2a900', '#4d8be8', '#e8743b', '#9aa3b5']
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
RULES = [('Festivals & culture', ['Festivals', 'Markets', 'Food', 'Christmas', 'Culture', 'Aboriginal']),
         ('Arts & music', ['Music', 'Performing arts', 'Art', 'Creative', 'Exhibitions', 'Films']),
         ('Nature & green', ['Green']), ('Workshops & tours', ['Workshops', 'Tours']),
         ('Fitness & wellbeing', ['Fitness']), ('Family', ['Family'])]

def pickCategory(row):
    if row['primaryeventtype'] == 'Library event' or 'Library' in str(row['venuetype']):
        return 'Library'
    tags = str(row['event_type'])
    for name, keys in RULES:
        if any(k in tags for k in keys):
            return name
    return 'Other'

def venueGroup(v):
    v = str(v)
    for key, name in [('Library', 'Library'), ('Swimming', 'Swimming pool'), ('Park', 'Park'), ('Community Hall', 'Community hall'), ('Non-Council', 'Non-council venue')]:
        if key in v: return name
    return 'Council venue'

def costGroup(c):
    if c == 'Free': return 'Free'
    if pd.isna(c) or c == 'See website': return 'Not stated'
    return 'Paid'

d = pd.read_csv(SRC, encoding='utf-8-sig')
d['start'] = pd.to_datetime(d.start_datetime, utc=True).dt.tz_convert('Australia/Brisbane')
d['end'] = pd.to_datetime(d.end_datetime, utc=True, errors='coerce').dt.tz_convert('Australia/Brisbane')
totalRows = len(d)
d = d[((d.end - d.start).dt.days <= 7) | d.end.isna()].copy()   # drop long-running exhibitions
d['category'] = d.apply(pickCategory, axis=1)
d['venueGroup'] = d.venuetype.map(venueGroup)
d['costGroup'] = d.cost.map(costGroup)
d['dow'] = d.start.dt.dayofweek.map(lambda i: DAYS[i])
d['hour'] = d.start.dt.hour
d['date'] = d.start.dt.strftime('%Y-%m-%d')
d['weekLabel'] = (d.start.dt.normalize() - pd.to_timedelta(d.start.dt.dayofweek, unit='D')).dt.strftime('%d %b')
d['weekend'] = d.dow.isin(['Sat', 'Sun'])
d['booking'] = d.bookingsrequired.map({'Yes': 'Booking required', 'No': 'No booking'}).fillna('Not stated')
ll = d.geolocation.str.split(',', expand=True).astype(float)
d['lat'], d['lon'] = ll[0].round(4), ll[1].round(4)

def dump(name, obj):
    with open(f'data/{name}.json', 'w') as f: json.dump(obj, f, indent=1)

def recs(df): return df.to_dict('records')
g = d.dropna(subset=['lat'])
# ---- aggregates
dump('daily', recs(d.groupby(['date', 'dow', 'weekLabel']).size().reset_index(name='n')))
dump('daily_category', recs(d.groupby(['date', 'category']).size().reset_index(name='n')))
dump('dow_hour', recs(d.groupby(['dow', 'hour']).size().reset_index(name='n')))
dump('venue_category', recs(d.groupby(['venueGroup', 'category']).size().reset_index(name='n')))
dump('booking', recs(d.groupby(['category', 'booking']).size().reset_index(name='n')))
ages = collections.Counter(a.strip() for s in d.agerange.dropna() for a in s.split(','))
dump('age', [{'ageGroup': k, 'n': v} for k, v in ages.items()])
cats = d.category.value_counts().reset_index(); cats.columns = ['category', 'n']; dump('categories', recs(cats))
cg = d.costGroup.value_counts(); cells = []
order = ['Free', 'Paid', 'Not stated']; seq = []
for k in order: seq += [k] * round(cg.get(k, 0) / len(d) * 100)
seq = (seq + ['Not stated'] * 100)[:100]
dump('waffle', [{'group': s, 'col': i % 10, 'row': i // 10} for i, s in enumerate(seq)])
vg = g.groupby(['lat', 'lon']).agg(n=('subject', 'size'), venue=('venue', lambda s: s.mode().iat[0] if s.notna().any() else 'Venue not named'),
                                  venueType=('venueGroup', lambda s: s.mode().iat[0]), weekend=('weekend', 'sum')).reset_index()
vg['weekday'] = vg.n - vg.weekend; dump('venues', recs(vg.drop(columns='weekend').assign(weekendN=vg.weekend)))
long = pd.concat([vg.assign(dayType='Weekdays (Mon-Fri)', k=vg.weekday), vg.assign(dayType='Weekends', k=vg.weekend)])
dump('venues_daytype', recs(long[long.k > 0][['lat', 'lon', 'dayType', 'k', 'venue']]))
S = 0.02; g = g.assign(gy=(g.lat // S), gx=(g.lon // S))
feats = []
for (gy, gx), c in g.groupby(['gy', 'gx']):
    x0, y0 = gx * S, gy * S
    feats.append({'type': 'Feature', 'properties': {'n': len(c), 'types': int(c.category.nunique())},
                  'geometry': {'type': 'Polygon', 'coordinates': [[[x0, y0], [x0 + S, y0], [x0 + S, y0 + S], [x0, y0 + S], [x0, y0]]]}})
dump('grid', {'type': 'FeatureCollection', 'features': feats})
# ---- map extent
latLo, latHi = g.lat.quantile([.02, .98]); lonLo, lonHi = g.lon.quantile([.02, .98])
cLat, cLon = (latLo + latHi) / 2, (lonLo + lonHi) / 2
k = min(W * .9 / (lonHi - lonLo), H * .9 * math.cos(math.radians(cLat)) / (latHi - latLo))
PROJ = {'type': 'mercator', 'center': [round(cLon, 3), round(cLat, 3)], 'scale': round(k * 180 / math.pi)}
marks = [('CBD', -27.4698, 153.0251), ('Chermside', -27.386, 153.034), ('Indooroopilly', -27.50, 152.973), ('Carindale', -27.505, 153.10), ('Sunnybank', -27.576, 153.058)]
lm = [{'name': n, 'lat': a, 'lon': b} for n, a, b in marks if latLo - .05 < a < latHi + .05 and lonLo - .05 < b < lonHi + .05]

# ---- specs
SC = {'domain': CATS, 'range': COLS}
CFG = {'view': {'stroke': None}, 'font': 'Source Serif 4', 'axis': {'labelFont': 'Source Serif 4', 'titleFont': 'Source Serif 4', 'domain': False, 'tickSize': 0, 'labelFontSize': 12, 'titleFontSize': 12},
       'legend': {'labelFont': 'Source Serif 4', 'titleFont': 'Source Serif 4'}, 'title': {'font': 'Bricolage Grotesque', 'fontSize': 16, 'anchor': 'start', 'subtitleFont': 'Source Serif 4', 'subtitleColor': '#5b6479'}}
def spec(name, title, sub, body):
    s = {'$schema': 'https://vega.github.io/schema/vega-lite/v5.json', 'title': {'text': title, 'subtitle': sub}, 'config': CFG}
    s.update(body)
    with open(f'specs/{name}.json', 'w') as f: json.dump(s, f, indent=2)
def label(t, extra=None):
    m = {'type': 'text', 'font': 'Source Serif 4', 'fontSize': 11, 'color': '#1d2540', 'align': 'left', 'dx': 6, 'dy': -6}; m.update(extra or {}); return m
landLayer = {'data': {'values': lm}, 'mark': label('', {'fontStyle': 'italic'}), 'encoding': {'latitude': {'field': 'lat', 'type': 'quantitative'}, 'longitude': {'field': 'lon', 'type': 'quantitative'}, 'text': {'field': 'name'}}}
tip = lambda *f: [{'field': a, 'type': t, 'title': ti} for a, t, ti in f]

spec('map1-venues', 'Where events are held', 'Each circle is one venue. Bigger circles host more events.',
     {'width': W, 'height': H, 'projection': PROJ, 'layer': [
         {'data': {'url': 'data/venues.json'}, 'mark': {'type': 'circle', 'opacity': .75, 'stroke': '#fff', 'strokeWidth': .5},
          'encoding': {'latitude': {'field': 'lat', 'type': 'quantitative'}, 'longitude': {'field': 'lon', 'type': 'quantitative'},
                       'size': {'field': 'n', 'type': 'quantitative', 'scale': {'range': [20, 1500]}, 'legend': {'title': 'Events'}},
                       'color': {'field': 'venueType', 'type': 'nominal', 'title': 'Venue type', 'scale': {'scheme': 'set2'}},
                       'tooltip': tip(('venue', 'nominal', 'Venue'), ('venueType', 'nominal', 'Type'), ('n', 'quantitative', 'Events'))}}, landLayer]})
spec('map2-density', 'Where events cluster', 'Events in each square of about 2 km by 2 km.',
     {'width': W, 'height': H, 'projection': PROJ, 'layer': [
         {'data': {'url': 'data/grid.json', 'format': {'property': 'features'}}, 'mark': {'type': 'geoshape', 'stroke': '#fff', 'strokeWidth': .5},
          'encoding': {'color': {'field': 'properties.n', 'type': 'quantitative', 'scale': {'scheme': 'tealblues', 'type': 'sqrt'}, 'legend': {'title': 'Events'}},
                       'tooltip': tip(('properties.n', 'quantitative', 'Events'), ('properties.types', 'quantitative', 'Kinds of event'))}}, landLayer]})
spec('map3-weekday-weekend', 'Do events move on the weekend?', 'Same venues, split by when the event starts.',
     {'data': {'url': 'data/venues_daytype.json'}, 'facet': {'column': {'field': 'dayType', 'type': 'nominal', 'title': None, 'header': {'labelFont': 'Bricolage Grotesque', 'labelFontSize': 13}}},
      'spec': {'width': W // 2 - 10, 'height': H - 100, 'projection': PROJ | {'scale': round(PROJ['scale'] * .6)}, 'mark': {'type': 'circle', 'opacity': .7, 'stroke': '#fff', 'strokeWidth': .4},
               'encoding': {'latitude': {'field': 'lat', 'type': 'quantitative'}, 'longitude': {'field': 'lon', 'type': 'quantitative'},
                            'size': {'field': 'k', 'type': 'quantitative', 'scale': {'range': [10, 600]}, 'legend': {'title': 'Events'}},
                            'color': {'field': 'dayType', 'type': 'nominal', 'scale': {'range': ['#138a8a', '#c2306b']}, 'legend': None},
                            'tooltip': tip(('venue', 'nominal', 'Venue'), ('k', 'quantitative', 'Events'))}}})
dd = d.groupby('date').size()
spec('chart4-calendar', 'The next three weeks at a glance', 'Number of events starting each day.',
     {'data': {'url': 'data/daily.json'}, 'width': W, 'height': 220, 'layer': [
         {'mark': {'type': 'rect', 'stroke': '#fff', 'strokeWidth': 2}, 'encoding': {'x': {'field': 'weekLabel', 'type': 'ordinal', 'title': 'Week starting Monday', 'axis': {'labelAngle': 0}},
              'y': {'field': 'dow', 'type': 'ordinal', 'sort': DAYS, 'title': None}, 'color': {'field': 'n', 'type': 'quantitative', 'scale': {'scheme': 'goldred'}, 'legend': {'title': 'Events'}},
              'tooltip': tip(('date', 'nominal', 'Date'), ('n', 'quantitative', 'Events'))}},
         {'mark': {'type': 'text', 'fontSize': 11}, 'encoding': {'x': {'field': 'weekLabel', 'type': 'ordinal'}, 'y': {'field': 'dow', 'type': 'ordinal', 'sort': DAYS}, 'text': {'field': 'n'}, 'color': {'value': '#1d2540'}}}]})
dh = d.groupby(['dow', 'hour']).size(); pk = dh.idxmax()
spec('chart5-time-of-day', 'When do events start?', f'Peak: {pk[0]} at {pk[1]}:00 with {dh.max()} events.',
     {'data': {'url': 'data/dow_hour.json'}, 'width': W, 'height': 220, 'layer': [
         {'mark': 'rect', 'encoding': {'x': {'field': 'hour', 'type': 'ordinal', 'title': 'Start hour (24-hour clock)', 'axis': {'labelAngle': 0}}, 'y': {'field': 'dow', 'type': 'ordinal', 'sort': DAYS, 'title': None},
              'color': {'field': 'n', 'type': 'quantitative', 'scale': {'scheme': 'purples'}, 'legend': {'title': 'Events'}}, 'tooltip': tip(('dow', 'nominal', 'Day'), ('hour', 'ordinal', 'Hour'), ('n', 'quantitative', 'Events'))}},
         {'data': {'values': [{'hour': int(pk[1]), 'dow': pk[0], 't': 'Busiest slot'}]}, 'mark': label('', {'dx': -8, 'align': 'right', 'dy': 0, 'fontWeight': 'bold'}),
          'encoding': {'x': {'field': 'hour', 'type': 'ordinal'}, 'y': {'field': 'dow', 'type': 'ordinal', 'sort': DAYS}, 'text': {'field': 't'}}}]})
spec('chart6-cost-waffle', 'What does it cost?', 'Each square is 1 in every 100 events.',
     {'data': {'url': 'data/waffle.json'}, 'width': 260, 'height': 260, 'mark': {'type': 'rect', 'stroke': '#fff', 'strokeWidth': 3},
      'encoding': {'x': {'field': 'col', 'type': 'ordinal', 'axis': None}, 'y': {'field': 'row', 'type': 'ordinal', 'axis': None},
                   'color': {'field': 'group', 'type': 'nominal', 'sort': order, 'scale': {'domain': order, 'range': ['#138a8a', '#f2a900', '#c9ced9']}, 'legend': {'title': None, 'orient': 'right'}}, 'tooltip': [{'field': 'group', 'title': 'Cost'}]}})
spec('chart7-stream', 'How the mix of events changes day to day', 'Stream thickness shows events per day. Click a legend item to highlight it.',
     {'data': {'url': 'data/daily_category.json'}, 'width': W, 'height': 260, 'params': [{'name': 'hl', 'select': {'type': 'point', 'fields': ['category']}, 'bind': 'legend'}],
      'mark': {'type': 'area', 'interpolate': 'monotone'}, 'encoding': {'x': {'field': 'date', 'type': 'temporal', 'title': None, 'axis': {'format': '%d %b'}}, 'y': {'field': 'n', 'type': 'quantitative', 'stack': 'center', 'axis': None},
      'color': {'field': 'category', 'type': 'nominal', 'scale': SC, 'legend': {'title': None}}, 'opacity': {'condition': {'param': 'hl', 'value': 1}, 'value': .35}, 'tooltip': tip(('category', 'nominal', 'Kind'), ('n', 'quantitative', 'Events'))}})
spec('chart8-categories', 'What kinds of events?', 'Each event is counted once under its main kind.',
     {'data': {'url': 'data/categories.json'}, 'width': W, 'height': 240, 'mark': 'bar', 'encoding': {'y': {'field': 'category', 'type': 'nominal', 'sort': '-x', 'title': None}, 'x': {'field': 'n', 'type': 'quantitative', 'title': 'Events'}, 'color': {'field': 'category', 'scale': SC, 'legend': None}, 'tooltip': tip(('n', 'quantitative', 'Events'))}})
spec('chart9-age', 'Who are events for?', 'Events can welcome more than one age group, so bars overlap. Events with no age listed are left out.',
     {'data': {'url': 'data/age.json'}, 'width': W, 'height': 220, 'mark': {'type': 'bar', 'color': '#4d8be8'}, 'encoding': {'y': {'field': 'ageGroup', 'type': 'nominal', 'sort': '-x', 'title': None}, 'x': {'field': 'n', 'type': 'quantitative', 'title': 'Events'}, 'tooltip': tip(('n', 'quantitative', 'Events'))}})
spec('chart10-venue-matrix', 'Which venues host which kinds of events?', 'Number of events for each venue type and kind of event.',
     {'data': {'url': 'data/venue_category.json'}, 'width': W, 'height': 240, 'layer': [
         {'mark': {'type': 'rect', 'stroke': '#fff'}, 'encoding': {'x': {'field': 'category', 'type': 'nominal', 'sort': CATS, 'title': None, 'axis': {'labelAngle': -30}}, 'y': {'field': 'venueGroup', 'type': 'nominal', 'title': None},
              'color': {'field': 'n', 'type': 'quantitative', 'scale': {'scheme': 'teals', 'type': 'sqrt'}, 'legend': {'title': 'Events'}}, 'tooltip': tip(('venueGroup', 'nominal', 'Venue'), ('category', 'nominal', 'Kind'), ('n', 'quantitative', 'Events'))}},
         {'mark': {'type': 'text', 'fontSize': 10}, 'encoding': {'x': {'field': 'category', 'type': 'nominal', 'sort': CATS}, 'y': {'field': 'venueGroup', 'type': 'nominal'}, 'text': {'field': 'n'}, 'color': {'value': '#1d2540'}}}]})
spec('chart11-booking', 'Do you need to book?', 'Share of events in each kind that ask for a booking.',
     {'data': {'url': 'data/booking.json'}, 'width': W, 'height': 240, 'mark': 'bar', 'encoding': {'y': {'field': 'category', 'type': 'nominal', 'sort': CATS, 'title': None}, 'x': {'field': 'n', 'type': 'quantitative', 'stack': 'normalize', 'title': 'Share of events', 'axis': {'format': '%'}},
      'color': {'field': 'booking', 'type': 'nominal', 'sort': ['Booking required', 'No booking', 'Not stated'], 'scale': {'domain': ['Booking required', 'No booking', 'Not stated'], 'range': ['#c2306b', '#138a8a', '#c9ced9']}, 'legend': {'title': None}}, 'tooltip': tip(('booking', 'nominal', 'Booking'), ('n', 'quantitative', 'Events'))}})

# ---- facts for the story
N = len(d); pct = lambda x: round(100 * x / N)
topCat = d.category.value_counts().index[0]; busy = dd.idxmax()
facts = dict(N=N, free=pct((d.costGroup == 'Free').sum()), topCat=topCat, topCatPct=pct((d.category == topCat).sum()), park=pct((d.venueGroup == 'Park').sum()), lib=pct((d.venueGroup == 'Library').sum()),
             wkend=pct(d.weekend.sum()), busy=pd.to_datetime(busy).strftime('%A %d %B'), busyN=int(dd.max()), first=d.start.min().strftime('%d %B'), last=d.start.max().strftime('%d %B %Y'), festN=int(d.event_type.fillna('').str.contains('Festivals').sum()))
json.dump(facts, open('facts.json', 'w'), indent=1)
print(f"{'rows in file':<28}{totalRows:>6}\n{'kept (not long-running)':<28}{N:>6}\n{'with coordinates':<28}{len(g):>6}")
for k2, v in facts.items(): print(f'{k2:<28}{v!s:>20}')
