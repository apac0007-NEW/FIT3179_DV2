"""Writes national data and specs. Numbers are typed from Volunteering Australia, 'Volunteering Statistics: General Social Survey 2025' (May 2026),
which reproduces ABS General Social Survey 2025 tables 6.3, 7.3, 10.3, 11.3 and 13.3."""
import json
W, H = 640, 520
INK = '#1d2540'
def dump(name, obj): json.dump(obj, open(f'data/{name}.json', 'w'), indent=1)
CFG = {'view': {'stroke': None}, 'font': 'Source Serif 4', 'axis': {'labelFont': 'Source Serif 4', 'titleFont': 'Source Serif 4', 'domain': False, 'tickSize': 0, 'labelFontSize': 12, 'titleFontSize': 12},
       'legend': {'labelFont': 'Source Serif 4', 'titleFont': 'Source Serif 4'}, 'title': {'font': 'Bricolage Grotesque', 'fontSize': 16, 'anchor': 'start', 'subtitleFont': 'Source Serif 4', 'subtitleColor': '#5b6479'}}
def spec(name, title, sub, body):
    s = {'$schema': 'https://vega.github.io/schema/vega-lite/v5.json', 'title': {'text': title, 'subtitle': sub}, 'config': CFG}; s.update(body)
    json.dump(s, open(f'specs/{name}.json', 'w'), indent=2)
Q = lambda f, **k: {'field': f, 'type': 'quantitative', **k}
N = lambda f, **k: {'field': f, 'type': 'nominal', **k}
M, F = '#4d8be8', '#c2306b'
# ---- state table (Table 6.3): name, abbreviation, formal 2025, formal 2020, label lat, label lon
rows = [('New South Wales', 'NSW', 22.3, 23.1, -32.6, 146.6), ('Victoria', 'Vic', 21.8, 24.4, -36.9, 144.6), ('Queensland', 'Qld', 22.0, 25.4, -22.6, 144.4),
        ('South Australia', 'SA', 23.6, 26.2, -30.0, 135.6), ('Western Australia', 'WA', 23.9, 25.6, -25.5, 122.2), ('Tasmania', 'Tas', 27.5, 30.2, -42.1, 146.6),
        ('Northern Territory', 'NT', 26.7, 28.4, -19.4, 133.4), ('Australian Capital Territory', 'ACT', 22.0, 30.9, -35.6, 151.0)]
states = [{'state': a, 'abbr': b, 'rate2025': c, 'rate2020': d, 'fall': round(d - c, 1), 'lat': e, 'lon': f, 'label': f'{b} {c}%', 'labelFall': f'{b} -{round(d - c, 1)}'} for a, b, c, d, e, f in rows]
dump('national_states', states)
PROJ = {'type': 'albers', 'rotate': [-134, 0], 'center': [0, -27], 'parallels': [-18, -36], 'scale': 800}
def stateMap(name, title, sub, field, scheme, domain, legend, labelField):
    spec(name, title, sub, {'width': W, 'height': H, 'projection': PROJ, 'layer': [
        {'data': {'url': 'data/states.geojson', 'format': {'property': 'features'}}, 'transform': [{'lookup': 'properties.STATE_NAME', 'from': {'data': {'url': 'data/national_states.json'}, 'key': 'state', 'fields': [field, 'abbr']}}],
         'mark': {'type': 'geoshape', 'stroke': '#fff', 'strokeWidth': 1}, 'encoding': {'color': Q(field, scale={'scheme': scheme, 'domain': domain}, legend={'title': legend, 'orient': 'bottom'}),
         'tooltip': [{'field': 'properties.STATE_NAME', 'type': 'nominal', 'title': 'State'}, Q(field, title=legend)]}},
        {'data': {'url': 'data/national_states.json'}, 'mark': {'type': 'text', 'fontSize': 11, 'fontWeight': 'bold', 'color': INK, 'stroke': '#fff', 'strokeWidth': 3, 'paintOrder': 'stroke'},
         'encoding': {'latitude': Q('lat'), 'longitude': Q('lon'), 'text': N(labelField)}}]})
