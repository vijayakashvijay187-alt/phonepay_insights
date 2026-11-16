# Knowledge transfer: PhonePe Transaction Insights

## What the project was

The brief asks for a PhonePe analysis: pull the public Pulse JSON, load aggregated, map, and top data into SQL, answer business case studies, and show the results in Streamlit. The case studies cover transaction mix, device engagement, insurance, state expansion, and top states, districts, and pin codes.

## What the live data actually contains

The Pulse repository cloned for this project (2026 snapshot) does not match the older course slides.

- Insurance folders are gone. The same slots are merchant registration counts.
- Aggregated user files contain `registeredCount` only. There is no `usersByDevice` list and no app-open count.
- Top files contain states and districts. There is no pin-code array.
- Aggregated transaction files contain category counts. Amounts are on the map transaction files.

The loader still understands the older shapes. A `usersByDevice` list becomes `row_kind = device` rows. A `pincodes` array becomes `entity_level = pincode`. If those keys are absent, those rows are simply not created.

Place names are folded to one form, so `karnataka` and `karnataka` from a path slug `karnataka` match `karnataka` from JSON. Hyphens and `&` become spaces and `and`.

## How it is built

`src/phonepe/extract.py` walks `data/pulse` and returns tuples for nine tables. `scripts/setup.py` waits until each container accepts connections, applies `sql/<table>.sql`, truncates, and `COPY`s the rows. Re-running setup replaces the data, so it is safe to sync again.

Each table has its own Postgres 16 container. They do not share a server, so a SQL statement cannot join users to merchants. `merchant_penetration` reads the two databases and joins in Python. Every other case study is a single-table query.

| Container | Port | What it holds |
| --- | --- | --- |
| aggregated_transaction | 5601 | State, year, quarter, payment category, count, amount |
| aggregated_user | 5602 | Registered users, plus device rows when the JSON has them |
| aggregated_merchant | 5603 | Registered merchants (the live stand-in for insurance) |
| map_transaction | 5604 | State and district transaction count and amount |
| map_user | 5605 | State and district registered users |
| map_merchant | 5606 | State and district registered merchants |
| top_transaction | 5607 | Top states, districts, and pin codes when present |
| top_user | 5608 | Top users by geography |
| top_merchant | 5609 | Top merchants by geography |

Country files are stored with `state = india` or `scope_state = india`. State files use the state name from the path.

## Snapshot from the loaded warehouse

For 2025 Q1, national category counts were about 79.6 billion retail, 41.2 billion peer-to-peer, and 7.8 billion utility. Maharashtra, Karnataka, and Telangana led mapped transaction counts. Uttar Pradesh led registered users (about 77 million) and merchants (about 6.9 million, 0.09 merchants per registered user). The busiest district was Bengaluru Urban. The full wording is in `reports/findings.md`.

Quarter-on-quarter growth compares each state with its previous row in year-quarter order. The first quarter of a series has no growth value.

## What to show

1. Open the dashboard and filter to 2025 Q1.
2. Transaction dynamics: category bars for one state, then the state ranking.
3. User engagement: explain that device brands are absent in this dump, so the chart is registered users.
4. Merchant penetration: this is the insurance case, answered with merchant counts because that is what Pulse publishes now.
5. Top regions and the district chart for Karnataka. The India view is a scatter on approximate state centroids, not a survey boundary file.

## Tests

`tests/test_extract.py` builds a tiny Pulse tree, including a legacy device list and a pin code, and checks the parsed tuples. It also checks quarter-on-quarter math. It does not need Docker.

## Moving the project

Copy the folder, install `requirements.txt`, and run `bash scripts/setup.sh`. Docker must be running. The script clones Pulse if `data/pulse` is empty. Override ports with the variables in `.env.example` if 5601–5609 are taken.
