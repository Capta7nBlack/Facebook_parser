import sqlite3
import telebot
import time

# Replace with your bot token
BOT_TOKEN = '7200182073:AAFjB48AWqcLZ4Ij_w9IN8JKDy7EUg8b87A'
OWNER_ID = 6162608646
DATABASE = './database.sql'
bot = telebot.TeleBot(BOT_TOKEN)

# Database connection
def get_unchecked_messages():
	conn = sqlite3.connect(DATABASE)
	cursor = conn.cursor()
	cursor.execute("SELECT post_links, post_messages FROM output WHERE to_send = 1")
	messages = cursor.fetchall()
	conn.close()
	return messages

def mark_messages_as_checked():
	conn = sqlite3.connect(DATABASE)
	cursor = conn.cursor()
	cursor.execute("UPDATE output SET to_send = 0 WHERE to_send = 1")
	conn.commit()
	conn.close()

def remove_checked_messages():
	conn = sqlite3.connect(DATABASE)
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM output")
	data = cursor.fetchall()

	if len(data) > 10000:
		cursor.execute("DELETE FROM output")
		conn.commit()

	conn.close()
	

# Sending messages to users
def send_messages():
	messages = get_unchecked_messages()
	mark_messages_as_checked()
	remove_checked_messages()

	for url, content in messages:
		message_text = f"{content}\n\n{url}"
		bot.send_message(OWNER_ID, message_text)


while True:
	send_messages()
	time.sleep(10)

	# time.sleep(300)  # Sleep for 5 minutes
