import requests
import argparse
import sys
url = 'https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_UIeHxhONfKXxP7Iv1rJ06ZDMJ4HBcPHDeBpZu177'
response = requests.get(url)
parser = argparse.ArgumentParser()
parser.add_argument("divident", type=str, help="Description of arg1")
parser.add_argument("divisor", type=str, help="Description of arg2")
args = parser.parse_args()
divident = args.divident
divisor = args.divisor
tmp = ["AUD", "BGN", "BRL", "CAD", "CHF", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HRK", "HUF", "IDR", "ILS", "INR",
       "ISK", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PLN", "RON", "RUB", "SEK", "SGD", "THB", "TRY", "USD", "ZAR"]

if response.status_code == 200:
    data = response.json()["data"]  # If the response contains JSON data
    if divident not in tmp or divisor not in tmp:
        print("False Currency")

    else:
        print(data[divident]/data[divisor])
sys.exit(0)
