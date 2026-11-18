
# T098-PS-073 - Electricity Billing Engine

**Team:** T098
**Project ID:** PS-073
**Project Title:** Electricity Billing Engine with Slab Tariffs, Time-of-Day, Net-Metering and Arrears
**Programming Language:** Python 3.10+
**Development Status:** Implementation and execution verified; final evaluation pending.

---

## 1. Project Overview

The Electricity Billing Engine is a command-driven Python application developed to process electricity consumer information, tariff orders, meter readings and payment records.

The application generates electricity bills by implementing slab-based tariffs, Time-of-Day (ToD) adjustments, net metering, subsidies, payment processing, arrears calculation, overdue interest, disconnection and reconnection management.

The project follows the requirements of the official 10 SECONDS capstone problem statement PS-073 for Team T098.

The application uses the supplied official sample data without generating or modifying sample records.

## 2. Technology Stack

- Python 3.10+
- CSV for input and output data
- Python standard library
- pytest for automated testing

## 3. Project Structure

```text
T098-PS-073/
|
|-- main.py
|-- requirements.txt
|-- README.md
|
|-- data/
|   |-- consumers.csv
|   |-- tariff_orders.csv
|   |-- tariff_slabs.csv
|   |-- readings.csv
|   |-- payments.csv
|   |-- commands.txt
|   |-- README.md
|
|-- commands/
|   |-- command_processor.py
|
|-- models/
|
|-- services/
|   |-- arrears_ageing_service.py
|   |-- arrears_service.py
|   |-- benefit_service.py
|   |-- billing_engine.py
|   |-- billing_service.py
|   |-- command_execution_service.py
|   |-- disconnection_service.py
|   |-- fixed_charge_service.py
|   |-- minimum_charge_service.py
|   |-- net_metering_service.py
|   |-- payment_processing_service.py
|   |-- reading_processor.py
|   |-- reading_service.py
|   |-- rebate_service.py
|   |-- reconciliation_service.py
|   |-- slab_calculator.py
|   |-- tariff_period_service.py
|   |-- tariff_service.py
|   |-- tax_service.py
|   |-- tod_service.py
|
|-- validators/
|
|-- utils/
|   |-- data_loader.py
|
|-- reports/
|   |-- csv_report_service.py
|
|-- tests/
|   |-- test_arrears_ageing_service.py
|   |-- test_arrears_service.py
|   |-- test_benefit_service.py
|   |-- test_billing_engine.py
|   |-- test_billing_service.py
|   |-- test_command_executor.py
|   |-- test_csv_report_service.py
|   |-- test_disconnection_service.py
|   |-- test_fixed_charge_service.py
|   |-- test_minimum_charge_service.py
|   |-- test_net_metering_service.py
|   |-- test_payment_processing_service.py
|   |-- test_reading_processor.py
|   |-- test_reading_service.py
|   |-- test_rebate_service.py
|   |-- test_reconciliation_service.py
|   |-- test_slab_calculator.py
|   |-- test_tariff_period_service.py
|   |-- test_tax_service.py
|   |-- test_tod_service.py
|
|-- docs/
|   |-- decision-log.md
|
|-- output/
    |-- bills.csv
    |-- bill_slabs.csv
    |-- ledger.csv
    |-- consumer_state.csv
    |-- arrears_ageing.csv
```

## 4. Official Sample Data

The application uses the sample data pack supplied by 10 SECONDS.

| Input File | Description | Data Records |
|---|---|---:|
| consumers.csv | Consumer master records | 100 |
| tariff_orders.csv | Electricity tariff orders | 2 |
| tariff_slabs.csv | Category-wise tariff slabs | 18 |
| readings.csv | Meter reading records | 1,499 |
| payments.csv | Consumer payment records | 1,208 |
| commands.txt | Processing commands | 36 |

### Consumer Distribution

