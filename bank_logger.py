import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bank_data.json")
DEFAULT_INVESTMENT = 10.0
INVEST_TYPES = ["Gold", "SIP", "Stocks", "Other"]

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "balances": {"savings": 0.0, "pocket_money": 0.0},
        "transactions": [],
        "investments": [],
        "next_investment_id": 1,
    }


def save(data):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)  # never leaves a half-written file

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def pretty(name):
    return name.replace("_", " ").title()

def total(data):
    return round(sum(data["balances"].values()), 2)

def ask_amount(prompt, default=None):
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            value = round(float(raw), 2)
            if value < 0:
                print("  Enter a positive number.")
                continue
            return value
        except ValueError:
            print("  Enter a valid number.")

def ask_bucket(prompt="Bucket (s = savings, p = pocket money): "):
    while True:
        choice = input(prompt).strip().lower()
        if choice == "s":
            return "savings"
        if choice == "p":
            return "pocket_money"
        print("  Type s or p.")

def ask_invest_type(current=None):
    for i, t in enumerate(INVEST_TYPES, 1):
        print(f"  {i}. {t}")
    suffix = f" [Enter = keep {current}]" if current else ""
    while True:
        raw = input(f"Invested in{suffix}: ").strip()
        if raw == "" and current:
            return current
        if raw.isdigit() and 1 <= int(raw) <= len(INVEST_TYPES):
            chosen = INVEST_TYPES[int(raw) - 1]
        elif raw:
            matches = [t for t in INVEST_TYPES if t.lower() == raw.lower()]
            chosen = matches[0] if matches else raw.title()  # custom, e.g. "Mutual Fund"
        else:
            continue
        if chosen == "Other":
            chosen = input("  Type what it was: ").strip().title() or "Other"
        return chosen

def find_investment(data):
    show_investments(data)
    if not data["investments"]:
        return None
    raw = input("Investment ID: ").strip()
    if raw.isdigit():
        for inv in data["investments"]:
            if inv["id"] == int(raw):
                return inv
    print("  No investment with that ID.")
    return None


def add_transaction(data):
    bucket = ask_bucket()
    kind = ""
    while kind not in ("in", "out"):
        kind = input("Money in or out? (in/out): ").strip().lower()
    amount = ask_amount("Amount (Rs): ")
    note = input("Message (what was it for / who from): ").strip()

    if kind == "out" and amount > data["balances"][bucket]:
        print(f"  That's more than your {pretty(bucket)} balance.")
        if input("  Continue anyway? (y/n): ").strip().lower() != "y":
            return
    delta = amount if kind == "in" else -amount
    data["balances"][bucket] = round(data["balances"][bucket] + delta, 2)
    data["transactions"].append(
        {"time": now(), "type": kind, "bucket": bucket, "amount": amount, "note": note}
    )
    save(data)
    print(f"  Saved. {pretty(bucket)} is now Rs {data['balances'][bucket]:.2f}")


def transfer(data):
    print("Move money from pocket money to savings.")
    amount = ask_amount("Amount (Rs): ")
    if amount > data["balances"]["pocket_money"]:
        print("  Not enough pocket money for that.")
        return
    note = input("Message (optional): ").strip()
    data["balances"]["pocket_money"] = round(data["balances"]["pocket_money"] - amount, 2)
    data["balances"]["savings"] = round(data["balances"]["savings"] + amount, 2)
    data["transactions"].append(
        {"time": now(), "type": "transfer", "bucket": "pocket_money -> savings",
         "amount": amount, "note": note or "Pocket money moved to savings"}
    )
    save(data)
    print("  Done. Your total is unchanged.")


def edit_balance(data):
    bucket = ask_bucket("Which balance to edit? (s = savings, p = pocket money): ")
    old = data["balances"][bucket]
    print(f"  Current {pretty(bucket)}: Rs {old:.2f}")
    new = ask_amount("New balance (Rs): ")
    reason = input("Reason (optional): ").strip()
    data["balances"][bucket] = new
    data["transactions"].append(
        {"time": now(), "type": "adjustment", "bucket": bucket,
         "amount": round(new - old, 2),
         "note": reason or f"Balance edited from {old:.2f} to {new:.2f}"}
    )
    save(data)
    print(f"  {pretty(bucket)} is now Rs {new:.2f}")

