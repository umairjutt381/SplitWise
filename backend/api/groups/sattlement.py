import json
from decimal import Decimal
from collections import defaultdict
from backend.utils.db_conn import conn


def get_db_conn():
    return conn

def get_username(user_id):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()
    cursor.execute("SELECT username FROM Users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    return result[0]

def expense_settlement(expenses, user_id):
    balances = defaultdict(Decimal)
    for expense in expenses:
        total_amount = Decimal(expense['amount'])
        split_users = json.loads(expense['split_on'])
        paid_by = json.loads(expense['paid_by'])
        split_count = len(split_users)
        split_amount = (total_amount / split_count)

        for splitter_id in split_users:
            for payer_id in paid_by:
                if splitter_id == user_id:
                    continue
                if splitter_id == user_id:
                    balances[payer_id] += split_amount
                if payer_id == user_id:
                    balances[splitter_id] -= split_amount

    response = {
        "You will get": [],
        "You pay back": []
    }
    for uid, amount in balances.items():
        if amount == 0:
            continue
        if amount > 0:
            response["You will get"].append({
                "to_user": get_username(uid),
                "amount": amount
            })
        else:
            response["You pay back"].append({
                "to_user": get_username(uid),
                "amount": amount
            })
    return response
