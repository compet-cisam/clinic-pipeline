import re
from logger_config import get_logger


def clean_date_hour(date_hour_text):
    """
    Clean the date_hour field by removing the 'Data/hora\n' prefix using regex.

    Args:
        date_hour_text (str): Raw text extracted from the webpage

    Returns:
        str: Cleaned date string (e.g., "25/05/2025")
    """
    if not date_hour_text or date_hour_text == "Not found":
        return date_hour_text

    cleaned_date = re.sub(
        r"^Data/hora\s*\n\s*", "", date_hour_text, flags=re.IGNORECASE
    )

    cleaned_date = cleaned_date.strip()

    return cleaned_date


def clean_medical_care(medical_care_text):
    """
    Clean the medical_care field by removing any unwanted prefixes.

    Args:
        medical_care_text (str): Raw text extracted from the webpage

    Returns:
        str: Cleaned medical care text
    """
    if not medical_care_text or medical_care_text == "Not found":
        return medical_care_text

    cleaned_text = re.sub(
        r"^Dados do atendimento\s*\n\s*", "", medical_care_text, flags=re.IGNORECASE
    )

    cleaned_text = cleaned_text.strip()

    return cleaned_text


def clean_patient_data(patient_data):
    """
    Clean all patient data before saving to file.

    Args:
        patient_data (list): List of patient records

    Returns:
        list: Cleaned patient data
    """
    cleaned_data = []

    for record in patient_data:
        cleaned_record = record.copy()

        if "date_hour" in cleaned_record:
            cleaned_record["date_hour"] = clean_date_hour(cleaned_record["date_hour"])

        if "medical_care" in cleaned_record:
            cleaned_record["medical_care"] = clean_medical_care(
                cleaned_record["medical_care"]
            )

        cleaned_data.append(cleaned_record)

    return cleaned_data


def save_data_to_file(patient_data):
    """Save extracted patient data to a JSON file after cleaning."""
    import json
    from datetime import datetime

    logger = get_logger()

    cleaned_data = clean_patient_data(patient_data)

    filename = f"patient_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Patient data saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to file: {e}")