def log_investment(data):
    amount = ask_amount(f"Amount (Rs) [Enter = {DEFAULT_INVESTMENT:g}]: ", DEFAULT_INVESTMENT)
    itype = ask_invest_type()
    note = input("Note (optional): ").strip()
    if amount > data["balances"]["pocket_money"]:
        print("  Heads up: this is more than your pocket money balance.")
        if input("  Continue anyway? (y/n): ").strip().lower() != "y":
            return
    data["balances"]["pocket_money"] = round(data["balances"]["pocket_money"] - amount, 2)
    data["investments"].append(
        {"id": data["next_investment_id"], "time": now(), "amount": amount,
         "type": itype, "note": note}
    )
    data["next_investment_id"] += 1
    save(data)
    print(f"  Logged. Pocket money is now Rs {data['balances']['pocket_money']:.2f}")


def edit_investment(data):
    inv = find_investment(data)
    if not inv:
        return
    print("Press Enter to keep a value.")
    new_amount = ask_amount(f"Amount (Rs) [{inv['amount']:.2f}]: ", inv["amount"])
    inv["type"] = ask_invest_type(inv["type"])
    note = input(f"Note [{inv['note']}]: ").strip()
    if note:
        inv["note"] = note
    diff = round(new_amount - inv["amount"], 2)
    data["balances"]["pocket_money"] = round(data["balances"]["pocket_money"] - diff, 2)
    inv["amount"] = new_amount
    save(data)
    print(f"  Updated. Pocket money is now Rs {data['balances']['pocket_money']:.2f}")


def delete_investment(data):
    inv = find_investment(data)
    if not inv:
        return
    if input("Delete it and refund pocket money? (y/n): ").strip().lower() != "y":
        return
    data["balances"]["pocket_money"] = round(data["balances"]["pocket_money"] + inv["amount"], 2)
    data["investments"].remove(inv)
    save(data)
    print(f"  Deleted. Pocket money is now Rs {data['balances']['pocket_money']:.2f}")


def show_balances(data):
    print("\n--- Balances ---")
    print(f"  Savings      : Rs {data['balances']['savings']:.2f}")
    print(f"  Pocket money : Rs {data['balances']['pocket_money']:.2f}")
    print(f"  TOTAL        : Rs {total(data):.2f}")


def show_transactions(data):
    print("\n--- Transactions (latest 20) ---")
    if not data["transactions"]:
        print("  Nothing logged yet.")
        return
    for t in data["transactions"][-20:]:
        sign = {"in": "+", "out": "-"}.get(t["type"], "~")
        print(f"  {t['time']} | {sign}Rs {t['amount']:.2f} | {pretty(t['bucket'])} | {t['note']}")


def show_investments(data):
    print("\n--- Investments (latest 20) ---")
    if not data["investments"]:
        print("  Nothing logged yet.")
        return
    for i in data["investments"][-20:]:
        print(f"  #{i['id']} | {i['time']} | Rs {i['amount']:.2f} | {i['type']} | {i['note']}")
    print("  By type:")
    by_type = {}
    for i in data["investments"]:
        by_type[i["type"]] = by_type.get(i["type"], 0) + i["amount"]
    for t, amt in by_type.items():
        print(f"    {t}: Rs {amt:.2f}")
    print(f"  Total invested: Rs {sum(i['amount'] for i in data['investments']):.2f}")


MENU = """
===== Bank Logger =====
1. Add transaction (in/out)
2. Move pocket money -> savings
3. Log investment (from pocket money)
4. View balances & total
5. View transactions
6. View investments
7. Edit savings / pocket money balance
8. Edit an investment
9. Delete an investment
0. Quit
"""

ACTIONS = {
    "1": add_transaction, "2": transfer, "3": log_investment,
    "4": show_balances, "5": show_transactions, "6": show_investments,
    "7": edit_balance, "8": edit_investment, "9": delete_investment,
}


def main():
    data = load()
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Bye!")
            break
        action = ACTIONS.get(choice)
        if action:
            action(data)
        else:
            print("  Pick a number from the menu.")


if __name__ == "__main__":
    main()
