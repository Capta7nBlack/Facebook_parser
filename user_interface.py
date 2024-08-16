from engine.VecDB_STF.config import Config
from telebot import TeleBot, types
from engine.VecDB_STF import VDB
import sqlite3


# Replace with your actual Telegram bot API token
BOT_TOKEN = ''
db_path = './database.sql'
vdb = VDB(Config)
vdb.load()
bot = TeleBot(BOT_TOKEN)


# Define a function for intializing a database
def init_db():
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	table_name = 'input'
	sql_create_table = f"""
	CREATE TABLE IF NOT EXISTS {table_name} (
	  id INTEGER PRIMARY KEY AUTOINCREMENT,
	  group_links TEXT
	);
	"""

	cursor.execute(sql_create_table)
	conn.commit()
	conn.close()


# Generate main menu
def main_keyboard():
	keyboard = types.ReplyKeyboardMarkup()
	list_button = types.KeyboardButton('/эталоны')
	save_button = types.KeyboardButton('/сохранить эталон')
	facebook_button = types.KeyboardButton('/Facebook ссылки')
	add_link_button = types.KeyboardButton('/добавить ссылку')
	change_threshold = types.KeyboardButton('/изменить трэшхолд')

	keyboard.add(list_button)
	keyboard.add(save_button)
	keyboard.add(facebook_button)
	keyboard.add(add_link_button)
	keyboard.add(change_threshold)

	return keyboard


# Function to format a saved message with a removal button
def format_saved_message(message_id, message_text):
	keyboard = types.InlineKeyboardMarkup()
	remove_button = types.InlineKeyboardButton(text='Remove', callback_data=f'remove_{message_id}')
	keyboard.add(remove_button)
	return f'{message_text}\n', keyboard


# Function to format a saved Facebook link with a removal button
def format_fackebook_link_message(message_id, message_text):
	keyboard = types.InlineKeyboardMarkup()
	remove_button = types.InlineKeyboardButton(text='Remove', callback_data=f'facebookremove_{message_id}')
	keyboard.add(remove_button)
	return f'{message_text}\n', keyboard


# Function to handle the '/эталоны' command
@bot.message_handler(commands=['start', 'help'])
def start_message(message):
	bot.send_message(message.chat.id, 'Используйте команды в меню', reply_markup=main_keyboard())


# Function to handle the '/список' command
@bot.message_handler(commands=['эталоны'])
def list_saved_messages(message):
	chat_id = message.chat.id

	if len(vdb.vocab_nontranslated) == 0:
		bot.send_message(chat_id, 'Эталонов не найдено.')
		return

	for message_id, message_text in enumerate(vdb.vocab_nontranslated):
		formatted_message, keyboard = format_saved_message(message_id, message_text)
		bot.send_message(chat_id, formatted_message, reply_markup=keyboard)


# Function to handle the '/Facebook ссылки' command
@bot.message_handler(commands=['Facebook'])
def list_facebook_links_messages(message):
	chat_id = message.chat.id

	conn = sqlite3.connect(db_path)
	cur = conn.cursor()

	cur.execute('SELECT id, group_links FROM input')
	data = cur.fetchall()

	conn.close()

	if len(data) == 0:
		bot.send_message(chat_id, 'Ссылок не найдено.')
		return

	for message_id, message_text in data:
		formatted_message, keyboard = format_fackebook_link_message(message_id, message_text)
		bot.send_message(chat_id, formatted_message, reply_markup=keyboard)


# Function to handle the '/сохранить' command
@bot.message_handler(commands=['сохранить'])
def save_message(message):
	message = bot.send_message(message.chat.id, 'Введите новый эталон.')
	bot.register_next_step_handler(message, save_message_handler)


def save_message_handler(message):
	message_text = message.text
	chat_id = message.chat.id

	vdb.add(message_text)
	vdb.save()
	vdb.load()

	bot.send_message(chat_id, 'Эталон был успешно сохранен!')


# Function to handle the '/изменить трэшхолд'
@bot.message_handler(commands=['изменить'])
def change_threshold_level(message):
	message = bot.send_message(message.chat.id, 'Введите новое значение (только число, пример "0.1" в диапозоне от 0 до 1).')
	bot.register_next_step_handler(message, change_threshold_level_handler)


def change_threshold_level_handler(message):
	message_text = message.text
	chat_id = message.chat.id

	with open('level.txt', 'w') as file:
		file.write(message_text)

	bot.send_message(chat_id, 'Значение было изменено.')


# Function to handle the '/добавить ссылку'
@bot.message_handler(commands=['добавить'])
def add_link_message(message):
	message = bot.send_message(message.chat.id, 'Введите новую ссылку.')
	bot.register_next_step_handler(message, add_link_message_handler)


def add_link_message_handler(message):
	message_text = message.text
	chat_id = message.chat.id

	conn = sqlite3.connect(db_path)
	cur = conn.cursor()

	cur.execute('INSERT INTO input(group_links) VALUES(?)', (message.text,))
	conn.commit()
	conn.close()

	bot.send_message(chat_id, 'Ссылка была добавлена.')


# Function to handle inline button callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith('remove_'))
def remove_saved_message(call):
	chat_id = call.message.chat.id
	message_id = int(' '.join(call.data.split('_')[1:]))

	# logic of removing messages
	vdb.remove(message_id)
	vdb.reset_index()
	vdb.save()
	vdb.load()
	
	bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text='Эталон удален.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('facebookremove_'))
def remove_facebook_link(call):
	chat_id = call.message.chat.id
	message_id = ' '.join(call.data.split('_')[1:])

	conn = sqlite3.connect(db_path)
	cur = conn.cursor()

	cur.execute('DELETE FROM input WHERE id = ?', (int(message_id),))
	conn.commit()
	conn.close()
	
	bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text='Ссылка удалена.')


# Handle all other messages
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
	bot.send_message(message.chat.id, 'Неизвестная команда. Используйте команды в меню')


if __name__ == '__main__':
	bot.infinity_polling()
