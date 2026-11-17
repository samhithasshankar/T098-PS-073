# DECISION LOG
## T098-PS-073 – Electricity Billing Engine

**Team:** T098  
**Project:** Electricity Billing Engine with Slab Tariffs, Time-of-Day, Net-Metering and Arrears  
**Team Members:**
- Samhitha S Shankar – 1AT24IS171
- Satyam Singh – 1AT24IS172

### 1. Technology Selection

**Decision:** Use Python 3.10+ as the implementation language.

**Reason:** Python supports modular development, CSV processing, data validation and financial calculations. It also provides a suitable environment for implementing and testing the billing engine.

**Alternatives considered:** Java and other programming languages.

**Outcome:** Python was selected for the complete backend implementation.

### 2. Application Architecture

**Decision:** Develop a command-file-driven backend application without a graphical user interface.

**Reason:** The primary requirement is accurate processing of electricity billing data and commands. A user interface is not necessary for the core assignment.

**Outcome:** The application processes input files and commands and generates structured output reports.

### 3. Data Storage and Input Format

**Decision:** Use CSV files for consumer details, tariff orders, tariff slabs, meter readings and payments.

**Reason:** The official project sample data is provided in CSV format. Using the supplied format maintains compatibility with the assignment requirements.

**Outcome:** The original sample records and tariff values are retained without modification.

### 4. Modular Code Structure

**Decision:** Separate the application into models, services, validators, utilities, commands, reports and tests.

**Reason:** Modular development improves maintainability, readability, debugging and independent testing of billing components.

**Outcome:** Individual responsibilities such as reading processing, tariff calculation, billing, payments and reporting are handled by separate modules.

### 5. Financial Calculation Precision

**Decision:** Use Python's Decimal arithmetic for monetary and tariff calculations.

**Reason:** Binary floating-point arithmetic can introduce precision errors in financial calculations. Decimal supports more reliable monetary calculations and rounding.

**Outcome:** Billing components use decimal-based calculations wherever precision is important.

### 6. Tariff Configuration

**Decision:** Load tariff orders and category-wise slab rates from the supplied input files instead of relying exclusively on hard-coded tariff values.

**Reason:** Electricity tariffs can change over time. Data-driven tariff configuration allows the engine to select applicable tariffs according to their effective dates.

**Outcome:** The system supports tariff selection and billing-period splitting when tariff changes occur.

### 7. Billing and Net-Metering Processing

**Decision:** Implement separate processing for slab tariffs, Time-of-Day adjustments, net metering, subsidies, fixed charges, taxes and minimum charges.

**Reason:** Different consumer categories and meter types require different billing treatments.

**Outcome:** The engine supports the required billing categories, eligible TOD meters, net-metering bank balances and applicable adjustments.

### 8. Automated Testing

**Decision:** Use pytest for automated testing.

**Reason:** Automated tests help verify individual calculation modules, business rules, integration workflows and boundary conditions.

**Outcome:** The recorded test execution completed successfully with 137 passing tests.

### 9. Command Processing

**Decision:** Process the supplied commands in the order in which they appear in commands.txt.

**Reason:** Maintaining command order preserves the expected sequence of billing, account updates and report generation.

**Outcome:** The application supports the supplied command-driven workflow.

### 10. Report Generation

**Decision:** Generate five CSV output reports.

**Reason:** Structured reports make billing calculations, account transactions and consumer service status easier to inspect and verify.

**Outcome:** The application generates:
- bills.csv
- bill_slabs.csv
- ledger.csv
- consumer_state.csv
- arrears_ageing.csv

### 11. Version Control

**Decision:** Use Git and GitHub for source-code version control and project collaboration.

**Reason:** Version control helps maintain project history, track changes and share the implementation with team members.

**Outcome:** The project is maintained in the T098-PS-073 GitHub repository.

### 12. Scope Management

**Decision:** Prioritise mandatory assignment requirements before optional enhancements.

**Reason:** The main objective is to satisfy the specified billing business rules and produce correct evaluation outputs.

**Outcome:** Optional prepaid metering and three-phase demand/power-factor billing enhancements are excluded from the current implementation scope.

---

**Decision Log Status:** Prepared for final project submission  
**Project:** T098-PS-073  
**Team:** T098 – ISE D