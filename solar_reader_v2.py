import requests
import signal
import mysql.connector
from mysql.connector import Error
import threading
import time
import logging
import sys


running = True
poll_rate = 3
scrapers = None
database = None 
mycursor = None

"""
Online URLs

'auth_url', 'https://webportal-backend.delios-srl.it/authenticate',
'api_url', 'https://webportal-backend.delios-srl.it/machine_logs/get_machine_log_general',
"""

auth_payload = {
    'email': 'john.timmins@icloud.com',
    'password': 'j2Pe25fdZecx'
}

sites_to_scrape = [
    {
        'auth_url': 'https://webportal-backend.delios-srl.it/authenticate',
        'api_url': 'https://webportal-backend.delios-srl.it/machine_logs/get_machine_log_general',
    },
]


def intialise_database():
    global mycursor, database
    
    try:
        database = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="lol12345",
        )
        mycursor = database.cursor()

        with open('init_database.sql') as f:
            mycursor.execute(f.read())
        database.close()
    except:
        print('failed to create database')
        quit()

    try:
        connect_to_database()
        with open('init_table.sql') as f:
            mycursor.execute(f.read())
            database.commit()
    except:
        print('failed to create and intialise data table, but data base might exist')
        quit()
 

def main():
    if(len(sys.argv) < 2):
        print('no valid argument passed. Use these...')
        print('init -> to intialise solar reader database')
        print('run -> to start program')
        quit()
    elif(sys.argv[1] == 'help'):
        print('init -> to intialise solar reader')
        print('run -> to start program')
        quit()
    elif(sys.argv[1] == 'init'):
        print('setting up database...')
        intialise_database()
        quit()
    elif(sys.argv[1] != 'run'):
        print('no valid argument passed. Use these...')
        print('init -> to intialise solar reader database')
        print('run -> to start program')
        quit()

    init()

    while running:
        try:
            print('scrape...')
            run()
        except Exception as e:
            print(str(e))
            if(str(e) == 'POLLING_FAILED'):
                try:
                    re_login_scrapers()
                except:
                    print('failed to log back in')
            if(str(e) == 'STORING_FAILED'):
                try:
                    connect_to_database()
                except:
                    print('failed to connect to database')
        time.sleep(poll_rate)


def re_login_scrapers():
    global scrapers
    for scraper in scrapers:
        scraper.login()



def init():
    global scrapers

    try:
        connect_to_database()
    except:
        print('failed to connect to database')
        quit()
    try:
        scrapers = create_scrapers()
    except:
        print('failed to intialise scraper(s)')
        quit()


def run():
    global scrapers

    data_list = []
    for scraper in scrapers:
        try:
            data = scraper.poll_api()
            data_list.append(data)
        except:
            raise Exception('POLLING_FAILED')

    try:
        store(format_data(data_list))
    except:
        raise Exception('STORING_FAILED')


class Scraper():
    def __init__(self, auth_url, api_url):
        self.api_url = api_url
        self.auth_url = auth_url
        self.session = requests.Session()
        self.login()


    def login(self):
        response = self.session.post(self.auth_url, data=auth_payload, timeout=10)
        token = response.json()['token']
        self.data_request_payload = {"plant_id":548,"machine_id":""}
        self.session.headers['Authorization'] = 'Bearer ' + token


    def poll_api(self):
        return self.session.post(self.api_url, data=self.data_request_payload, timeout=10).json()


def create_scrapers():
    new_scrapers = []
    for site in sites_to_scrape:
        scraper = Scraper(site['auth_url'], site['api_url'])
        new_scrapers.append(scraper)
    return new_scrapers
    




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
    except Error as e:
        print("Failed to connect to database")


def format_data(data_list):
    formated_data = {}
    if(len(data_list) == 1):
        return data_list[0]
    elif(len(data_list) == 0):
        raise("no data to format...")
    
    for data in data_list:
        for key in data:
            if key in formated_data:
                formated_data[key] = formated_data[key] + data[key]
            else:
                formated_data[key] = data[key]
    formated_data['percentbattery'] = formated_data['percentbattery'] / len(data_list)
    formated_data['energy_battery_char'] = formated_data['energy_battery_char'] / len(data_list)
    formated_data['energy_battery_discha'] = formated_data['energy_battery_discha'] / len(data_list)
    formated_data['self_sufficiency'] = formated_data['self_sufficiency'] / len(data_list)
    return formated_data


def store(data):
    for key in data:
        mycursor.execute("update data set value=" + str(data[key]) + " where type='" + key + "';")
        database.commit()


def signal_handler(signal, frame):
    global running
    running = False
    quit()
signal.signal(signal.SIGINT, signal_handler)




# MAIN START
main()



quit()


