import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import mysql.connector
from mysql.connector import Error
import signal
import sys


database = None
mycursor = None
browser = None
web_elements = dict()
url = 'https://webportal.delios-srl.it/device_monitoring?id=548'
xpath_list = {
    'pv': '/html/body/app-dashboard/div/main/div/ng-component/div/div[3]/div/div/general-device/div/div/div[2]/div[1]/div[1]/div[2]/ul/li[2]/span',
    'battery_percent': '/html/body/app-dashboard/div/main/div/ng-component/div/div[3]/div/div/general-device/div/div/div[1]/div/div/div/label/span',
    'power': '/html/body/app-dashboard/div/main/div/ng-component/div/div[3]/div/div/general-device/div/div/div[2]/div[2]/div/div[2]/ul/li[1]/span'
}


def signal_handler(signal, frame):
    print("closing browser and database connection")
    database.close
    browser.quit()
    print("bye")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


for key in xpath_list.items():
    web_elements[key] = None


try:
    database = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password=""
    )
    mycursor = database.cursor()
    mycursor.execute('use solar;')

except Error as e:
    print("failed to connect to database:")
    print(e)
    print("exiting program")
    quit()


print("initialising webdriver")

print("starting browser")
browser = webdriver.Firefox(executable_path=r'geckodriver.exe')
print("loading url '" + url + "'")
browser.get(url)
print("login and navigate to the correct page")
input("press any key to start scraper...")
print("Searching for web elements")
try:
    for key, value in xpath_list.items():
        web_elements[key] = browser.find_element(By.XPATH, value)
except Error as e:
    print("failed to find elements")
    print(e)
    print("scraper failed to run...")
    scraper_running = False
    time.sleep(1)
print("starting scraper")
while True:
    time.sleep(1)
    for element_key in web_elements.items():
        mycursor.execute("update data set value=" + element_key[key].text + " where type='" + key + "';")
        database.commit()

"""
battery %, PV Power and Power
john.timmins@icloud.com
j2Pe25fdZecx
"""
# pip install mysql-connector-python selenium
