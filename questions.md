# Topic

Affordable housing development in California, as recorded in public data from
the California Tax Credit Allocation Committee (CTCAC), which awards federal and
state Low-Income Housing Tax Credits (LIHTC). Official, publicly accessible
government sources come first.

**Workshop scope (phase 1):** one program year of CTCAC awards. Pick a recent,
complete year such as 2025: its annual report, plus the project staff reports
for a handful of awarded projects. Later phases add more years, the full
project list and other agencies (see "Expanding" below).

# Questions

1. **Where are affordable housing projects being developed across California,
   and how has development activity changed over time?**
   - Phase 1 claims: projects and low-income units awarded, by region or county,
     for the chosen year, as the annual report states them.
   - Change over time needs the same figures from two or more annual reports,
     one claim per year.

2. **Who are the most active affordable housing developers, and how many
   projects and units are associated with each developer?**
   - Phase 1 claims: developer name and unit count for each project, quoted
     from its staff report.
   - A ranking is a count over many rows, not a number quoted in one sentence,
     so verify.py can't check it directly (see "Reliability").

3. **How much public funding or tax credit financing is being awarded to these
   projects, and how does it vary by location, developer, and project size?**
   - Phase 1 claims: total federal and state credits awarded in the year
     (annual report), and per project: annual federal credits, state credits,
     total development cost and units (staff reports).
   - Comparisons across places, developers or sizes, such as credits per unit,
     are calculated from verified claims, not quoted.

4. **What types of affordable housing projects are being developed (new
   construction versus rehabilitation, number of units, and geographic
   distribution)?**
   - Phase 1 claims: new construction and rehabilitation counts or units for
     the year, plus each sampled project's construction type, housing type
     (large family, senior, special needs, at-risk) and unit count.

5. **Which projects have recently received funding awards, and what can
   available public records tell us about their development status?**
   - Phase 1 claims: award amount, date and unit count for recently awarded
     projects, from staff reports and committee meeting materials.
   - Status: CTCAC records show the award and its deadlines, not whether a
     building has been built. See "Reliability".

# Sources (official, public)

| Source | Where | Format | Fits this system? |
|---|---|---|---|
| CTCAC annual reports (1994-2026) | treasurer.ca.gov/ctcac/annual-reports | PDF per year | Yes. Totals written in sentences and tables. |
| Project staff reports | treasurer.ca.gov/ctcac/meeting/staff | PDF per project | Yes. Developer, units, credits, costs, construction type. |
| Committee meeting agendas and award lists | treasurer.ca.gov/ctcac/meeting | PDF | Yes. Which projects were recommended or awarded at each meeting. |
| CTCAC project list (all awarded projects) | treasurer.ca.gov/ctcac/projects, file "List of Projects_1.xlsx" | Excel | Not yet. verify.py reads only PDF, HTML and text. |
| Project mapping | treasurer.ca.gov/ctcac/projects | Interactive map | Reference only. Not something a claim can quote. |

# Reliability: what each question can rest on

| Question | Phase 1 (annual report + staff reports) | Needs more |
|---|---|---|
| 1. Where, and over time | **Good** for statewide and regional totals the report states; trend with 2+ years of reports | County or city detail for every project needs the Excel project list |
| 2. Top developers | **Partial.** Developer and units for sampled projects only | A full ranking needs the Excel list plus a counting script. Developer names vary in spelling and joint ventures, so they need cleanup. |
| 3. Funding amounts | **Good** for totals and per-project credits | Credits are only part of the financing. Local, state (HCD) and bond money appear in staff reports but not in one place. |
| 4. Project types | **Good** if the annual report breaks out construction type, and per project from staff reports | Statewide shares by type need the full list |
| 5. Recent awards and status | **Good** for awards. **Weak** for status. | Placed-in-service records, CTCAC compliance data, local building permits or developer announcements. Not in phase 1. |

Things to watch for when checking claims:
- The 9% and 4% credit programs are separate competitions with separate totals.
  Each claim's subject should say which one it covers.
- Federal credits are annual amounts (claimed each year for 10 years). State
  credits are a total over the life of the credit. Don't add them together.
- Annual reports often give several years in one sentence or table. Check that
  the period in each claim is the right one.

# Expanding over time

1. **More years:** add one annual report per year to build the trend for questions 1, 3 and 4.
2. **Full project list:** teach verify.py to read Excel files (for example,
   saving each row as a line of text) so that table rows can be quoted.
   Rankings by developer and county then come from verified rows.
3. **Other sources:** California HCD funding awards, the California Debt Limit
   Allocation Committee (CDLAC) bond awards for 4% projects, HUD's national
   LIHTC database and local housing element progress reports, for status and
   completion.
4. **Keep current:** a weekly routine that checks the CTCAC staff reports page
   for new awards and adds them on a separate branch for review.
