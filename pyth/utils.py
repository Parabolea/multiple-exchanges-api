import random
import math
import json
from datetime import datetime
from typing import List, Dict


def get_random_number():
    min_val = 40
    max_val = 90
    random_num = random.uniform(min_val, max_val)
    return round(random_num, 5)

def safe_json_dumps(data):
    """
    Serializes Python objects to a JSON-formatted string, replacing NaN values with 'NaN' (string).
    """
    def replace_nan(obj):
        if isinstance(obj, list):
            return [replace_nan(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: replace_nan(value) for key, value in obj.items()}
        elif isinstance(obj, float) and math.isnan(obj):
            return 0
        else:
            return obj

    return json.dumps(replace_nan(data))

def filter_future_events(data: List[Dict[str, str]], key_name: str) -> List[Dict[str, str]]:
    today = datetime.today().date()  # Get today's date

    # Filter data based on ex_dividend_date
    filtered_data = [
        item for item in data
        if datetime.strptime(item[key_name], "%Y-%m-%d").date() >= today
    ]

    return filtered_data