| Consumer Category | Count |
|---|---:|
| Domestic | 60 |
| Commercial | 20 |
| Industrial LT | 12 |
| Agriculture | 8 |
| **Total** | **100** |

The supplied input records and tariff values must remain unchanged.

## 5. Functional Requirements

The billing engine implements the following functionality:

1. Consumer information and category management.
2. Tariff order and slab-based billing.
3. Fixed charge and minimum charge calculation.
4. Time-of-Day billing adjustments.
5. Net metering, energy banking and settlement.
6. BPL subsidy and payment rebates.
7. Normal, estimated, faulty and meter replacement reading processing.
8. Tariff changes during billing periods.
9. Payment processing and arrears management.
10. Interest calculation on overdue payments.
11. Disconnection and reconnection management.
12. Bill generation, consumer ledger and arrears ageing reports.

All billing calculations must follow the official project business rules and applicable tariff data.

## 6. Input Data Format

### consumers.csv

Contains consumer master information, including:

- Consumer ID and name
- Consumer category
- Sanctioned load
- Pump horsepower
- Connection date
- Meter type
- Solar capacity
- BPL status
- Security deposit
- Reading day
- City and mobile number

### tariff_orders.csv

Contains tariff order information, including:

- Tariff ID and effective date
- FAC per unit
- Electricity duty percentages
- Fixed charges by category
- Minimum charges
- ToD peak and off-peak percentages
- Net-metering settlement rate
- Agriculture subsidy horsepower limit

### tariff_slabs.csv

Contains category-wise tariff slab information for each tariff order, including:

- Tariff ID
- Slab number
- Unit limits
- Rate per unit

### readings.csv

Contains meter reading information, including:

- Reading ID and consumer ID
- Reading timestamp and status
- Cumulative import and export readings
- ToD zone-wise consumption
- Maximum demand
- Old and new meter readings for meter changes

### payments.csv

Contains payment information, including:

- Payment ID
- Consumer ID
- Payment timestamp
- Payment amount
- Payment mode

### commands.txt

Contains the processing commands supplied with the official sample data.

## 7. Command Processing

The application reads commands from `commands.txt` and processes them in their supplied file order.

The command processor supports operations such as:

| Command | Purpose |
|---|---|
| RECONNECT | Process a consumer reconnection request |
| PRINT_ARREARS_AGEING | Generate an arrears ageing report |
| PRINT_BILL | Print bills for a consumer and billing month |
| PRINT_LEDGER | Generate a consumer ledger |

The complete command list and arguments are defined by the supplied command file.

### Command Format

```text
COMMAND_NAME|argument1|argument2
```

Lines beginning with `#` and blank lines are ignored. Empty arguments are treated as not supplied.

## 8. Required Business Rules

The engine implements the business rules BR-01 through BR-12 from the official PS-073 problem statement.

The implemented calculation areas include:

- Billing-period and slab-limit proration.
- Category-wise tariff calculation.
- Fixed charges and excess-demand charges.
- Minimum billing requirements.
- Time-of-Day adjustments.
- FAC and electricity duty.
- Net-metering and banked-unit settlement.
- Estimated and faulty reading reconciliation.
- BPL subsidies and payment rebates.
- Payment allocation and overdue interest.
- Disconnection and reconnection conditions.
- Mid-cycle tariff changes.

Tariff values and configurable parameters are obtained from the supplied tariff data and applicable business rules.

## 9. Planted Edge Cases

The official sample data contains scenarios used for validation.

| Scenario | Consumer / Record |
|---|---|
| Exact slab boundaries: 50, 100, 200 and 300 units | CON-0063 |
| 28-day and 34-day billing periods | CON-0054 |
| Maximum demand exactly 10% above sanctioned load | CON-0091 |
| Net export followed by banked-unit consumption | CON-0061 |
| Solar capacity equal to sanctioned load | CON-0049 |
| Faulty reading with negative reconciliation | CON-0077 |
| Payment on seventh day at 23:59 | CON-0008 |
| Tariff change effective on reading date | CON-0076 |
| Solar capacity greater than sanctioned load | CON-0068 |
| Disconnection and refused reconnection | CON-0044 |
| Agriculture disconnection restriction | CON-0011 |
| Billing period longer than 45 days | CON-0001 |
| Meter replacement calculation | CON-0088 |

