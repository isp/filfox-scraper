import requests
import csv

def fetch_table_data(filecoin_address, page, page_size, data_type):
    url = f"https://filfox.info/api/v1/address/{filecoin_address}/messages"
    params = {"pageSize": page_size, "page": page, "type": data_type}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception if the response status code is not 2xx
        return response.json(), response.url
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None, None

def extract_data_from_api_response(api_response):
    if not api_response or "messages" not in api_response:
        print("No data found.")
        return []

    messages = api_response["messages"]
    headers = ["Message ID", "Height", "Time", "From", "To", "Method", "Value", "Status"]
    rows = []

    for message in messages:
        row = [
            message["cid"],
            message["height"],
            message["timestamp"],
            message["from"],
            message["to"],
            message["method"],
            format_value(message["value"]),  # Format the Value column here
            message["receipt"]["exitCode"] if "receipt" in message else None,
        ]
        rows.append(row)

    return headers, rows

def format_value(value):
    # Convert the value to a float and then format it to have 18 decimal places
    return "{:.18f}".format(float(value) / 1e18)

def save_to_csv(filecoin_address, headers, rows):
    if not headers or not rows:
        print("No data to save.")
        return

    file_name = f"{filecoin_address}_filecoin_data.csv"

    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Data successfully saved to {file_name}")

def fetch_all_transfers(filecoin_address):
    page_size = 100
    total_count_response, _ = fetch_table_data(filecoin_address, 0, 1, "transfer")
    total_count = total_count_response.get("totalCount", 0)

    if total_count == 0:
        print("No data found.")
        return

    total_pages = (total_count + page_size - 1) // page_size
    print(f"Total transfers to fetch: {total_count}")

    all_rows = []
    for page in range(1, total_pages + 1):
        print(f"Fetching data on page {page}/{total_pages}")
        api_response, url = fetch_table_data(filecoin_address, page, page_size, "transfer")
        if api_response:
            headers, rows = extract_data_from_api_response(api_response)
            if headers and rows:
                all_rows.extend(rows)
            else:
                print(f"Failed to fetch data on page {page} or 'messages' not found.")
        else:
            print(f"Failed to fetch data on page {page} or 'messages' not found. URL: {url}")

    return headers, all_rows

if __name__ == "__main__":
    filecoin_address = input("Enter the Filecoin address to scrape data from: ")
    headers, all_rows = fetch_all_transfers(filecoin_address)
    if headers and all_rows:
        # Save the data to a CSV file with the entered Filecoin address as the filename
        save_to_csv(filecoin_address, headers, all_rows)
