import os                                                                                                      
import requests
import csv
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def login(email, password):
    '''Login to chinesepod website'''
    driver.get('https://chinesepod.com/accounts/signin')
    email_input = driver.find_element_by_id('email')    
    password_input = driver.find_element_by_id('password')
    submit_input = driver.find_element_by_css_selector('button.btn.btn-lg.btn-red-border')
    email_input.send_keys(email)
    password_input.send_keys(password)
    submit_input.click()

def read_list_from_file(filename):
    '''Read information from file into list'''
    my_data = []
    with open(filename, 'r') as f:
        for line in f:
            my_data.append(line.rstrip())
    if not my_data:
        print('Error: File is empty.')
        return None
    return my_data

def download_image(my_dir, url):
    '''Download image for lesson'''
    image = driver.find_element_by_css_selector('img.big-thumb')
    image_filename = url.split('/')[-1] + '.jpg'
    src = image.get_attribute('src')
    if src:
        try:
            print('Downloading image {0}'.format(src))
            res = requests.get(src)
            res.raise_for_status()
        except requests.exceptions.MissingSchema:
            pass
    with open(os.path.join(my_dir, image_filename), 'wb') as f:
        for chunk in res.iter_content(1024):
            f.write(chunk)
    return image_filename

def move_filetypes(source_dir, target_dir, filetypes):
    '''Move all files in list of filetypes from source to target'''
    for f in os.listdir(source_dir):
        if any(filetype in f for filetype in filetypes):
            os.rename(os.path.join(source_dir, f), os.path.join(target_dir, f))
        else:
            print('Not going to move {0}'.format(f))


root_dir = os.path.join(os.path.expanduser('~'), 'chinesepod')
temp_dir = os.path.join(root_dir, 'downloads')
chrome_profile = webdriver.ChromeOptions()
profile = { "download.default_directory": temp_dir,
            "plugins.plugins_list": [{"enabled":False, "name":"Chrome PDF Viewer"}]}                
chrome_profile.add_experimental_option("prefs", profile)
driver = webdriver.Chrome(chrome_options=chrome_profile)

credentials = read_list_from_file(os.path.join(root_dir, 'login.txt'))
login(credentials[0], credentials[1])
urls = read_list_from_file(os.path.join(root_dir, 'chinesepod_urls.txt'))

for url in urls:
    table = []
    driver.get(url+'#dialogue-tab')
    print('Starting on {0}'.format(url))
    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.download-link')))
    image_filename = download_image(temp_dir, url)
    chinese = driver.find_elements_by_css_selector('p.font-chinese')
    english = driver.find_elements_by_css_selector('div.font-english')
    audio_files = driver.find_elements_by_css_selector('a.download-link')
    
    print('Chinese {0}'.format(len(chinese)))
    print('English {0}'.format(len(english)))
    print('Audio Files {0}'.format(len(audio_files)))

    
    for i in range(len(chinese)):
        chinese_text = chinese[i].text
        english_text = english[i].text.replace('show pinyin', '').replace('\n', '')
        old_dir = set(os.listdir(temp_dir))
        driver.get(audio_files[i].get_attribute('href'))
        time.sleep(5) # Selenium doesn't support waiting for downloads
        audio_filename = set(os.listdir(temp_dir)).difference(old_dir).pop()
        image_text = '<img src="{0}">'.format(image_filename)
        print('Downloaded {0} of {1}'.format(i+1, len(chinese)))
        table.append([chinese_text, english_text, '[sound:{0}]'.format(audio_filename), image_text])
    
    tsv_filename = os.path.join(temp_dir, '{0}.tsv'.format(url.split('/')[-1]))
    with open(tsv_filename, 'w') as f:
        writer = csv.writer(f, delimiter='\t', quotechar='|')
        writer.writerows(table)
    print('Successfully wrote Chinesepod data to {0}'.format(tsv_filename))

source_dir = temp_dir
target_dir = os.path.join(os.path.expanduser('~'), '.local/share/Anki2/User 1/collection.media/')
move_filetypes(source_dir, target_dir, ['.jpg', '.mp3'])
