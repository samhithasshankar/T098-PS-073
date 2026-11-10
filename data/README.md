# PS-073 – Electricity Billing Engine with Slab Tariffs, Time-of-Day, Net-Metering and Arrears — Sample Data Pack

Prepared by 10 SECONDS for Team T098.

## Files

| File | What it holds | Row count |
|---|---|---|
| `consumers.csv` | 100 consumers (DOMESTIC 60 / COMMERCIAL 20 / INDUSTRIAL_LT 12 / AGRICULTURE 8) incl. 10 NET and 15 TOD meters | 100 data rows |
| `tariff_orders.csv` | 2 tariff orders (TO-2025 in force at start, TO-2026 mid-period) with fixed, FAC, duty, TOD and minimum parameters | 2 data rows |
| `tariff_slabs.csv` | Energy slabs per category per tariff order | 18 data rows |
| `readings.csv` | Opening reading (Aug 2025) + 14 monthly readings per consumer, with ESTIMATED / FAULTY / METER_CHANGE months | 1499 data rows |
| `payments.csv` | Consumer payments (counter and online) | 1208 data rows |
| `commands.txt` | Reconnection request, arrears-ageing, bill and ledger prints | 36 command lines (excluding comments) |

Volumes in this sample are reduced for email delivery; the hidden evaluation set is larger and uses the same schema.

Row numbers quoted below are 1-based data-row numbers (the header is row 0). Line numbers for `commands.txt` are physical line numbers including comment lines.

## Column reference

Conventions: dates `YYYY-MM-DD`; timestamps `YYYY-MM-DD HH:MM:SS` (24h, IST, no timezone suffix); money in Rs as plain decimals with 2 places (no commas, no symbol); percentages as plain numbers (12.5 means 12.5%); booleans `true`/`false`; IDs uppercase with a fixed prefix. An empty cell means "not applicable" and only occurs in columns whose notes say so.

### `consumers.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| consumer_id | string | CON-nnnn | — | primary key |
| consumer_name | string | — | — | — |
| category | enum | — | DOMESTIC, COMMERCIAL, INDUSTRIAL_LT, AGRICULTURE | — |
| sanctioned_load_kw | decimal | kW | — | fixed charge base |
| pump_hp | int | HP | — | AGRICULTURE only (empty otherwise); <= 10 HP fully subsidised |
| connection_date | date | — | — | — |
| meter_type | enum | — | NORMAL, TOD, NET | TOD only for COMMERCIAL / INDUSTRIAL_LT |
| solar_capacity_kw | decimal | kW | — | 0.00 unless NET; > sanctioned load -> INELIGIBLE_NET |
| bpl | bool | — | — | — |
| security_deposit | decimal | Rs | — | held at start |
| read_day | int | day of month | 3, 10, 17, 24 | usual reading day (actual dates are in readings.csv) |
| city | string | — | — | — |
| mobile | string | 10 digits | — | — |

### `tariff_orders.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| tariff_id | string | TO-YYYY | — | — |
| effective_date | date | — | — | in force from 00:00 of this date |
| fac_per_unit | decimal | Rs/unit | — | — |
| duty_pct_domestic | decimal | % | — | — |
| duty_pct_others | decimal | % | — | — |
| fixed_domestic_per_kw | decimal | Rs/kW/month | — | — |
| fixed_commercial_per_kw | decimal | Rs/kW/month | — | — |
| fixed_industrial_per_kw | decimal | Rs/kW/month | — | — |
| min_charge_domestic | decimal | Rs | — | — |
| min_charge_others | decimal | Rs | — | — |
| tod_peak_pct | decimal | % | — | 18:00-22:00 |
| tod_offpeak_pct | decimal | % | — | 22:00-06:00 (negative = discount) |
| net_settlement_rate | decimal | Rs/unit | — | March settlement of banked units |
| agri_subsidy_hp_limit | int | HP | — | — |

### `tariff_slabs.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| tariff_id | string | — | tariff_orders.csv | — |
| category | enum | — | DOMESTIC, COMMERCIAL, INDUSTRIAL_LT, AGRICULTURE | — |
| slab_no | int | — | — | — |
| from_unit | int | units | — | slab 1 starts at 0 (units 0-50 = first 50 units) |
| to_unit | int | units | — | inclusive upper bound; empty = no upper limit |
| rate_per_unit | decimal | Rs | — | — |

