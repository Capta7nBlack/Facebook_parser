import sqlite3
from Config import Config
import hashlib
import random

database = Config.database


def db_open():
    conn_func = sqlite3.connect(database)
    curr_func = conn_func.cursor()
    print("The db connection is opened")
    return conn_func, curr_func


def db_close(conn_func, curr_func):
    conn_func.commit()
    curr_func.close()
    conn_func.close()
    print("The db connection is closed")


def hash_generator(message):
    hash_object = hashlib.sha256(message.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    hash_decimal = int(hash_hex, 16)
    hash_value_ready = hash_decimal % (10 ** 8)
    print("The hash value generated")
    return hash_value_ready


def db_insert_with_comparison_post_message(message, post_link):
    hash_value = hash_generator(message)
    conn_func, curr_func = db_open()
    try:
        curr_func.execute('INSERT INTO output'
                          '(hash_values, post_messages, post_links, to_send) VALUES (?, ?, ?, ?)'
                          , (hash_value, message, post_link, 1))
        conn_func.commit()
        print("The post message has been added to db")

    except sqlite3.IntegrityError:
        print("The post message was a duplicate")
    finally:
        curr_func.close()
        conn_func.close()
        print("Post message inserting function completed")


def db_insert_with_comparison_comment_message(message, comment_link):
    hash_value = hash_generator(message)
    conn_func, curr_func = db_open()
    try:
        curr_func.execute('INSERT INTO output'
                          '(hash_values, comment_messages, comment_links, to_send) VALUES (?, ?, ?, ?)'
                          , (hash_value, message, comment_link, 1))
        conn_func.commit()
        print("The comment message has been added to db")

    except sqlite3.IntegrityError:
        print("The comment message was a duplicate")
    finally:
        curr_func.close()
        conn_func.close()
        print("Comment inserting function completed")


def links_fetch_and_randomize():
    conn, curr = db_open()
    curr.execute('SELECT group_links FROM input')
    group_links = curr.fetchall()
    db_close(conn,curr)

    random.shuffle(group_links)
    print("Group links are fetched and shuffled")
    return group_links


# Initializing databases through imporint database.py to main.py and running main.py
conn, curr = db_open()

curr.execute('CREATE TABLE IF NOT EXISTS output('
             'hash_values INTEGER PRIMARY KEY,'
             'post_links TEXT,'
             'post_messages TEXT,'
             'comment_links TEXT,'
             'comment_messages TEXT,'
             'to_send INTEGER'
             ')'
             )
curr.execute('CREATE TABLE IF NOT EXISTS input('
             'id INTEGER PRIMARY KEY,'
             'group_links TEXT'
             ')'
             )


conn.commit()


db_close(conn, curr)

