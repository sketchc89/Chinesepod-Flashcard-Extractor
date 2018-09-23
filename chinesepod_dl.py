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

def download_mp3(my_dir, url):
    mp3s = driver.find_elements_by_css_selector('a.list-group-item')
    print(mp3s)
    for i, mp3 in enumerate(mp3s[1:]): #skip dashboard link
        src = mp3.get_attribute('href')
        print(src)
        mp3_filename = '{0}_{1}.mp3'.format(url.split('/')[-1], i)
        if src:
            try:
                print('Downloading mp3 {0}'.format(src))
                res = requests.get(src)
                res.raise_for_status()
                with open(os.path.join(my_dir, mp3_filename), 'wb') as f:
                    for chunk in res.iter_content(1024):
                        f.write(chunk) 
            except requests.exceptions.MissingSchema:
                print("Fail")
                pass
            
    return mp3_filename

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
    driver.get(url)
    print('Starting on {0}'.format(url))
    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.list-group-item')))
    download_mp3(temp_dir, url)

