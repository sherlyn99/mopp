import requests
import html
import logging
import time
import secrets
import string
import csv
import os
from pathlib import Path

def generate_random_string(length=30):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(secrets.choice(alphabet) for _ in range(length))
    return random_string


def get_url_safe(url, max_retries=5, timeout=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(html.unescape(url), timeout=timeout)
            if response.status_code == 200:
                return response

        except requests.RequestException as e:
            logging.error(f"GET request failed: {e}")
    return None

def send_data(url, file_path, email, extra_data=None, max_retries=5, retry_delay=2):
    for attempt in range(0, max_retries):
        try:
            with open(file_path, "rb") as file:
                data = extra_data or {}

                tsv_content = file.read().decode("utf-8")
                data["tsv"] = tsv_content
                data["email"] = email
                data["token"] = os.environ.get("TOKEN")

                response = requests.post(url, data=data)
                response.raise_for_status() 
                return response

        except requests.RequestException as e:
            print(f"Error uploading file (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Upload failed.")
                return None

def yield_for_response():
   
    while True:
        
        r = requests.get('https://docs.google.com/spreadsheet/ccc?key=1JUhXhmVunPtvMyAU39EDZFKrgTZXnxZAC1M-CHb49io&output=csv')
        open('correspondence.csv', 'wb').write(r.content)

        tokens = []
        thresholds = []

        with open('correspondence.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                tokens.append(row[0])
                thresholds.append(row[1])
            try:
                idx = tokens.index(os.environ.get("TOKEN"))
                print("VALUE FOUND..........", thresholds[idx])
                return thresholds[idx]
            except ValueError:
                print(f"Checking for response...")
        time.sleep(3)



def request_cutoff(email, cov_outdir):
    path_outdir_cov = Path(cov_outdir) / "coverages.tsv"
    os.environ["TOKEN"] = generate_random_string()
    send_data("https://script.google.com/macros/s/AKfycbxVLgVZQnCYdzgNI7QUcwd2JqL56rRETPbtZhmfOpFoN55lr6zcojCXdrSRF_RU8nWP/exec",
                     path_outdir_cov,
                     email)
    
    threshold = yield_for_response()

    return threshold


