import os
from scraper import Scraper
from dotenv import load_dotenv
from utils import save_data_to_file


def main():
    load_dotenv()

    url = os.getenv("URL")
    username = os.getenv("USERNAME_")
    password = os.getenv("PASSWORD_")

    with Scraper(
        url=url, username=username, password=password, headless=False
    ) as scraper:
        print("Scraper initialized...")

        # Step 1: Login
        if scraper.login():
            patient_data = scraper.extract_patient_data()

            if patient_data:
                print("\n=== EXTRACTED PATIENT DATA ===")
                for i, patient in enumerate(patient_data, 1):
                    print(f"\nPatient Record {i}:")
                    print(f"  Total Patients: {patient.get('total_patients', 'N/A')}")
                    print(f"  Page Number: {patient.get('page_number', 'N/A')}")
                    print(
                        f"  Patient Index on Page: "
                        f"{patient.get('patient_index_on_page', 'N/A')}"
                    )
                    print(f"  Date/Hour: {patient.get('date_hour', 'N/A')}")
                    print(f"  Medical Care: {patient.get('medical_care', 'N/A')}")
                    print(
                        f"  Extracted At: {patient.get('extraction_timestamp', 'N/A')}"
                    )

                save_data_to_file(patient_data)

            else:
                print("No patient data could be extracted.")

        else:
            print("Login failed. Please check your credentials and URL.")
            scraper.take_screenshot("images/login_failed.png")


if __name__ == "__main__":
    main()
