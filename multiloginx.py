import requests
import hashlib
import time

from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

import csv

MLX_BASE = "https://api.multilogin.com"
MLX_LAUNCHER = "https://launcher.mlx.yt:45001/api/v1"
LOCALHOST = "http://127.0.0.1"
HEADERS = {
 'Accept': 'application/json',
 'Content-Type': 'application/json'
 }

# INFO TO PROVIDE TO SIGN IN AND START A PROFILE
USERNAME = ""
PASSWORD = ""

FOLDER_ID = ""
PROFILE_ID = ""

def signin():
    payload = {
        'email': USERNAME,
        'password': hashlib.md5(PASSWORD.encode()).hexdigest()
    }

    r = requests.post(f'{MLX_BASE}/user/signin', json=payload)
    
    if(r.status_code != 200):
        print(f'\nError during login: {r.text}\n')

    response =r.json()['data']
    token = response['token']

    return token


def start_profile() -> webdriver:
    r = requests.get(f'{MLX_LAUNCHER}/profile/f/{FOLDER_ID}/p/{PROFILE_ID}/start?automation_type=selenium', headers=HEADERS)

    response = r.json()

    if(r.status_code != 200):
        print(f'\nError while starting profile: {r.text}\n')
    else:
        print(f'\nProfile {PROFILE_ID} started.\n')

    selenium_port = response.get('status').get('message')
    print(f'SeleniumPort: {selenium_port}')
    
    driver = webdriver.Remote(command_executor=f'{LOCALHOST}:{selenium_port}', options=ChromiumOptions())

    return driver

def stop_profile() -> None:
    r = requests.get(f'{MLX_LAUNCHER}/profile/stop/p/{PROFILE_ID}', headers=HEADERS)

    if(r.status_code != 200):
        print(f'\nError while stopping profile: {r.text}\n')
    else:
        print(f'\nProfile {PROFILE_ID} stopped.\n')


token = signin()
HEADERS.update({"Authorization": f'Bearer {token}'})


driver = start_profile()
driver.get('https://www.whois.com/whois/')

# TYPE IN TO REQUEST INFO FROM THIS SPECIFIC DOMAIN
domain_name = input("Domain name: ")

driver.implicitly_wait(15)

search = driver.find_element(By.XPATH, "/html/body/main/div[1]/div/form/div[1]/input")
search.send_keys(domain_name)

btn_search = driver.find_element(By.XPATH, "/html/body/main/div[1]/div/form/div[1]/div/button")
btn_search.click()
time.sleep(3)

# GATHERING THE DATA
exp_date = driver.find_elements(By.XPATH, "/html/body/div[1]/div[1]/main/div[3]/div[2]/div[5]/div[2]")
        
reg_email = driver.find_elements(By.XPATH, "/html/body/div[1]/div[1]/main/div[3]/div[3]/div[10]/div[2]")
        
owner_phone = driver.find_elements(By.XPATH, "/html/body/div[1]/div[1]/main/div[3]/div[3]/div[9]/div[2]")

# IF THE DATA IS NOT PRESENT IN THE PAGE, IT WILL ASSIGN A STRING VALUE "Empty"
if len(exp_date) == 0:
    exp_date_value = 'Empty'
else:
    exp_date_value = exp_date[0].text

if len(reg_email) == 0:
    reg_email_value = 'Empty'
else:
    reg_email_value = reg_email[0].text

if len(owner_phone) == 0:
    owner_phone_value = 'Empty'
else:
    owner_phone_value = owner_phone[0].text

# CREATING A CSV FILE AND SAVING THE DATA
info_file = "info.csv"
with open(info_file, 'a', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Expiration date', 'Phone number', 'Registration email'])
    csvwriter.writerow([exp_date_value.replace(",", "|"), owner_phone_value.replace(",", "|"), reg_email_value.replace(",", "|")])


stop_profile()