The corresponding record IDs and row numbers are documented in the original sample-data README inside the data directory.

## 10. Expected Output Files

The application generates five CSV reports in the `output/` directory.

### 10.1 bills.csv

Contains one row per generated bill.

Columns:

```text
bill_id,consumer_id,bill_date,period_from,period_to,days,tariff_ids,units_billed,banked_used,banked_closing,energy_charge,tod_adjustment,fixed_charge,excess_demand_charge,fac,duty,subsidy,minimum_charge_adjustment,reconciliation_adjustment,net_current,arrears,interest,total_due,due_date,flags
```

### 10.2 bill_slabs.csv

Contains the slab-wise breakup of every generated bill.

Columns:

```text
bill_id,tariff_id,slab_no,units,rate_per_unit,amount
```

### 10.3 ledger.csv

Contains consumer-wise financial ledger entries.

Columns:

```text
consumer_id,entry_ts,entry_type,reference,debit,credit,balance
```

### 10.4 consumer_state.csv

Contains consumer status changes and related events.

Columns:

```text
consumer_id,event_date,state,reason
```

### 10.5 arrears_ageing.csv

Contains consumer-wise outstanding arrears grouped into ageing buckets.

Columns:

```text
as_of_date,consumer_id,bucket_0_30,bucket_31_60,bucket_61_90,bucket_over_90,total
```

### Verified Sample Execution

The official sample data execution generated:

| Output | Verified Records |
|---|---:|
| bills.csv | 1,500 |
| bill_slabs.csv | 3,795 |
| ledger.csv | 713 |
| consumer_state.csv | 157 |
| arrears_ageing.csv | 1,300 |

These counts describe the verified sample execution and are not fixed limits for other input datasets.

## 11. Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/samhithasshankar/T098-PS-073.git
```

### Step 2: Open the Project

```bash
cd T098-PS-073
```

### Step 3: Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

### Step 4: Activate the Virtual Environment

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use Command Prompt:

```cmd
venv\Scripts\activate.bat
```

### Step 5: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

## 12. Running the Application

From the project root directory, execute:

```bash
python main.py
```

The application:

1. Loads the official input files.
2. Validates input data and references.
3. Processes the supplied commands.
4. Executes the billing calculations.
5. Generates the five CSV output reports.
6. Displays an execution summary.

Generated reports are saved in:

```text
output/
```

## 13. Running Automated Tests

The project uses pytest for automated testing.

Run the complete test suite:

```bash
python -m pytest -q
```

The verified test suite result during project validation was:

```text
137 passed
```

The test suite covers billing calculations, slab calculations, net metering, ToD, taxes, payments, arrears, reconciliation, disconnection, reconnection and report generation.

## 14. Execution Summary

Verified execution using the supplied sample dataset:

| Metric | Result |
|---|---:|
| Consumers loaded | 100 |
| Tariff orders loaded | 2 |
| Tariff slabs loaded | 18 |
| Meter readings loaded | 1,499 |
| Payments loaded | 1,208 |
| Commands executed | 36 |
| Bills calculated | 1,500 |
| Ledger entries generated | 697 |
| CSV reports generated | 5 |

The application entry point and report generation were successfully verified using:

```bash
python main.py
```

## 15. Repository and video link

**GitHub Repository:**

https://github.com/samhithasshankar/T098-PS-073

**Video Link:**

https://drive.google.com/drive/folders/1c0hNtaePdx95sRMROu-wmbTY3MEiKYZh?usp=sharing

---

**Team T098 | PS-073 | Electricity Billing Engine**
