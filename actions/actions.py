import pymysql
import re
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List


def db_connect():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="password",
        database="bank",
        port=3306
    )

def extract_amount(text: Text) -> float:
    
    match = re.search(r'\b\d+(?:\.\d{1,2})?\b', text)
    if match:
        return float(match.group(0))
    return None

class ActionCheckBalance(Action):
    def name(self) -> Text:
        return "action_check_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE name='John Doe'")
        result = cursor.fetchone()
        balance = result[0] if result else "Account not found"
        connection.close()
        
        dispatcher.utter_message(text=f"Your balance is {balance} dollars.")
        return []

class ActionAddMoney(Action):
    def name(self) -> Text:
        return "action_add_money"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        amount = tracker.get_slot("amount")
        if not amount:
            amount = extract_amount(tracker.latest_message.get('text'))
            if not amount:
                dispatcher.utter_message(text="Please specify an amount.")
                return []

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE name='John Doe'", (amount,))
        connection.commit()
        connection.close()
        
        dispatcher.utter_message(text=f"Added {amount} dollars to your account.")
        return []

class ActionRemoveMoney(Action):
    def name(self) -> Text:
        return "action_remove_money"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        amount = tracker.get_slot("amount")
        if not amount:
            amount = extract_amount(tracker.latest_message.get('text'))
            if not amount:
                dispatcher.utter_message(text="Please specify an amount.")
                return []

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE name='John Doe'", (amount,))
        connection.commit()
        connection.close()
        
        dispatcher.utter_message(text=f"Removed {amount} dollars from your account.")
        return []
