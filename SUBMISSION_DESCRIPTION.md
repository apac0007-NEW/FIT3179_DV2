# FIT3179 Data Visualisation 2 — Submission description

## Domain, audience and purpose (Why / Who)

**Domain:** community festivals, cultural events and neighbourhood celebrations in Australia.

**Audience:** the general Australian public, including people interested in local councils, community participation and volunteering.

**Purpose:** to show who attends festivals and cultural events, how broader cultural participation differs across states and demographic groups, where Australians want more opportunities, and how cultural volunteering and neighbourhood connection relate to community life. The story avoids claiming that festival attendance itself causes social connection.

## What: data and relevance

The visualisation combines five published datasets/reports:

1. **Australian Bureau of Statistics (ABS), Cultural and creative activities, 2021–22.** Provides state/territory participation rates and breakdowns by age, sex and children’s cultural activities, with a 2017–18 comparison for selected measures.
2. **Creative Australia, Soundcheck: Insights into Australia’s music festival sector (2022–23).** Maps 535 music festivals across Australia, with state/territory counts, genre shares and organiser challenges. This is a national music-festival inventory, not a count of all neighbourhood or council celebrations.
3. **Creative Australia, Creative Transformations: Results of the National Arts Participation Survey 2025.** A nationally representative survey of 9,065 Australians aged 15 and over. Provides the latest live arts/festival attendance, cost barriers, cultural identity participation and First Nations arts/festival measures.
4. **Creative Australia, Creating Value: Results of the National Arts Participation Survey 2022.** Used only for selected age/gender and regional-demand breakdowns where equivalent subgroup details were not available in the 2025 summary.
5. **Australian Institute of Health and Welfare (AIHW), Social cohesion and social connection.** Provides 2024 indicators on neighbourhood belonging, perceived neighbour support and social isolation.

These sources are relevant because they combine direct national festival-attendance measures with broader cultural participation and social connection context. Those measures are labelled separately where their definitions and years differ.

**Data limitation:** the supplied project version contained a Brisbane City Council export of up to 2,000 future event listings, not a national inventory. It was not used as evidence of national festival coverage. A nationally consistent council-level festival inventory was not present in the supplied materials, so the final story focuses on national survey evidence rather than fabricating or extrapolating event counts.

## How: idioms and design rationale

The page follows a four-part narrative: (1) the national music-festival footprint and genre diversity, (2) demographic cultural participation, (3) festival attendance and unmet demand, and (4) volunteering, organiser pressures and neighbourhood connection.

- **Choropleth map:** compares the number of mapped music festivals by state/territory.
- **Proportional-symbol map:** compares mapped music festivals per 10,000 residents, reducing the bias of raw totals toward larger jurisdictions.
- **Tile-grid cartogram:** lets readers compare state/territory festival counts without large states dominating visual space.
- **Dumbbell chart:** directly compares two survey waves by state/territory.
- **Mirrored comparison and heatmap:** make demographic differences visible across the same age bands.
- **Slopegraph:** highlights how children’s participation changed between waves.
- **Point chart:** compares festival attendance and demand across selected groups.
- **Lollipop chart:** shows the scale of cultural volunteering measures.
- **Matrix chart and annotated bars:** compare unmet demand and connect cultural indicators with broader neighbourhood measures.

Tooltips offer optional details. The narrative text and annotations explain the central insight so readers do not need specialist statistical knowledge. A restrained green, warm ochre and rust palette, consistent type hierarchy, aligned chart cards and responsive CSS support readability on laptop and mobile screens.

## Sources

- ABS: https://www.abs.gov.au/statistics/people/people-and-communities/cultural-and-creative-activities/latest-release
- Creative Australia 2025: https://creative.gov.au/research/creative-transformations-results-national-arts-participation-survey
- Creative Australia Soundcheck: https://www.creative.gov.au/research/soundcheck-australian-music-festivals
- Creative Australia 2022 subgroup detail: https://creative.gov.au/sites/creative-australia/files/documents/2025-04/National-Arts-Participation-Survey-results-2022-1.pdf
- AIHW: https://www.aihw.gov.au/reports/australias-welfare/social-cohesion-and-social-connection
- ABS ASGS boundary reference: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/latest-release

## Authorship and AI acknowledgement

Author: Aditya Pachegaonkar. FIT3179 Data Visualisation 2, Monash University. Prepared 29 October 2026.

AI tools were used to assist with code structure, chart specifications and editorial drafting. The student should review every figure and specification, verify the boundary-file edition/licence, test the public deployment and be able to explain the design decisions in the interview.
