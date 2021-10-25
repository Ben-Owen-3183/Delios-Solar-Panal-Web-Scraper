import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import mysql.connector
from mysql.connector import Error
import signal
import sys
import traceback

intialised = False
running = True
database = None
mycursor = None
prompt = '[solreader] '
close_thread = True
xpath_list = {
    'pv': '/html/body/app-dashboard/div/main/div/ng-component/div/div[3]/div/div/general-device/div/div/div[2]/div[1]/div[1]/div[2]/ul/li[2]/span',
    'battery_percent': '/html/body/app-dashboard/div/main/div/ng-component/div/div[3]/div/div/general-device/div/div/div[1]/div/div/div/label/span',
    'power': '/html/body/app-dashboard/div/main/div/ng-component/div/div[3]/div/div/general-device/div/div/div[2]/div[2]/div/div[2]/ul/li[1]/span'
}

solar_reader_thread = None
solar_reader_running = True

def run():
    global solar_reader_thread
    connect_to_database()
    command_line()
    solar_reader_thread.join()


def command_line():
    while running:
        try:
            process_input(input(prompt))
        except Exception as e:
            print(prompt + 'Processing Input Error: ' + str(e))


def process_input(input):
    global solar_reader_thread, intialised, running, solar_reader_running, intialised
    if input == 'quit':
        running = False
        clean_up()
        sys.exit()
    elif input == 'init':
        if solar_reader_thread != None:
            print(prompt + 'ending current thread')
            solar_reader_running = False
            print(prompt + 'waiting for thread to finish')
            solar_reader_thread.join()
            print(prompt + 'old thread closed correctly')
        print(prompt + 'starting new thread...')
        solar_reader_running = True
        intialised = False
        solar_reader_thread = threading.Thread(target=solar_reader)
        solar_reader_thread.start()
    elif input == 'start':
        intialised = True
    elif input == 'help':
        print_help()
    else:
        print(prompt + 'command "' + input + '" not recognised' )


def print_help():
    print(prompt + '-----------------------------------------')
    print(prompt + 'Help Menu:')
    print(prompt + '[Command]' + '\t\t[what it does]')
    print(prompt + '')
    print(prompt + 'quit' + '\t\tquits the program')
    print(prompt + 'start' + '\t\tstarts polling the web pages')
    print(prompt + 'init' + '\t\tintialises the browsers to be prepared for polling')
    print(prompt + 'help' + '\t\tprints this list')
    print(prompt + '-----------------------------------------')


def connect_to_database():
    global database, mycursor
    try:
        database = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="lol12345",
            database="solar"
        )
        mycursor = database.cursor()
        # mycursor.execute('use solar;')

    except Error as e:
        print(prompt + str(e))
        raise Exception('Failed to connect to database')


def signal_handler(signal, frame):
    clean_up()
    sys.exit()
signal.signal(signal.SIGINT, signal_handler)


def clean_up():
    global solar_reader_thread, mycursor, database, solar_reader_running
    try:
        print(prompt + "cleaning up")
        if solar_reader_thread != None:
            solar_reader_running = False
            print(prompt + "waiting for scraper thread to end")
            solar_reader_thread.join()
            print(prompt + "Thread ended safely")

        if mycursor != None:
            print(prompt + "closing database cursor")
            mycursor.close()

        if database != None:
            print(prompt + "closing database connection")
            database.close()

        print(prompt + 'clean up complete')
    except Exception as e:
        pass


def solar_reader():
    global solar_reader_running, intialised
    try:
        print(prompt + 'solar reader thread started')
        url1 = 'https://webportal.delios-srl.it/device_monitoring?id=548'
        url2 = 'https://webportal.delios-srl.it/device_monitoring?id=548'
        scraper_1 = None
        scraper_2 = None

        try:
            scraper_1 = WebScraper(url1, 1)
            scraper_2 = WebScraper(url2, 2)
        except Exception as e:
            print(prompt + "Solar reader failed to intialise")
            print(prompt + 'Error: '+ str(e))
            return
        print(prompt + 'Web Scrapers intialised. Run start command when ready')
        while not intialised:
            time.sleep(0.5)
            if not solar_reader_running:
                scraper_1.close()
                scraper_2.close()
                return

        print(prompt + 'starting web scrapers...')

        scraper_1.find_elements()
        scraper_2.find_elements()

        values = {
            'pv': 0,
            'battery_percent': 0,
            'power': 0
        }
        while solar_reader_running:
            time.sleep(1)
            scraper_1.poll()
            scraper_2.poll()
            for key, value in scraper_1.values.items():
                values[key] = str(float(scraper_1.values[key]) + float(scraper_2.values[key]))
            store_data(values)

        scraper_1.close()
        scraper_2.close()
    except Exception as e:
        scraper_1.close()
        scraper_2.close()
        print(prompt + "Solar Reader Thread Error: " + str(e))
        print(prompt + 'Thread finshed, type start to run again')
        traceback.print_exc()

def store_data(values):
    for key, value in values.items():
        mycursor.execute("update data set value=" + str(value) + " where type='" + key + "';")
        database.commit()


class WebScraper():
    def __init__(self, url, index):
        print(prompt + 'initialising WebScraper ' + str(index))
        self.index = str(index)
        self.web_elements = { 'pv': '', 'battery_percent': '', 'power': '' }
        self.browser = webdriver.Firefox(executable_path=r'./geckodriver')
        self.browser.get(url)
        self.values = { 'pv': 0, 'battery_percent': 0, 'power': 0 }


    def remove_letters(self, text):
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        text = text.lower()
        for letter in alphabet:
            text = text.replace(letter, '')
        return text

    def find_elements(self):
        try:
            for key, value in xpath_list.items():
                self.web_elements[key] = self.browser.find_element(By.XPATH, value)
        except Exception as e:
            print('\n' + prompt + 'can\'t read from page ' + self.index + '. Make sure you are logged into all browser instances and they are on the correct active pages')

    # reads the web page and updates values
    def poll(self):
        try:
            for key, value in self.web_elements.items():
                str_value = self.remove_letters(value.text)
                self.values[key] = float(str_value)
        except:
            pass


    # cleans up this scraper
    def close(self):
        self.browser.quit()


print(prompt + 'When the browsers load, log into each one and navigate to the correct pages')
print(prompt + 'when ready, run the command "start" to begin the program');
print(prompt + 'type help to print the following menu');
print_help()

try:
    run()
except Exception as e:
    print('Critcal Failure')
    print(prompt + 'Error: ' + str(e))
    print('Program closing...')