### `readings.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| reading_id | string | RD-nnnnn | — | file sorted by reading_ts |
| consumer_id | string | — | consumers.csv | — |
| reading_ts | timestamp | — | — | bill is generated at this instant; bill date = this date |
| status | enum | — | NORMAL, ESTIMATED, FAULTY, METER_CHANGE | first row per consumer (Aug 2025) is the opening reading, not billed |
| kwh_import | int | kWh, cumulative register | — | empty for ESTIMATED / FAULTY |
| kwh_export | int | kWh, cumulative register | — | NET meters only |
| tod_peak_kwh | int | kWh in this period | — | TOD meters only; zone split of the period's import since the last NORMAL reading |
| tod_offpeak_kwh | int | kWh in this period | — | TOD only |
| tod_normal_kwh | int | kWh in this period | — | TOD only |
| max_demand_kw | decimal | kW | — | recorded MD; empty for AGRICULTURE and for ESTIMATED/FAULTY |
| old_meter_final | int | kWh | — | METER_CHANGE only |
| new_meter_initial | int | kWh | — | METER_CHANGE only; kwh_import is the new meter's register |

### `payments.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| payment_id | string | PAY-nnnnn | — | file sorted by payment_ts |
| consumer_id | string | — | consumers.csv | — |
| payment_ts | timestamp | — | — | — |
| amount | decimal | Rs | — | — |
| mode | enum | — | ONLINE, COUNTER | ONLINE earns the extra 0.5% |

## Command file format

`commands.txt` holds one command per line in the form `COMMAND_NAME|arg1|arg2|...`. Commands must be processed strictly in file order. Lines starting with `#` are comments and blank lines are ignored. An empty argument (two pipes in a row) means "not supplied". Every command used in this pack:

| Command | Arguments (in order) | Meaning |
|---|---|---|
| `RECONNECT` | `consumer_id|timestamp` | Request reconnection (needs full arrears + Rs 250 + deposit top-up already paid) |
| `PRINT_ARREARS_AGEING` | `as_of_date` | Arrears ageing report (0-30, 31-60, 61-90, >90 days) |
| `PRINT_BILL` | `consumer_id|bill_month (YYYY-MM)` | Print the bill(s) dated in that month for the consumer |
| `PRINT_LEDGER` | `consumer_id|as_of_date` | Consumer ledger up to the date |

## Planted scenarios

Every edge case in the brief, mapped to the exact record where it occurs, followed by extra traps.

- **EC-01 Consumption exactly 50, 100, 200 and 300 units**
  - CON-0063 (DOMESTIC, NORMAL meter, not BPL): four consecutive 30-day periods with exactly 50, 100, 200 and 300 units -> each lands on a slab boundary (no pro-ration since 30 days) — `readings.csv RD-00301 (row 301); readings.csv RD-00401 (row 401); readings.csv RD-00501 (row 501); readings.csv RD-00600 (row 600)`
- **EC-02 Billing period of exactly 28 days and exactly 34 days**
  - CON-0054: period 2026-01-17 -> 2026-02-14 is exactly 28 days (inside 28-33, no pro-ration); 2026-02-14 -> 2026-03-20 is exactly 34 days -> slab limits pro-rated by 34/30 (rounded to the unit) — `readings.csv RD-00654 (row 654); readings.csv RD-00781 (row 781)`
- **EC-03 Maximum demand exactly 10% above sanctioned load**
  - CON-0091 (COMMERCIAL, 5 kW): recorded MD 5.50 kW = exactly 10% above -> no excess-demand charge and no regularisation flag; next reading MD 5.51 kW -> 0.51 kW excess at 2x fixed rate + flag — `readings.csv RD-00827 (row 827); readings.csv RD-00939 (row 939)`
- **EC-04 Net export month followed by import month that fully consumes banked units**
  - CON-0061 (NET, 3 kW solar on 4 kW load): the 2026-05-03 reading imports 220 and exports 310 -> 90 units banked, only fixed charge billed; the 2026-06-03 reading imports 400 and exports 280 -> net 120, the 90 banked units are fully drawn down first -> 30 units slab-billed, bank back to 0 — `readings.csv RD-00915 (row 915); readings.csv RD-01006 (row 1006)`
- **EC-05 Solar capacity exactly equal to sanctioned load**
  - CON-0049: solar_capacity_kw 3.00 = sanctioned_load_kw 3.00 -> NOT 'greater than' -> net-metering eligible (bill on net units) — `consumers.csv CON-0049 (row 49)`
- **EC-06 FAULTY month reconciled where actual consumption is lower than the estimate**
  - CON-0077: three NORMAL bills of 260, 250, 270 units (average 260) -> FAULTY reading billed at 260; the next NORMAL reading shows only 220 units actually consumed across both months (120 + 100) -> reconciliation is NEGATIVE (actual < estimated total): credit the excess with slabs re-applied to each month separately; minimum charge not applied to the FAULTY month — `readings.csv RD-00493 (row 493); readings.csv RD-00595 (row 595)`
