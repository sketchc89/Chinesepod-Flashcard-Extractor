import os
import requests
import unicodecsv as csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def login(email, password):
	driver.get('https://chinesepod.com/accounts/signin')
	email_input = driver.find_element_by_id('email')	
	password_input = driver.find_element_by_id('password')
	submit_input = driver.find_element_by_css_selector('button.btn-lg')
	email_input.send_keys(email)
	password_input.send_keys(password)
	submit_input.click()

#def checkAudio(previous_state, directory):
#	current_state = set(os.listdir(directory))
#	while True:
#		if 'part' in current_state.difference(previous_state):
#			sleep(10)
#			current_state = set(os.listdir(directory))
#		elif 'mp3' in current_state.difference(previous_state):
#			print 'downloaded mp3 :)'
#			return current_state.difference(previous_state).pop(), current_state


root_dir = 'C:\\INSERT_PATH_HERE'
temp_dir = os.path.join(root_dir, 'downloads')
old_dir = set(os.listdir(temp_dir))
print(old_dir)

chrome_profile = webdriver.ChromeOptions()
profile = { "download.default_directory": temp_dir,
			"plugins.plugins_list": [{"enabled":False,
									  "name":"Chrome PDF Viewer"}]}
chrome_profile.add_experimental_option("prefs", profile)
driver = webdriver.Chrome(executable_path= os.path.join(root_dir, 'chromedriver.exe'),
                               chrome_options=chrome_profile)
driver.get("chrome://plugins/")

login('USERNAME', 'PASSWORD')

urls = []
url_filename = os.path.join(root_dir, 'chinesepod_urls.txt')

with open(url_filename, 'r') as f:
	for line in f:
		urls.append(line)

for url in urls:
	table = []
	new_url = url + '#dialogue-tab'
	stub = url.split('/')[-1].replace('\n', '')
	driver.get(new_url)
	#query redi for url
	print('Starting on {0}'.format(new_url))
	time.sleep(5)
	
	#Download image for all
	image = driver.find_element_by_css_selector('img.thumbnail')
	image_filename = stub + '.jpg'
	src = ''
	src = image.get_attribute("src")
	if src:
		try:
			# Download the image.
			print('Downloading image {0}...'.format(src))
			res = requests.get(src)
			res.raise_for_status()
		except requests.exceptions.MissingSchema:
			continue
	with open(os.path.join(temp_dir, image_filename), 'wb') as f:
		for chunk in res.iter_content(1024):
			f.write(chunk)

	#pull text and audio for all
	chinese = 		driver.find_elements_by_css_selector('p.font-chinese')
	english = 		driver.find_elements_by_css_selector('div.font-english')
	audio_files = 	driver.find_elements_by_xpath("//div[@class='jp-interface']/a")
	print('Chinese {0}\nEnglish {1}\nAudio Files {2}\n'.format(len(chinese), len(english), len(audio_files)))
	count = 0
	for i in range(len(chinese)):
		chinese_text = chinese[i].text
		english_text = english[i].text.replace('\nshow pinyin', '')
		print(audio_files[i].get_attribute('href'))
		old_dir = set(os.listdir(temp_dir))
		audio_files[i].click()
		time.sleep(2)
		audio_filename = set(os.listdir(temp_dir)).difference(old_dir).pop()
		print('Downloaded {0} :)'.format(audio_filename))
		image_text = '<img src="{0}">'.format(image_filename)
		print(image_text, '\n')
		table.append([chinese_text, english_text, '[sound:{0}]'.format(audio_filename), image_text])

	#save data to tsv compatible with anki
	tsv_filename = os.path.join(temp_dir, '{0}.tsv'.format(stub))
	with open(tsv_filename, 'wb') as f:
		writer = csv.writer(f, delimiter='\t', quotechar = '|')
		writer.writerows(table)
	print('Successfully wrote Chinesepod data to {0}'.format(tsv_filename))

source_dir = 'C:\\SOURCE_DIR'
target_dir = 'C:\\TARGET_DIR'
#def move_filetypes(source_dir, target_dir):
for f in os.listdir(source_dir):
	if '.jpg' in f or '.mp3' in f:
		os.rename(os.path.join(source_dir, f), os.path.join(target_dir, f))
	else:
		print('Not going to move {0}'.format(f))
