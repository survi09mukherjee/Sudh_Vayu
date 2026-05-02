digital_twin = {}

def process_data(data):
    digital_twin.update(data)

    # Basic logic
    if data.get("co", 0) > 10:
        digital_twin["risk"] = "HIGH"
    else:
        digital_twin["risk"] = "LOW"

    return digital_twin