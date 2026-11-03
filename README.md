# T098-PS-073 | Electricity Billing Engine

**A Python-based electricity billing system supporting slab tariffs, Time-of-Day (ToD) billing, net metering, subsidies, payments, arrears and disconnection management.**

## Project Overview

The Electricity Billing Engine is a backend application designed to automate electricity bill calculation and consumer account management.

The system calculates electricity bills based on consumer category, applicable tariff slabs, meter readings and billing rules. It also supports Time-of-Day adjustments, solar net-metering settlements, government subsidies, payment processing and arrears management.

The application is being developed using Python and is designed to process structured input files and generate detailed billing outputs and reports.

## Project Details

 Detail and Description 
 Project ID - T098-PS-073 
 Project Type - Backend Application 
 Programming Language - Python 3.10+ 
 Input Format - CSV / Command Files 
 Testing Framework - Pytest 
 Interface - Command-file-driven 
 Project Status - In Development 

## Key Features

### 1. Consumer Management
- Register and manage electricity consumers.
- Support Domestic, Commercial, Industrial LT and Agriculture categories.
- Maintain sanctioned load, meter type, connection details and security deposits.
- Support BPL consumer identification.

### 2. Slab-Based Billing
- Calculate electricity charges using category-specific tariff slabs.
- Support telescopic slab calculations for domestic consumers.
- Apply fixed charges based on sanctioned load.
- Handle minimum billing requirements and excess load penalties.

### 3. Time-of-Day (ToD) Billing
- Support ToD-enabled meters.
- Apply peak-hour and off-peak-hour tariff adjustments.
- Calculate applicable charges based on consumption across time zones.

### 4. Net Metering and Solar Settlement
- Calculate net electricity consumption using imported and exported units.
- Maintain banked solar energy units.
- Adjust banked units against future consumption.
- Support annual settlement of remaining banked units.
- Validate solar capacity eligibility.

### 5. Subsidies and Rebates
- Apply eligible BPL consumer benefits.
- Calculate payment-based rebates.
- Support online payment incentives.

### 6. Payments and Arrears
- Record consumer payments.
- Maintain consumer payment ledgers.
- Calculate delayed payment interest.
- Apply payments towards outstanding interest and principal.

### 7. Disconnection and Reconnection
- Track outstanding arrears.
- Generate disconnection notices based on applicable rules.
- Manage disconnection and reconnection conditions.
- Apply special disconnection restrictions for agricultural consumers.

### 8. Reports and Billing Records
- Generate detailed electricity bills.
- Print consumer billing history.
- Generate consumer ledger statements.
- Produce arrears ageing reports.

## Technology Stack

- **Programming Language:** Python 3.10+
- **Testing:** Pytest
- **Data Processing:** Python CSV module
- **Date and Time:** Python datetime
- **Financial Calculations:** Python Decimal
- **Version Control:** Git and GitHub
- **Development Environment:** Visual Studio Code

## Project Structure


T098-PS-073/
│
├── main.py
├── models/
├── services/
├── validators/
├── utils/
├── commands/
├── reports/
├── tests/
├── data/
├── output/
└── docs/


### Folder Description

 Folder and its Purpose:
 
 models - Consumer, meter, tariff, bill and payment models 
 services - Billing calculations and business logic 
 validators - Input validation 
 utils - CSV processing and utility functions 
 commands - Command-file processing 
 reports - Billing and account reports 
 tests - Automated test cases 
 data - Input CSV files 
 output - Generated bills and reports 
 docs - Project documentation and decision log 

## Business Rules

The application is designed to implement the following major billing rules:

- Monthly billing with billing-period adjustments.
- Category-specific slab tariffs.
- Fixed charges and minimum bill requirements.
- Time-of-Day tariff adjustments.
- Fuel Adjustment Cost (FAC) and electricity duty.
- Solar net-metering and annual settlement.
- Estimated and faulty meter reading adjustments.
- BPL subsidies and timely payment rebates.
- Delayed payment interest and arrears tracking.
- Disconnection and reconnection management.
- Mid-cycle tariff changes.

## Testing

The project will include automated tests for:

- Slab tariff calculations.
- Net-metering calculations.
- Time-of-Day adjustments.
- Bill generation.
- Payment and arrears processing.
- Meter reading validation.
- Disconnection and reconnection conditions.

Tests will be executed using Pytest.

## Team Members


 Samhitha S Shankar-1AT24IS171
 Satyam Singh-1AT24IS172 

**Section:** ISE D  
**Team ID:** T098

## Project Objective

The objective of this project is to develop a reliable and modular electricity billing engine that accurately handles complex tariff structures, consumer categories, solar energy settlements and payment-related operations while maintaining transparent billing records.

---

**Project ID:** T098-PS-073  
**Project Name:** Electricity Billing Engine with Slab Tariffs, Time-of-Day, Net-Metering and Arrears