stateMap('map4-states', 'Where Australians volunteer most', 'Share of people aged 15+ who volunteered through an organisation, 2025.', 'rate2025', 'teals', [20, 28], 'Volunteers (%)', 'label')
stateMap('map5-states-change', 'Where volunteering fell most since 2020', 'Fall in the share volunteering, in percentage points.', 'fall', 'oranges', [0, 9], 'Fall (percentage points)', 'labelFall')
spec('chart12-state-dumbbell', 'Every state and territory fell, the ACT most', 'Share volunteering through an organisation, 2020 and 2025.',
     {'data': {'url': 'data/national_states.json'}, 'width': W, 'height': 300, 'encoding': {'y': N('state', sort='-x', title=None)}, 'layer': [
         {'mark': {'type': 'rule', 'color': '#c9ced9', 'strokeWidth': 3}, 'encoding': {'x': Q('rate2020', title='Volunteers (%)', scale={'domain': [20, 32]}), 'x2': Q('rate2025')}},
         {'mark': {'type': 'circle', 'size': 130, 'color': '#9aa3b5'}, 'encoding': {'x': Q('rate2020'), 'tooltip': [N('state'), Q('rate2020', title='2020')]}},
         {'mark': {'type': 'circle', 'size': 130, 'color': '#138a8a'}, 'encoding': {'x': Q('rate2025'), 'tooltip': [N('state'), Q('rate2025', title='2025')]}},
         {'data': {'values': [{'state': 'Australian Capital Territory', 'x': 30.9, 't': 'Biggest fall: 30.9% to 22.0%'}]}, 'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'fontSize': 11, 'color': INK}, 'encoding': {'x': Q('x'), 'text': N('t')}}]})
dump('national_remote', [{'area': a, 'type': t, 'rate': r} for a, f, i in [('Major cities', 20.9, 29.2), ('Inner regional', 26.7, 30.1), ('Outer regional', 28.0, 30.2), ('Remote', 34.0, 34.2)] for t, r in [('Formal', f), ('Informal', i)]])
spec('chart13-remoteness', 'The further from a big city, the more people volunteer', 'Formal = through an organisation (12 months). Informal = helping neighbours and friends (4 weeks).',
     {'data': {'url': 'data/national_remote.json'}, 'width': W, 'height': 200, 'layer': [
         {'mark': {'type': 'circle', 'size': 160}, 'encoding': {'y': N('area', sort=['Major cities', 'Inner regional', 'Outer regional', 'Remote'], title=None), 'x': Q('rate', title='People volunteering (%)', scale={'domain': [18, 36]}),
          'color': N('type', scale={'domain': ['Formal', 'Informal'], 'range': ['#138a8a', '#f2a900']}, legend={'title': None}), 'tooltip': [N('area'), N('type'), Q('rate')]}}]})
dump('national_trend', [{'year': y, 'type': 'Formal', 'rate': r} for y, r in [(2010, 36.2), (2014, 30.9), (2019, 28.8), (2020, 25.0), (2025, 22.6)]] + [{'year': y, 'type': 'Informal', 'rate': r} for y, r in [(2019, 33.4), (2020, 32.1), (2025, 29.5)]])
spec('chart14-trend', 'Volunteering through organisations has slipped for 15 years', 'Share of people aged 15+. Informal volunteering was first measured in 2019.',
     {'data': {'url': 'data/national_trend.json'}, 'width': W, 'height': 280, 'layer': [
         {'mark': {'type': 'line', 'point': True, 'strokeWidth': 3}, 'encoding': {'x': Q('year', title=None, axis={'format': 'd', 'values': [2010, 2014, 2019, 2020, 2025]}, scale={'domain': [2009, 2026]}), 'y': Q('rate', title='People volunteering (%)', scale={'domain': [15, 40]}),
          'color': N('type', scale={'domain': ['Formal', 'Informal'], 'range': ['#138a8a', '#f2a900']}, legend={'title': None}), 'tooltip': [N('type'), Q('year', format='d'), Q('rate')]}},
         {'mark': {'type': 'text', 'dy': -10, 'fontSize': 11, 'color': INK}, 'encoding': {'x': Q('year'), 'y': Q('rate'), 'text': Q('rate', format='.1f'), 'color': {'value': INK}}},
         {'data': {'values': [{'year': 2010, 'rate': 36.2, 't': 'Peak in 2010'}]}, 'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'dy': 10, 'fontSize': 11, 'fontStyle': 'italic', 'color': INK}, 'encoding': {'x': Q('year'), 'y': Q('rate'), 'text': N('t')}}]})
age = [('15 to 24', 15.7, 14.1), ('25 to 34', 13.2, 13.1), ('35 to 44', 24.9, 30.5), ('45 to 54', 30.6, 26.8), ('55 to 64', 23.4, 27.5), ('65 and over', 25.6, 26.5)]
dump('national_age', [{'age': a, 'gender': g, 'rate': r, 'signed': -r if g == 'Males' else r} for a, m, f in age for g, r in [('Males', m), ('Females', f)]])
spec('chart15-age-gender', 'Volunteering peaks in middle age', 'Share volunteering through an organisation, 2025. Men to the left, women to the right.',
     {'data': {'url': 'data/national_age.json'}, 'width': W, 'height': 280, 'mark': 'bar', 'encoding': {'y': N('age', sort=[a[0] for a in age], title=None), 'x': Q('signed', title='People volunteering (%)', axis={'labelExpr': "abs(datum.value) + '%'"}, scale={'domain': [-35, 35]}),
      'color': N('gender', scale={'domain': ['Males', 'Females'], 'range': [M, F]}, legend={'title': None}), 'tooltip': [N('gender'), N('age'), Q('rate', title='Volunteers (%)')]}})
orgs = [('Sport and physical recreation', 40.0, 27.9), ('Religious or spiritual', 22.7, 23.8), ('Community or cultural groups', 15.2, 20.1), ('Education and training', 11.7, 15.4), ('Parenting, children and youth', 8.1, 11.7),
        ('Arts or heritage', 6.3, 5.0), ('Welfare or homelessness', 5.5, 7.5), ('Environment or animal welfare', 5.4, 5.8), ('Emergency services', 7.2, 4.1), ('Health or mental health', 2.5, 6.3)]
dump('national_orgs', [{'org': o, 'males': m, 'females': f} for o, m, f in orgs])
spec('chart16-org-dumbbell', 'What people volunteer for', 'Share of volunteers helping each type of organisation, 2025. People can help more than one.',
     {'data': {'url': 'data/national_orgs.json'}, 'width': W, 'height': 340, 'encoding': {'y': N('org', sort=[o[0] for o in orgs], title=None)}, 'layer': [
         {'mark': {'type': 'rule', 'color': '#c9ced9', 'strokeWidth': 3}, 'encoding': {'x': Q('males', title='Volunteers (%)'), 'x2': Q('females')}},
         {'mark': {'type': 'circle', 'size': 120, 'color': M}, 'encoding': {'x': Q('males'), 'tooltip': [N('org'), Q('males', title='Men (%)')]}},
         {'mark': {'type': 'circle', 'size': 120, 'color': F}, 'encoding': {'x': Q('females'), 'tooltip': [N('org'), Q('females', title='Women (%)')]}}]})
why = {'Not interested or no need': [45.1, 35.8, 27.2, 28.0, 35.1, 39.2], 'Not sure how, or never asked': [22.1, 19.8, 15.2, 12.3, 14.7, 11.1], 'No suitable opportunities': [11.1, 11.3, 11.9, 7.1, 9.5, 7.8],
       'Money': [7.8, 11.7, 14.7, 7.0, 4.6, 2.4], 'Health': [3.9, 4.3, 7.0, 11.0, 15.6, 27.8], 'No time': [45.0, 57.7, 57.7, 56.6, 43.8, 24.0]}
ages = ['15-24', '25-34', '35-44', '45-54', '55-64', '65+']
dump('national_why', [{'reason': k, 'age': a, 'pct': v} for k, vs in why.items() for a, v in zip(ages, vs)])
spec('chart17-why-not', 'Why people do not volunteer', 'Share of non-volunteers giving each reason, by age. People could give more than one reason.',
     {'data': {'url': 'data/national_why.json'}, 'width': W, 'height': 260, 'layer': [
         {'mark': {'type': 'rect', 'stroke': '#fff', 'strokeWidth': 2}, 'encoding': {'x': N('age', sort=ages, title='Age group', axis={'labelAngle': 0}), 'y': N('reason', sort=list(why), title=None),
          'color': Q('pct', scale={'scheme': 'purples'}, legend={'title': 'Non-volunteers (%)'}), 'tooltip': [N('reason'), N('age'), Q('pct', title='%')]}},
         {'mark': {'type': 'text', 'fontSize': 11}, 'encoding': {'x': N('age', sort=ages), 'y': N('reason', sort=list(why)), 'text': Q('pct', format='.0f'), 'color': {'condition': {'test': 'datum.pct > 35', 'value': '#fff'}, 'value': INK}}}]})
