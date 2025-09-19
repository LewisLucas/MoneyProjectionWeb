import argparse
import datetime
from dateutil import relativedelta
from datetime import datetime as dt
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

def arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--money", "-m", help = "Current amount of money", required=True, type=float)
    parser.add_argument("--days", "-d", default=50, help="Number of days to project (default: 50)", type=int)
    parser.add_argument("--file", "-f", help = "File path of json file", required=True, type=str)
    return parser.parse_args()

args = arguments()
current_money = args.money
number_of_days = args.days
curret_date = datetime.date.today() + datetime.timedelta(days=1)
date_list = [curret_date + datetime.timedelta(days=i) for i in range(number_of_days)]
with open(args.file, "r") as file:
    schedule = json.load(file)  

class Calendar:
    def __str__(self):
        return f"Calendar with {len(self.days)} days"

    def __init__(self):
        self.days = [Day(date=d) for d in date_list]
        self.endate = self.days[-1].date
    
    def subtract_money_from_days_from(self, money, dates, transaction):
        """ Loop through a list of dates and subtract money from that date"""
        active = False
        mult = 0
        for d in self.days:
            if d.date in dates:
                active = True
                mult += 1
                d.transactions.append(f"-{transaction['name']}:£{money},")
            if active:
                d.money -= money * mult

    def add_money_to_days_from(self, money, dates, transaction):
        """ Loop through a list of dates and add money to that date"""
        active = False
        mult = 0
        for d in self.days:
            if d.date in dates:
                active = True
                mult += 1
                d.transactions.append(f"+{transaction['name']}:£{money},")
            if active:
                d.money += money * mult

    def list_days(self):
        """ Print all days. """
        for d in self.days:
            print(d)

    def get_list_of_dates(self, frequency, start_date):
        """ Returns a list of dates starting from start_date and then everyday with an interval of frequency etc. 7 days. """
        today = datetime.date.today()
        working_date = start_date
        list_of_dates = []
        while working_date <= self.endate:
            if working_date >= today:
                list_of_dates.append(working_date)
            working_date += relativedelta.relativedelta(days=frequency)
        return list_of_dates
    
    def get_list_of_dates_monthly(self, start_date):
        """ Returns a list of dates starting from start_date and then everyday with an interval 1 month. """
        today = datetime.date.today()
        working_date = start_date
        list_of_dates = []
        while working_date <= self.endate:
            if working_date >= today:
                list_of_dates.append(working_date)
            working_date += relativedelta.relativedelta(months=1)
        return list_of_dates
    
    def calculate_schedule_transactions(self):
        daily_in = [i for i in schedule["daily"]["in"].values()]
        daily_out = [i for i in schedule["daily"]["out"].values()]
        weekly_in = [i for i in schedule["weekly"]["in"].values()]
        weekly_out = [i for i in schedule["weekly"]["out"].values()]
        biweekly_in = [i for i in schedule["biweekly"]["in"].values()]
        biweekly_out = [i for i in schedule["biweekly"]["out"].values()]
        quadweekly_in = [i for i in schedule["quadweekly"]["in"].values()]
        quadweekly_out = [i for i in schedule["quadweekly"]["out"].values()]
        monthly_in = [i for i in schedule["monthly"]["in"].values()]
        monthly_out = [i for i in schedule["monthly"]["out"].values()]
        if daily_in:
            for i in daily_in:
                self.add_money_to_days_from(i["amount"], self.get_list_of_dates(1, dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if daily_out:
            for i in daily_out:
                self.subtract_money_from_days_from(i["amount"], self.get_list_of_dates(1, dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if weekly_in:
            for i in weekly_in:
                self.add_money_to_days_from(i["amount"], self.get_list_of_dates(7, dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if weekly_out:
            for i in weekly_out:
                self.subtract_money_from_days_from(i["amount"], self.get_list_of_dates(7, dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if biweekly_in:
            for i in biweekly_in:
                self.add_money_to_days_from(i["amount"], self.get_list_of_dates(14, dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if biweekly_out:
            for i in biweekly_out:
                self.subtract_money_from_days_from(i["amount"], self.get_list_of_dates(14, dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if quadweekly_in:
            for i in quadweekly_in:
                self.add_money_to_days_from(i["amount"], self.get_list_of_dates(28, dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if quadweekly_out:
            for i in quadweekly_out:
                self.subtract_money_from_days_from(i["amount"], self.get_list_of_dates(28, dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if monthly_in:
            for i in monthly_in:
                self.add_money_to_days_from(i["amount"], self.get_list_of_dates_monthly(dt.strptime(i["date"], "%d-%m-%Y").date()), i)
        if monthly_out:
            for i in monthly_out:
                self.subtract_money_from_days_from(i["amount"], self.get_list_of_dates_monthly(dt.strptime(i["date"], "%d-%m-%Y").date()), i)
    
    def create_transaction_list(self):
        days_with_transactions =  [d for d in self.days if d.transactions]
        filtered_days = []
        for d in days_with_transactions:
            if len(d.transactions) == 1:
                continue
            filtered_days.append(d)

        # Clear previous transactions file
        if os.path.exists('media/transactions.txt'):
            os.remove('media/transactions.txt')
        # Write transactions to files
        transactions_json = {"transactions": [

        ]}
        with open('media/transactions.txt', 'w') as f:
            for d in filtered_days:
                string = str(d)
                string = string.replace(" -daily overdraft:£1.5,", "")
                f.write(string + '\n')
        with open('push_notifier/transactions.json', 'w') as f:
            for d in filtered_days:
                for t in d.transactions:
                    t = t.replace(",", "")
                    name = t.split(":")[0].replace("+", "").replace("-", "")
                    amount = float(t.split(":")[1].replace("£", ""))
                    date = d.date.strftime("%d-%m-%Y")
                    if name == "daily overdraft":
                        continue
                    transactions_json["transactions"].append({
                        "name": name,
                        "amount": amount,
                        "date": date
                    })
            json.dump(transactions_json, f, indent=4)

class Day:
    def __str__(self):
        if self.money < 0:
            string = f"{self.date.strftime('%a %d of %b %Y')} has a deficit of £{round(-self.money, 2)}"
            if self.transactions:
                string += f"| Transactions:"
            for transaction in self.transactions:
                string += f" {transaction}"
            return string
        else:
            string = f"{self.date.strftime('%a %d of %b %Y')} has £{round(self.money, 2)}"
            if self.transactions:
                string += f"| Transactions:"
            for transaction in self.transactions:
                string += f" {transaction}"
            return string

    def __init__(self, date=None, money=current_money):
        self.date = date
        self.money = money
        self.transactions = []


calendar = Calendar()
calendar.calculate_schedule_transactions()
calendar.create_transaction_list()

# Delete the json file after processing
if os.path.exists(args.file):
    os.remove(args.file)

dates = [d.date for d in calendar.days]
money = [d.money for d in calendar.days]

plt.plot(dates, money, marker='.', linewidth=0.6, markersize=2)
plt.title(f'Money Projection Over {number_of_days} Days')
plt.xlabel('Date')
plt.ylabel('Money (£)')

# Format x-axis as DD-MM-YYYY but keep dates as date objects
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d %b%y'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

plt.xticks(rotation=90)
plt.grid()
plt.tight_layout()
plt.axhline(y=0, color='r', linestyle='--', label='Zero Line')
plt.legend()
plt.fill_between(dates, money, where=(np.array(money) < 0),
                 color='red', alpha=0.3, label='Deficit Area')
plt.fill_between(dates, money, where=(np.array(money) >= 0),
                 color='green', alpha=0.3, label='Surplus Area')
plt.savefig('images/output_image.png', dpi=300)

