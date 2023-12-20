import json
import datetime
import telebot
import os
from dotenv import load_dotenv

load_dotenv()

JSON_FILE = "./data.json"
# Replace 'YOUR_BOT_TOKEN' with the actual token provided by BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN")


def add_data_to_transaction(user_id, comment, amount, is_debit, timestamp):
    try:
        file_data = {}
        with open(JSON_FILE, "r") as json_file:
            try:
                file_data = json.load(json_file)
            except Exception as e:
                print("Data is corrupted")
                with open("_backup.json", "w") as backup_file:
                    backup_file.write(str(json_file.readlines()))
        with open(JSON_FILE, "w") as json_file:
            try:
                if user_id in file_data.keys():
                    file_data[user_id].append(
                        {
                            "date": str(timestamp),
                            "type": "debited" if is_debit else "credited",
                            "comment": comment,
                            "amount": amount,
                        }
                    )
                else:
                    file_data[user_id] = []
                    file_data[user_id].append(
                        {
                            "date": str(timestamp),
                            "type": "debited" if is_debit else "credited",
                            "comment": comment,
                            "amount": amount,
                        }
                    )
                json.dump(file_data, json_file)
                return True
            except Exception as e:
                print("Error while adding transaction:", e)
                return False
    except Exception as e:
        print("Error:", e)
        return False


def delete_last_transaction(user_id):
    try:
        file_data = {}
        with open(JSON_FILE, "r") as json_file:
            file_data = json.load(json_file)
        if user_id in file_data.keys() and len(file_data[user_id]) != 0:
            with open(JSON_FILE, "w") as json_file:
                data = file_data[user_id].pop()
                json.dump(file_data, json_file)
                return True, data, "Success"
        else:
            return False, None, "No transactions to delete"
    except Exception as e:
        print("Error:", e)
        return False, None, "Failed to delete last transaction"


def check_valid_message(message):
    try:
        data = message.strip().split(" ")
        n = len(data)
        formatted_data = dict()
        if len(data) > 1:
            is_credit = data[n - 1]
            if is_credit == "+":
                formatted_data["amount"] = int(data[n - 2])
                formatted_data["comment"] = " ".join(data[: n - 2])
                formatted_data["is_debit"] = False
                return True, formatted_data
            else:
                formatted_data["amount"] = int(data[n - 1])
                formatted_data["comment"] = " ".join(data[: n - 1])
                formatted_data["is_debit"] = True
                return True, formatted_data
        else:
            return False, None
    except Exception as e:
        print("Data not in rigt format:", e)
        return False, None


def get_user_auth(message):
    from_user = message.json["from"]
    from_chat = message.json["chat"]
    if message.content_type != "text":
        return False, "We support only text messages"
    if from_user["is_bot"] == True:
        return False, "We do not support bot messages"
    elif from_user["id"] != from_chat["id"]:
        return False, "We do not support group messages"
    else:
        return True, str(from_user["id"])


def get_transaction_history(user_id, count=50):
    file_data = {}
    with open(JSON_FILE, "r") as json_file:
        file_data = json.load(json_file)
    if user_id in file_data and len(file_data[user_id]):
        n = len(file_data[user_id])
        if n > count:
            return True, file_data[user_id][n - count :], "Success"
        else:
            return True, file_data[user_id], "Success"
    else:
        return False, None, "No transaction history available!"


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_status, user_message = get_user_auth(message)
    if user_status == False:
        bot.reply_to(message, user_message)
    else:
        bot.reply_to(message, "Welcome to Expense Manager!\n")


@bot.message_handler(commands=["help"])
def send_welcome(message):
    user_status, user_message = get_user_auth(message)
    if user_status == False:
        bot.reply_to(message, user_message)
    else:
        bot.reply_to(
            message,
            "To add transactions follow following examples:\nDebit ->  Lunch 500\nCredit ->  Salary 5000 +\n\nContact iamgmbhat@gmail.com for further help",
        )


@bot.message_handler(commands=["history"])
def send_welcome(message):
    user_status, user_message = get_user_auth(message)
    if user_status == False:
        bot.reply_to(message, user_message)
    else:
        status, history, reply = get_transaction_history(user_message)
        if status == False:
            bot.reply_to(message, reply)
        else:
            trasaction_history = ""
            for i in history:
                trasaction_history += (
                    f"{i['type'].title()}\n\nDate: {i['date'].split(' ')[0]}\nAmount: {i['amount']}\nComment: {i['comment']}"
                    + "\n"
                    + "-" * 30
                    + "\n\n"
                )
            bot.reply_to(message, trasaction_history)


@bot.message_handler(commands=["remove"])
def cancel_last_transaction(message):
    user_status, user_message = get_user_auth(message)
    if user_status == False:
        bot.reply_to(message, user_message)
    else:
        status, data, reply = delete_last_transaction(user_message)
        if status == True:
            bot.reply_to(
                message,
                f"Your last transaction of Rs. {data['amount']} for '{data['comment']}' on {data['date'].split(' ')[0]} has been deleted",
            )
        else:
            bot.reply_to(
                message,
                reply,
            )


@bot.message_handler(func=lambda msg: True)
def add_transaction(message):
    user_status, user_message = get_user_auth(message)
    if user_status == False:
        bot.reply_to(message, user_message)
    else:
        status, data = check_valid_message(message.text)
        if status == True:
            comment = data["comment"]
            amount = data["amount"]
            is_debit = data["is_debit"]
            timestamp = datetime.datetime.fromtimestamp(message.date)
            status = add_data_to_transaction(
                user_message, comment, amount, is_debit, timestamp
            )
            if status == True:
                bot.reply_to(
                    message,
                    "Transaction added successfully",
                )
            else:
                bot.reply_to(
                    message,
                    "Failed to add transaction!",
                )
        else:
            bot.reply_to(
                message,
                "Message not in right format!\n\nFollow following examples:\nDebit ->  Lunch 500\nCredit ->  Salary 5000 +",
            )


bot.infinity_polling()