- **EC-07 Payment on the 7th day after the bill date at 23:59**
  - CON-0008: bill on reading 2026-04-10; ONLINE payment at 2026-04-17 23:59:00 = 7th day after the bill date at 23:59 -> 1% prompt rebate (max Rs 100) + 0.5% online (max Rs 50) — `readings.csv RD-00845 (row 845); payments.csv PAY-00646 (row 646)`
- **EC-08 Tariff change effective on the reading date itself**
  - TO-2026 takes effect 2026-04-10, the same date as CON-0076's reading (period 2026-03-10 -> 2026-04-10); every consumer with read_day 10 hits the same boundary. State which tariff the reading day itself belongs to and apportion days accordingly — `tariff_orders.csv TO-2026 (row 2); readings.csv RD-00831 (row 831)`
- **Extra traps (not in the brief, but realistic):**
  - CON-0068: solar 3.00 kW > sanctioned 2.00 kW -> INELIGIBLE_NET, billed on gross import (export ignored) — `consumers.csv CON-0068 (row 68)`
  - CON-0044 (DOMESTIC, ~330 units/month) never pays -> arrears > Rs 1,000 over more than 2 consecutive bills -> DISCONNECTION_NOTICE, disconnection 15 days later; the RECONNECT request on 2026-06-20 has no payment behind it and must be REFUSED — `consumers.csv CON-0044 (row 44); commands.txt line 19`
  - CON-0011 (AGRICULTURE, 15 HP -> above the 10 HP subsidy limit, billed at Rs 3.00/unit) stops paying from the May 2026 bill -> arrears cross Rs 5,000 over more than 2 consecutive bills during June-October; a notice may issue but it must NOT be disconnected between June and November — `consumers.csv CON-0011 (row 11)`
  - CON-0001: the reading after 2025-12-24 comes 62 days later (> 45) -> split into two bills at the 30-day mark, 410 units apportioned by days (30/62 and 32/62) — `readings.csv RD-00698 (row 698)`
  - CON-0088: METER_CHANGE reading -> consumption = (old_meter_final - previous reading) + (kwh_import - new_meter_initial) — `readings.csv RD-00622 (row 622)`

## What is NOT in this pack

Expected outputs are not provided for this set. Validate your engine with your own test suite against the rules in your brief (BR-01 … BR-nn). A separate hidden input set with the same schema will be used at final evaluation; outputs are compared field-for-field, so follow the column formats above exactly in your own output.

## Output format expected at evaluation

Produce these CSV files (header row, same conventions as above, rows sorted as stated). Where the brief is silent on a format detail the choice below is binding for evaluation.

### `bills.csv`

One row per bill (split bills get two rows), sorted by bill_date then consumer_id. bill_id = BL-<consumer_id>-<YYYYMMDD>[-n].

Columns, in order: `bill_id`, `consumer_id`, `bill_date`, `period_from`, `period_to`, `days`, `tariff_ids`, `units_billed`, `banked_used`, `banked_closing`, `energy_charge`, `tod_adjustment`, `fixed_charge`, `excess_demand_charge`, `fac`, `duty`, `subsidy`, `minimum_charge_adjustment`, `reconciliation_adjustment`, `net_current`, `arrears`, `interest`, `total_due`, `due_date`, `flags`

### `bill_slabs.csv`

Slab breakup per bill.

Columns, in order: `bill_id`, `tariff_id`, `slab_no`, `units`, `rate_per_unit`, `amount`

### `ledger.csv`

One row per bill, payment, interest, rebate, fee or settlement entry.

Columns, in order: `consumer_id`, `entry_ts`, `entry_type`, `reference`, `debit`, `credit`, `balance`

### `consumer_state.csv`

One row per state change.

Columns, in order: `consumer_id`, `event_date`, `state`, `reason`

### `arrears_ageing.csv`

One row per consumer with arrears per PRINT_ARREARS_AGEING.

Columns, in order: `as_of_date`, `consumer_id`, `bucket_0_30`, `bucket_31_60`, `bucket_61_90`, `bucket_over_90`, `total`

Binding choices: `flags` is a ';'-separated set of LOAD_REGULARISATION, INELIGIBLE_NET, ESTIMATED, FAULTY_AVERAGE, RECONCILED, SPLIT_BILL, MINIMUM_APPLIED; `state` is CONNECTED, DISCONNECTION_NOTICE, DISCONNECTED, RECONNECTED; `entry_type` BILL, PAYMENT, INTEREST, REBATE, RECONNECTION_FEE, NET_SETTLEMENT; units are whole kWh; money 2 decimals.
