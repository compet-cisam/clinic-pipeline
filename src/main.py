import os
from scraper import Scraper
from dotenv import load_dotenv
from utils import save_data_to_file
from logger_config import setup_logger


def main():
    # Setup logger
    logger = setup_logger()

    load_dotenv()

    url = os.getenv("URL")
    username = os.getenv("USERNAME_")
    password = os.getenv("PASSWORD_")

    with Scraper(
        url=url, username=username, password=password, headless=True
    ) as scraper:
        logger.info("Scraper initialized...")

        # Step 1: Login
        if scraper.login():
            patient_data = scraper.extract_patient_data()
            save_data_to_file(patient_data)

        else:
            logger.error("Login failed. Please check your credentials and URL.")
            scraper.take_screenshot("images/login_failed.png")


if __name__ == "__main__":
    main()
