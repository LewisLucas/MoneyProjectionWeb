import requests
import json
from datetime import datetime as dt
from datetime import timedelta
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
token_path = os.path.join(script_dir, 'token.txt')
transactions_path = os.path.join(script_dir, 'transactions.json')

with open(token_path, 'r') as file:
    api_token = file.read().strip()

def push(title, body):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {
        "Access-Token": api_token,
        "Content-Type": "application/json"
    }
    data = {
        "type": "note",
        "title": title,
        "body": body
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

due_today = []
due_tomorrow = []
incoming = ["ESA", "PIP", "Walsall Council"]
today = dt.now()
tomorrow = today + timedelta(days=1)
marked_for_removal = []
with open(transactions_path, 'r') as file:
    transactions = json.load(file)

for transaction in transactions["transactions"]:
    name = transaction["name"]
    amount = transaction["amount"]
    date = transaction["date"]
    if dt.strptime(date, "%d-%m-%Y").date() == today.date():
        if name not in incoming:
            due_today.append(f"£{amount} due today for {name}")
        else:
            due_today.append(f"£{amount} incoming today for {name}")
        # Remove the transaction from the list if due today
        marked_for_removal.append(transaction)
      
for transaction in transactions["transactions"]:
    name = transaction["name"]
    amount = transaction["amount"]
    date = transaction["date"]
    if dt.strptime(date, "%d-%m-%Y").date() == tomorrow.date():
        if name not in incoming: 
            due_tomorrow.append(f"£{amount} due tomorrow for {name}")
        else:
            due_tomorrow.append(f"£{amount} incoming tomorrow for {name}")

if due_today:
    message = "\n".join(due_today)
    push(f"{len(due_today)} Transactions Today", message)

if due_tomorrow:
    message = "\n".join(due_tomorrow)
    push(f"{len(due_tomorrow)} Transactions Tomorrow", message)

file.close()
# Remove transactions that were due today
for item in marked_for_removal:
    transactions["transactions"].remove(item)
with open(transactions_path, 'w') as file:
    json.dump(transactions, file, indent=4)
file.close()
