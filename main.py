# importing necessary libraries, files and functions


from time import sleep


from scraper import parser
from scraper import DriverManager

from engine.VecDB_STF import VDB
from engine.VecDB_STF.config import Config

import sqlite3
import random



from db import db_open
from db import db_close
from db import hash_generator
from db import db_insert_with_comparison_comment_message
from db import db_insert_with_comparison_post_message
from db import links_fetch_and_randomize

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains



def main():
	switch = False
	api = VDB(Config, online=True)

	while True:
		try:
			thl = 0

			try:
				with open('level.txt', 'r') as file:
					thl = float(file.read())
			except:
				thl = 0.3
			
			raw_links = links_fetch_and_randomize()

			group_links_order = list(set(raw_links))
			group_links = random.sample(group_links_order, len(group_links_order))
			print(group_links)
			# api.load()

			if group_links:	
				for current_link in group_links:
					#current_url = "https://www.facebook.com/groups/rentalanya/?locale=ru_RU"
					current_url = current_link[0]
					try:
						if not switch:
							parser.log_in()
							parser.rand_rest()
							switch = True
						
						parser.page_switch(current_url)
						print("test end", DriverManager.get_driver().current_url)
						if not DriverManager.get_driver().current_url == current_url:
							print("the page switch did not go well")
							continue
						parser.rand_rest()
						print("Checking for working start")
						
						parser.see_more()
						parser.rand_rest()
						feed_div = parser.html()
						
						
						if feed_div:
							
							with open('output.txt', 'w', encoding='utf-8') as file:
								children_long = feed_div.find_all(recursive=False)
								children = children_long[:len(children_long)//2]
								i = 0
								
								for child in children:
									child_text = child.get_text()
									# if len(child_text) == 0:
									#	 i +=1
									#	 continue
									# ///// Fetches all links in post and returns those that begin with the link below
									links = child.find_all('a', href=True)
									filtered_links = [link['href'] for link in links if link['href'].startswith('https://www.facebook.com/groups')]

									#///// Duplicate functions erases the chance for existence of posts that has two identical strings
									
									comment_num = len(filtered_links) - 1
									duplicate_check = parser.extract_text(child_text, comment_number=comment_num)
									extracted_text = parser.extract_duplicate(duplicate_check)

									if (len(extracted_text) == 0):
										i+=1
										continue
									
									
									
									if filtered_links:
										
										file.write(f"\n{'='*10} Child {i} {'='*10}\n")
										# file.write(child.prettify())
										file.write(str(filtered_links) + '\n')
										
										file.write(str(extracted_text) + '\n')

										i += 1

										print("Using ENGINE to analyze text")
										
										# print(api.vocab)
										print('### ', extracted_text, api.confidence(extracted_text, exact=True, confidence_threshold=thl), thl)
										if(api.confidence(extracted_text, exact=False, confidence_threshold=thl)):
										#if True:
											print("Check start")
											conn, curr = db_open()
											count = 0
											hashed = hash_generator(extracted_text)
											curr.execute("SELECT hash_values FROM output")
											db_hashes = curr.fetchall()
											if db_hashes:
												is_duplicate = any(db_hash[0] == hashed for db_hash in db_hashes)
												if not is_duplicate:

													curr.execute("INSERT INTO output (hash_values, post_links, post_messages, to_send) VALUES (?,?,?,?)", (hashed, filtered_links[0], extracted_text, 1))
													conn.commit()
													print("Added new post in db")
													db_close(conn, curr)
												else:
													print("COPY post was not inserted")
													db_close(conn,curr)
													continue
											else:
												
												curr.execute("INSERT INTO output (hash_values, post_links, post_messages, to_send) VALUES (?,?,?,?)", (hashed, filtered_links[0], extracted_text, 1))
												conn.commit()
												db_close(conn,curr)
												print(f"THe list was empty, so {i}th post was inserted")
										elif not api.confidence(extracted_text, confidence_threshold=0.5, exact=False):
											print("The post was discarded by ENGINE")
											continue
									
								conn, curr = db_open()
								curr.execute('SELECT post_messages, post_links FROM output')
								results = curr.fetchall()

								# Initialize two empty lists
								post_messages = []
								post_links = []

								# Iterate through the results and append to the respective lists
								for row in results:
									post_messages.append(row[0])
									post_links.append(row[1])
								for idx, i in enumerate(post_messages):
									print(f"Post number {idx}")
									print(i)
									print(post_links[idx])
									print("\n"*10)
								db_close(conn,curr)
						
					except Exception as e:
						# Handle any exceptions raised during login
						print("Unexpected error catched:", e)
			else:
				print("Group links were not fetched. Either the db is empty or something went wrong")
				continue
		except Exception as e:
			 print("The exception HAVE BEEN RAISED: ", e)
			 continue
		 


if __name__ == "__main__":
	main()
