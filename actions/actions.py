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
        database="bank"
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
        name = tracker.get_slot("name")
        if not name:
            dispatcher.utter_message(text="Please specify the account name.")
            return []

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE name=%s", (name,))
        result = cursor.fetchone()
        balance = result[0] if result else "Account not found"
        connection.close()
        
        dispatcher.utter_message(text=f"{name}'s balance is {balance} dollars.")
        return []

class ActionAddMoney(Action):
    def name(self) -> Text:
        return "action_add_money"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        amount = tracker.get_slot("amount")
        name = tracker.get_slot("name")
        
        if not amount:
            amount = extract_amount(tracker.latest_message.get('text'))
        if not amount or not name:
            dispatcher.utter_message(text="Please specify an amount and an account name.")
            return []

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE name=%s", (amount, name))
        connection.commit()
        connection.close()
        
        dispatcher.utter_message(text=f"Added {amount} dollars to {name}'s account.")
        return []

class ActionRemoveMoney(Action):
    def name(self) -> Text:
        return "action_remove_money"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        amount = tracker.get_slot("amount")
        name = tracker.get_slot("name")
        
        if not amount:
            amount = extract_amount(tracker.latest_message.get('text'))
        if not amount or not name:
            dispatcher.utter_message(text="Please specify an amount and an account name.")
            return []

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE name=%s", (amount, name))
        connection.commit()
        connection.close()
        
        dispatcher.utter_message(text=f"Removed {amount} dollars from {name}'s account.")
        return []

class ActionTransferFunds(Action):
    def name(self) -> Text:
        return "action_transfer_funds"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        amount = tracker.get_slot("amount")
        recipient = tracker.get_slot("recipient")
        sender = tracker.get_slot("name")
        
        if not amount or not recipient or not sender:
            dispatcher.utter_message(text="Please specify an amount, sender, and recipient.")
            return []

        connection = db_connect()
        cursor = connection.cursor()

        cursor.execute("SELECT balance FROM accounts WHERE name=%s", (recipient,))
        result = cursor.fetchone()
        if not result:
            dispatcher.utter_message(text=f"Recipient {recipient} not found.")
            connection.close()
            return []

       
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE name=%s", (amount, sender))
        
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE name=%s", (amount, recipient))
        connection.commit()
        connection.close()
        
        dispatcher.utter_message(text=f"Transferred {amount} dollars from {sender} to {recipient}.")
        return []

class ActionCreateAccount(Action):
    def name(self) -> Text:
        return "action_create_account"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("name")
        initial_balance = tracker.get_slot("initial_balance")
        
        if not name or not initial_balance:
            dispatcher.utter_message(text="Please provide a name and an initial balance.")
            return []

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", (name, initial_balance))
        connection.commit()
        connection.close()
        
        dispatcher.utter_message(text=f"Account for {name} created with initial balance {initial_balance} dollars.")
        return []

class ActionDeleteAccount(Action):
    def name(self) -> Text:
        return "action_delete_account"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("name")
        
        if not name:
            dispatcher.utter_message(text="Please provide the account name to delete.")
            return []

        connection = db_connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM accounts WHERE name=%s", (name,))
        connection.commit()
        connection.close()
        
        dispatcher.utter_message(text=f"Account for {name} has been deleted.")
        return []

# class ActionListALLAccounts(Action):
#     def name(self) -> Text:
#         return "action_list_all_accounts"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         connection = db_connect()
#         cursor = connection.cursor()
#         cursor.execute("SELECT name FROM accounts")
#         results = cursor.fetchall()
#         connection.close()
        
#         accounts = [result[0] for result in results]
#         accounts_list = ", ".join(accounts) if accounts else "No accounts found"
        
#         dispatcher.utter_message(text=f"The accounts are: {accounts_list}")
#         return []
