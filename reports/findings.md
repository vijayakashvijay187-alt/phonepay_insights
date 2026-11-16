# PhonePe findings

Period used for the snapshot: 2025 Q1. The latest full calendar year at or before 2025 is preferred so a partial current year does not dominate the ranking.

## 1. Transaction dynamics

National payment-category counts for 2025:

- retail: 79,615,629,899
- p2p: 41,152,641,116
- utility: 7,775,768,952

States with the most mapped transactions in Q1:

- maharashtra: 3,904,534,550
- karnataka: 3,729,923,285
- telangana: 2,957,671,238
- uttar pradesh: 2,618,333,992
- andhra pradesh: 2,422,886,250

Fastest quarter-on-quarter transaction growth in that quarter:

- manipur: 34.1% versus the previous quarter
- lakshadweep: 25.2% versus the previous quarter
- mizoram: 19.7% versus the previous quarter
- tripura: 16.1% versus the previous quarter
- assam: 14.5% versus the previous quarter

## 2. User engagement

Device-brand files are not in the current Pulse dump, so engagement is measured from registered users. Largest states in 2025 Q1:

- uttar pradesh: 77,043,398
- maharashtra: 74,177,131
- karnataka: 46,870,457
- rajasthan: 38,208,545
- west bengal: 37,781,664

Top states from the top-user extract:

- uttar pradesh: 77,043,398
- maharashtra: 74,177,131
- karnataka: 46,870,457
- rajasthan: 38,208,545
- west bengal: 37,781,664

## 3. Merchant penetration

The course brief asks for insurance. The live Pulse repository publishes merchant registration instead. Highest merchant counts, with merchants per registered user:

- uttar pradesh: 6,931,337 merchants, 0.0900 per registered user
- maharashtra: 5,550,838 merchants, 0.0748 per registered user
- west bengal: 3,221,457 merchants, 0.0853 per registered user
- karnataka: 2,990,287 merchants, 0.0638 per registered user
- rajasthan: 2,927,213 merchants, 0.0766 per registered user

## 4. Market expansion

Use the state leader list above as the expansion baseline. Amounts are present on the map transaction table even when the aggregated transaction files only carry counts. Compare `transaction_amount` and `transaction_count` in the dashboard before treating a state as high value rather than high volume.

## 5. Top districts

Highest transaction districts in India for 2025 Q1:

- bengaluru urban district: 1,862,104,522
- pune district: 973,919,811
- rangareddy district: 665,666,525
- medchal malkajgiri district: 615,484,296
- jaipur district: 522,673,707

Pin codes are not in this Pulse snapshot. If an older dump with a `pincodes` array is placed in `data/pulse`, the loader stores those rows with `entity_level = pincode`.
