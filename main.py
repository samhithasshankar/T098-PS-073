
"""
T098-PS-073: Electricity Billing Engine

Application entry point.
Loads and validates official input data,
executes billing commands, and generates reports.
"""

from utils.data_loader import load_all_data, print_data_summary
from services.command_execution_service import execute_project


def main():
    print("=" * 65)
    print("          T098-PS-073 ELECTRICITY BILLING ENGINE")
    print("=" * 65)

    try:
        # Step 1: Load and validate input data
        print("\n[1/3] Loading official project data...")

        data = load_all_data()

        print("\nInput data loaded and validated successfully.")
        print_data_summary(data)

        # Step 2: Execute the billing engine
        print("\n[2/3] Executing electricity billing engine...")

        result = execute_project(data)

        # Step 3: Display execution summary
        print("\n[3/3] Billing execution completed.")

        print("\n" + "=" * 65)
        print("                 EXECUTION SUMMARY")
        print("=" * 65)

        print(
            f"Commands executed : "
            f"{result['commands_executed']}"
        )

        print(
            f"Bills calculated  : "
            f"{result['bills_calculated']}"
        )

        print(
            f"Ledger entries    : "
            f"{result['ledger_entries']}"
        )

        print("\nGenerated output reports:")

        for report_name, report_path in result["reports"].items():
            print(f"  {report_name}: {report_path}")

        print("\n" + "=" * 65)
        print("       ELECTRICITY BILLING ENGINE COMPLETED")
        print("=" * 65)

    except FileNotFoundError as error:
        print("\nERROR: Required input file not found.")
        print(error)

    except ValueError as error:
        print("\nERROR: Input data validation or processing failed.")
        print(error)

    except Exception as error:
        print("\nUNEXPECTED ERROR:")
        print(f"{type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()
