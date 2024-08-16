from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup 

from Config import Config
import time
import random



class DriverManager:
	_instance = None

	@staticmethod
	def get_driver():
		print('init')
		if DriverManager._instance is None:
			options = Options()
			options.add_argument('--headless')
			options.add_argument('--no-sandbox')
			options.add_argument('--disable-gpu')
			options.add_argument('--remote-debugging-port=9222')
			options.add_argument('--disable-dev-shm-usage')
			options.add_argument('--disable-software-rasterizer')
			options.add_argument('--disable-extensions')
			options.add_argument('--disable-background-networking')
			options.add_argument('--disable-default-apps')
			options.add_argument('--disable-sync')
			options.add_argument('--metrics-recording-only')
			options.add_argument('--disable-crash-reporter')
			options.add_argument('--disable-hang-monitor')
			options.add_argument('--disable-prompt-on-repost')
			options.add_argument('--disable-infobars')
			options.add_argument('--disable-popup-blocking')
			options.add_argument('--disable-features=TranslateUI')
			options.add_argument('--disable-background-timer-throttling')
			options.add_argument('--disable-renderer-backgrounding')
			options.add_argument('--disable-device-discovery-notifications')
			options.add_argument('--disable-software-rasterizer')
			options.add_argument('--disable-client-side-phishing-detection')
			options.add_argument('--disable-default-apps')
			options.add_argument('--no-first-run')
			options.add_argument('--no-service-autorun')
			options.add_argument('--no-default-browser-check')
			options.add_argument('--disable-sync-preferences')
			options.add_argument('--password-store=basic')
			options.add_argument('--use-gl=swiftshader')
			options.add_argument('--hide-scrollbars')
			options.add_argument('--mute-audio')
			options.add_argument('--incognito')
			options.add_argument('--disable-extensions-http-throttling')
			options.add_argument('--disable-blink-features=AutomationControlled')
			options.add_argument('--enable-automation')

			print('1 init')
			DriverManager._instance = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
		print('2 init')

		return DriverManager._instance
	

class parser:
	email = Config.email
	password = Config.password
	driver = DriverManager.get_driver()
	
	
	def log_in():
		print('##### driver getting')
		driver = DriverManager.get_driver()
		print('##### driver got')

		if len(parser.email) == 0:
			raise ValueError("The email value is invalid, probably empty")
		if len(parser.password) == 0:
			raise ValueError("The password value is invalid, probably empty")
		try:
			
			driver.maximize_window()
			driver.get('https://www.facebook.com/')
			print ("Opened facebook")
			parser.rand_rest()

			WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.NAME, "email"))
			).send_keys(parser.email)
			print ("Email Id entered")

			parser.rand_rest()

			WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.NAME, "pass"))
			).send_keys(parser.password)
			print ("Password entered")

			parser.rand_rest()

			WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.NAME, "login"))
			).click()

			parser.rand_rest()

		except Exception as e:
			print("The error catched: ", e)


	def rand_rest():
	   print("Resting...")
	   time.sleep(random.uniform(1,4))


	def page_switch(url):
		driver = DriverManager.get_driver()

		driver.get(url)
		print(driver.current_url)


	def scroll_to_bottom():
		driver = DriverManager.get_driver()
		driver.execute_script("window.scrollTo(0, 4000)")
		
			
	def extract_text(long_string, start_keywords=["Общедоступная группа","Доступно всем", "Закрытая группа"], end_keywords=["комментар", "Все реакции", "Нравится", "и ещё"], comment_number = None):
	   
		# Find the start index
		start_indices = []
		for start_keyword in start_keywords:
			idx = long_string.find(start_keyword)
			if not idx == -1:
				start_indices.append(idx+len(start_keyword))
		if start_indices:
			start_index = max(start_indices)
		else:
			start_index = 0
			
		
		# Find the end index
		end_indices = []
		for keyword in end_keywords:
			if keyword == 'комментар':
				if not comment_number == None:
					length = len(str(comment_number))
					idx = long_string.find(keyword, start_index)
					if idx != -1:
						end_indices.append(idx-(length+1))
			else:	
				idx = long_string.find(keyword, start_index)
				if idx != -1:
					end_indices.append(idx)
		if end_indices:
			end_index = min(end_indices)
		else:
			end_index = len(long_string)
		
		
		print("Starting index is " + str(start_index) + " and ending index is " + str(end_index))

		return long_string[start_index:end_index]
	
	def extract_duplicate(string):
		length = len(string)
		half_length = length // 2

		# Check if the string can be divided into two identical halves
		if string[:half_length] == string[half_length:]:
			return string[:half_length]
		else:
			return string
		

	def getBack(old_url):
		driver = DriverManager.get_driver()
		if not driver.current_url == old_url:
			print('redirected!!!')
			driver.back()
			print('got back!!!')

	
	def see_more(skip_indices=None):
		parser.rand_rest()
		if skip_indices is None:
			skip_indices = []
		driver = DriverManager.get_driver()
		old_url = driver.current_url
		parser.scroll_to_bottom()
		parser.rand_rest()
		parser.scroll_to_bottom()
		parser.rand_rest()
		readMore = driver.find_elements(By.XPATH, "//div[contains(text(), 'Ещё') and not(.//a[@href])]")
		print("Pressing all see more buttons")

		
		count = 0
		switch = False
		imposter = None
		if len(readMore) > 0:	
			
			for idx, i in enumerate(readMore):
				if idx in skip_indices:
					continue
				action=ActionChains(driver)
				try:
					parser.rand_rest()
					action.move_to_element(i).click().perform()
					if not(driver.current_url == old_url):
						imposter = idx
						switch = True
						break
					count += 1
				except:
					try:
						driver.execute_script("arguments[0].click();", i)
						count += 1
						pass
					except:
						continue
			if switch:
				parser.getBack(old_url)
				parser.rand_rest()
				parser.see_more(skip_indices + [imposter])

			return 

	def html():
		driver = DriverManager.get_driver()
		html_content = driver.page_source

		soup = BeautifulSoup(html_content, 'html.parser')

		feed_div = soup.find('div', {'role': 'feed'})
		return feed_div
	

	

#The code to include in scraper.py
# - Create a class named Parser
#  - log_in, page_switch, scroll_to_bottom method that returns driver
#  - 
