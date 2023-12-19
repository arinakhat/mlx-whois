import requests
import hashlib
import time

from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

MLX_BASE = "https://api.multilogin.com"
MLX_LAUNCHER = "https://launcher.mlx.yt:45001/api/v1"
LOCALHOST = "http://127.0.0.1"
HEADERS = {
 'Accept': 'application/json',
 'Content-Type': 'application/json'
 }

#TODO: Insert your account information in both variables below.
USERNAME = "arina.khatuntceva@multilogin.com"
PASSWORD = "7327522Aa"

#TODO: Insert the Folder ID and the Profile ID below 
FOLDER_ID = "79b14e74-a29c-4a5d-b06e-37f7389066a7"
PROFILE_ID = "ef2d6d2c-c672-4d7d-8f8d-c0786042a673"

def signin() -> str:
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

info_file = "info.csv"
# f = open(info_file, 'a', encoding = 'utf-8')
# f.write('Expiration date, Phone number, Registration email')

# ask the user info from which domain name is required
domain_name = input("Domain name: ")

driver.implicitly_wait(15)

search = driver.find_element(By.XPATH, "/html/body/main/div[1]/div/form/div[1]/input")
search.send_keys(domain_name)

btn_search = driver.find_element(By.XPATH, "/html/body/main/div[1]/div/form/div[1]/div/button")
btn_search.click()
time.sleep(3)

exp_date = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div[3]/div[2]/div[5]/div[2]").text
        
reg_email = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div[3]/div[3]/div[10]/div[2]").text
        
owner_phone = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div[3]/div[3]/div[9]/div[2]").text
print(exp_date, reg_email, owner_phone)

# f.write('\n' + '{exp_date}' + ',' + '{owner_phone}' + ',' + '{reg_email}' + '\n')

with open(info_file, 'a', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Expiration date', 'Phone number', 'Registration email'])
    csvwriter.writerow([exp_date, owner_phone, reg_email])

driver.quit()
