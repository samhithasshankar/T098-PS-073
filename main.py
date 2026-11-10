
"""
T098-PS-073: Electricity Billing Engine

Application entry point.
Loads and validates the official sample data.
"""

from pprint import pprint

from utils.data_loader import load_all_data


def main():
    print("=" * 60)
    print("       T098-PS-073 ELECTRICITY BILLING ENGINE")
    print("=" * 60)

    try:
        print("\nLoading project data...")

        data = load_all_data()

        print("\nData loaded successfully!")

        print("\nLoaded data summary:")
        pprint(data)

        print("\n" + "=" * 60)
        print("DATA LOADING COMPLETED")
        print("=" * 60)

    except FileNotFoundError as error:
        print("\nERROR: Required data file not found.")
        print(error)

    except ValueError as error:
        print("\nERROR: Data validation failed.")
        print(error)

    except Exception as error:
        print("\nUNEXPECTED ERROR:")
        print(error)


if __name__ == "__main__":
    main()
