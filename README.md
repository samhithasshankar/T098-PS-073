
T098-PS-073 – Electricity Billing Engine
Team: T098
Project ID: PS-073
Project Title: Electricity Billing Engine with Slab Tariffs, Time-of-Day, Net-Metering and Arrears
Programming Language: Python 3.10+
Development Status: In Progress

1. Project Overview
The Electricity Billing Engine is a command-driven Python application that processes consumer details, electricity tariff orders, meter readings and payments to generate electricity bills.

The system implements slab-based tariffs, Time-of-Day (ToD) billing, net metering, subsidies, payment processing, arrears calculation and disconnection management according to the PS-073 project requirements.

The application uses the official sample data pack provided by 10 SECONDS for Team T098.

2. Technology Stack
Python 3.10+
CSV files for input and output data
Python standard library
pytest for testing
3. Project Structure
T098-PS-073/
│
├── main.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── consumers.csv
│   ├── tariff_orders.csv
│   ├── tariff_slabs.csv
│   ├── readings.csv
│   ├── payments.csv
│   ├── commands.txt
│   └── README.md
│
├── models/
├── services/
├── validators/
├── utils/
├── commands/
├── reports/
├── tests/
├── docs/
└── output/
4. Official Sample Data
The application uses the sample data pack supplied by 10 SECONDS.

Input file	Description	Data rows
consumers.csv	Consumer master records	100
tariff_orders.csv	Electricity tariff orders	2
tariff_slabs.csv	Category-wise tariff slabs	18
readings.csv	Meter readings	1,499
payments.csv	Consumer payment records	1,208
commands.txt	Required processing commands	36
The consumer distribution is:

Domestic: 60
Commercial: 20
Industrial LT: 12
Agriculture: 8
The input files must be used without changing their supplied records or tariff values.

5. Functional Requirements
The billing engine is designed to implement the following required functionality:

Consumer registration and category management.
Tariff order and slab-based billing.
Fixed charge and minimum charge calculation.
Time-of-Day billing adjustments.
Net-metering, energy banking and settlement.
BPL subsidy and payment rebates.
Normal, estimated, faulty and meter-change reading processing.
Tariff changes during billing periods.
Payment processing and arrears management.
Interest calculation on overdue payments.
Disconnection and reconnection management.
Bill generation, consumer ledger and arrears ageing reports.
All calculations must follow the business rules in the official project brief and the applicable tariff order.

6. Input Data Format
consumers.csv
Contains consumer details, including:

Consumer ID and name
Consumer category
Sanctioned load
Pump horsepower
Connection date
Meter type
Solar capacity
BPL status
Security deposit
Reading day
City and mobile number
tariff_orders.csv
Contains tariff order details, including:

Tariff ID and effective date
FAC per unit
Electricity duty percentages
Fixed charges by category
Minimum charges
ToD peak and off-peak percentages
Net-metering settlement rate
Agriculture subsidy horsepower limit
tariff_slabs.csv
Contains category-wise slab details for each tariff order, including slab number, unit limits and rate per unit.

readings.csv
Contains meter reading details, including:

Reading ID and consumer ID
Reading timestamp and status
Cumulative import and export readings
ToD zone-wise consumption
Maximum demand
Old and new meter readings for meter changes
payments.csv
Contains payment ID, consumer ID, payment timestamp, payment amount and payment mode.

7. Command Processing
The application processes commands from commands.txt strictly in file order.

Supported commands in the supplied sample data:

Command	Arguments	Purpose
RECONNECT	consumer_id, timestamp	Process a reconnection request
PRINT_ARREARS_AGEING	as_of_date	Generate arrears ageing report
PRINT_BILL	consumer_id, bill_month	Print bills for a consumer and month
PRINT_LEDGER	consumer_id, as_of_date	Generate consumer ledger
Command format:

COMMAND_NAME|argument1|argument2
Lines beginning with # and blank lines are ignored. Empty arguments are treated as not supplied.

8. Required Business Rules
The engine must implement the business rules BR-01 through BR-12 from the official PS-073 problem statement.

These include:

Billing-period and slab-limit proration.
Category-wise tariff calculation.
Fixed charges and excess-demand charges.
Minimum billing requirements.
ToD adjustments.
FAC and electricity duty.
Net-metering and banked-unit settlement.
Estimated and faulty reading reconciliation.
BPL subsidies and payment rebates.
Payment allocation and overdue interest.
Disconnection and reconnection conditions.
Mid-cycle tariff changes.
Tariff values and other configurable parameters must be obtained from the supplied tariff data and applicable business rules rather than replaced with invented values.

9. Planted Edge Cases
The official sample data contains scenarios that must be validated through the test suite.

Scenario	Consumer / Record
Exact slab boundaries: 50, 100, 200 and 300 units	CON-0063
28-day and 34-day billing periods	CON-0054
Maximum demand exactly 10% above sanctioned load	CON-0091
Net export followed by banked-unit consumption	CON-0061
Solar capacity equal to sanctioned load	CON-0049
Faulty reading with negative reconciliation	CON-0077
Payment on seventh day at 23:59	CON-0008
Tariff change effective on reading date	CON-0076
Solar capacity greater than sanctioned load	CON-0068
Disconnection and refused reconnection	CON-0044
Agriculture disconnection restriction	CON-0011
Billing period longer than 45 days	CON-0001
Meter replacement calculation	CON-0088
The exact record IDs and row numbers are documented in the original sample-data README inside the data directory.

10. Expected Output Files
The application must generate the following five CSV files in the required evaluation format.

bills.csv
Contains one row per generated bill.

Columns:

bill_id,consumer_id,bill_date,period_from,period_to,days,tariff_ids,units_billed,banked_used,banked_closing,energy_charge,tod_adjustment,fixed_charge,excess_demand_charge,fac,duty,subsidy,minimum_charge_adjustment,reconciliation_adjustment,net_current,arrears,interest,total_due,due_date,flags
bill_slabs.csv
Contains the slab-wise breakup for each bill.

bill_id
