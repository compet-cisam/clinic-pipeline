def save_data_to_file(patient_data):
    """Save extracted patient data to a JSON file."""
    import json
    from datetime import datetime

    filename = f"patient_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(patient_data, f, indent=2, ensure_ascii=False)
        print(f"Patient data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to file: {e}")
