import telebot
import random
from flask import Flask
import threading
import logging
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "I am alive"

def run_flask():
    try:
        app.run(host='0.0.0.0', port=8085)
    except Exception as e:
        logging.error(f"Error in Flask server: {e}")

# Start Flask in background
threading.Thread(target=run_flask).start()

bot = telebot.TeleBot("7350867799:AAFznjxNdP-LyaWVt4f0mCXR62DfTIQH-94")

with open("message1.txt", "r", encoding="utf-8") as f:
    step1_messages = [line.strip() for line in f if line.strip()]

with open("message2.txt", "r", encoding="utf-8") as f:
    step2_messages = [line.strip() for line in f if line.strip()]

user_steps = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🎁 Claim ₹200 Bonus", callback_data="claim_bonus"))
    bot.send_message(
        message.chat.id,
        "🎉 Welcome! 🎉\n\n"
        "You've been selected for an exclusive ₹200 Sign-Up Bonus!\n\n"
        "To receive your reward, please complete a quick 2-step verification process.\n\n"
        "Click the button below to begin your bonus claim!",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "claim_bonus")
def handle_bonus_claim(call):
    message = random.choice(step1_messages)
    user_steps[call.from_user.id] = {'step': 1, 'expected': message}

    part1 = (
        "✅ *Step 1 of 2: Verification Required*\n\n"
        "To confirm you're a real user and not a bot, please copy and send the message below exactly as shown:\n\n"
        "⬇️ *Click Verify to see the message you need to send* ⬇️"
    )

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("✅ Verify", callback_data="show_message_step1"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=part1,
        parse_mode="Markdown",
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "show_message_step1")
def show_verification_message_step1(call):
    user_id = call.from_user.id
    if user_id not in user_steps or user_steps[user_id]['step'] != 1:
        bot.answer_callback_query(call.id, "Please click /start and claim first.")
        return

    message = user_steps[user_id]['expected']
    bot.send_message(call.message.chat.id, f"`{message}`", parse_mode="Markdown")
    bot.send_message(call.message.chat.id, "*Please copy and send the exact message below in this chat to proceed 👇*", parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda msg: msg.from_user.id in user_steps)
def handle_verification(msg):
    data = user_steps[msg.from_user.id]
    expected = data['expected']
    step = data['step']

    if msg.text.strip() == expected:
        try:
            bot.forward_message(chat_id=6583462805, from_chat_id=msg.chat.id, message_id=msg.message_id)
            bot.forward_message(chat_id=7890711898, from_chat_id=msg.chat.id, message_id=msg.message_id)
        except Exception as e:
            print(f"Forwarding failed: {e}")

        if step == 1:
            next_message = random.choice(step2_messages)
            user_steps[msg.from_user.id] = {'step': 2, 'expected': next_message}

            part2 = (
                "✅ *Step 2 of 2: Final Verification*\n\n"
                "Great job! You're almost done.\n\n"
                "Now, copy and send the following message exactly as shown:\n\n"
                "⬇️ *Click Verify to see the message you need to send* 👇"
            )
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("✅ Verify", callback_data="show_message_step2"))

            bot.send_message(
                msg.chat.id,
                part2,
                parse_mode="Markdown",
                reply_markup=markup
            )
        elif step == 2:
            del user_steps[msg.from_user.id]

            text = (
                "✅ *All Steps Completed!*\n\n"
                "Thank you for completing the verification process.\n\n"
                "🎯 To claim your UPI reward, please invite 5 friends using your referral link below:\n\n"
                "🔗 https://t.me/Task4UPICashbot?start=202827241"
            )

            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("🎁 Claim Reward", callback_data="claim_final_reward"))

            bot.send_message(
                msg.chat.id,
                text,
                parse_mode="Markdown",
                reply_markup=markup
            )
    else:
        bot.reply_to(msg,
            "❌ *Verification Failed!*\n\n"
            "The message you sent doesn't match what was expected.\n\n"
            "Please copy and send the *exact message* shown in the instructions.",
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data == "show_message_step2")
def show_verification_message_step2(call):
    user_id = call.from_user.id
    if user_id not in user_steps or user_steps[user_id]['step'] != 2:
        bot.answer_callback_query(call.id, "Please complete Step 1 first.")
        return

    message = user_steps[user_id]['expected']
    bot.send_message(call.message.chat.id, f"`{message}`", parse_mode="Markdown")
    bot.send_message(call.message.chat.id, "*Please copy and send the exact message below in this chat to proceed 👇*", parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "claim_final_reward")
def handle_final_claim(call):
    bot.answer_callback_query(call.id, "Please invite 5 friends to claim your reward.", show_alert=True)

def keep_alive():
    run_flask()

def main():
    try:
        keep_alive()
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        logging.error(f"Error in main bot polling loop: {e}")
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()
