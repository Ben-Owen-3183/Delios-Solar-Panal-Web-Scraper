import requests
import mysql.connector
from requests import Response
import logging
import sys
import time
import re

database = None
db_cursor = None
logger = logging.getLogger()


if len(sys.argv) > 1 and sys.argv[1] == 'showlogs':
    logging.basicConfig(filemode='a',
                        format='[%(asctime)s] [%(levelname)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)
else:
    logging.basicConfig(filename='solar_reader_logs',
                        filemode='a',
                        format='[%(asctime)s] [%(levelname)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.CRITICAL)



def connect_to_database():
    global database, db_cursor
    database = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="lol12345",
        database="solar"
    )
    db_cursor = database.cursor()


def store_data(machine_name, data):
    for k, v in data.items():
        db_cursor.execute(f"update data set value={v} where machine='{machine_name}' and type='{k}';")
        database.commit()


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class Scraper:
    def __init__(self, auth_url, api_url, machine_name):
        self.machine_name = machine_name
        self.auth_headers = {
            'Authorization': 'Basic dXNlcjp1c2Vy',
            'Cookie': 'dnx_web_interface={%22language%22:%22en%22%2C%22auth%22:{%22level%22:-1%2C%22expire%22:0%2C%22api_key%22:%22%22}}'
        }
        self.api_header = {
            'x-access-token':  '',
            'Cookie': ''
        }
        self.api_url = api_url
        self.auth_url = auth_url
        self.session = requests.Session()
        self.api_key = ''
        self.login()

    def login(self):
        response = self.session.get(self.api_url + self.auth_url, timeout=10, headers=self.auth_headers)
        self.api_key = response.json()['api_key']
        self.api_header['x-access-token'] = self.api_key
        self.api_header['Cookie'] = 'dnx_web_interface={"language":"en","auth":{"level":"0","expire":1681653802,"api_key":"' + self.api_key + '"}}'

    def poll_api(self):
        data = {
            **self.__poll_totalizer(),
            **self.__poll_dashboard(),
            **self.__poll_system()
        }

        renamed_data = dict()
        for k, v in data.items():
            renamed_data[camel_to_snake(k)] = v
        return renamed_data

    def __poll_totalizer(self):
        response: Response = self.session.get(
            self.api_url + '/api/v1/info/totalizer', timeout=10, headers=self.api_header
        )
        if response.status_code == 200:
            totalizers = response.json()
            return totalizers['totalizers']
        else:
            raise Exception(f'Response returned none 200 status. Status = {response.status_code}')

    def __poll_dashboard(self):
        response: Response = self.session.get(
            self.api_url + '/api/v1/dashboard', timeout=10, headers=self.api_header
        )
        if response.status_code == 200:
            dashboard = response.json()
            data = dict()
            for item in dashboard['variables']:
                data[item['ctrl_name']] = item['value']
            return data
        else:
            raise Exception(f'Response returned none 200 status. Status = {response.status_code}')

    def __poll_system(self):
        response: Response = self.session.get(
            self.api_url + '/api/v1/info/system', timeout=10, headers=self.api_header
        )
        if response.status_code == 200:
            system_values = response.json()
            data = dict()
            for item in system_values['variables']:
                data[item['ctrl_name']] = item['value']
            return data
        else:
            raise Exception(f'Response returned none 200 status. Status = {response.status_code}')


def login_scrapers(scrapers):
    for scraper in scrapers:
        scraper.login()


def create_scrapers() -> list:
    return [
        Scraper('/api/v1/token', 'http://81.187.83.190:844', 'machine-1'),
        Scraper('/api/v1/token', 'http://81.187.83.190:845', 'machine-2')
    ]


def run():
    try:
        connect_to_database()
    except Exception as e:
        logger.critical(f'Failed to connect to database. Error: {e}. Another attempt will be tried.')
        connect_to_database()

    scrapers: list
    try:
        scrapers = create_scrapers()
    except Exception as e:
        logger.critical(f'failed to create scrapers. Error: {e}. Another attempt will be tried.')
        scrapers = create_scrapers()

    try:
        login_scrapers(scrapers)
    except Exception as e:
        logger.critical(f'failed  to log in with scraper(s). Error: {e}. Another attempt will be tried.')
        login_scrapers(scrapers)

    scraping = True
    error_in_row_count = 0
    while scraping:
        print('Polling scrapers...')
        for scraper in scrapers:
            try:
                data = scraper.poll_api()
                store_data(scraper.machine_name, data)
                error_in_row_count = 0
            except Exception as e:
                error_in_row_count += 1
                logger.critical(f"something went wrong polling solar panels. Error: {e}")
                if error_in_row_count >= 3:
                    raise Exception('polling failed 3 times in a row.')
        time.sleep(3)


running = False
if __name__ == '__main__':
    running = True

while running:
    try:
        run()
    except Exception as e:
        logger.critical(f"Something went running during the running of the program. Error:{e}")
        logger.info('Restarting program...')
        database.close()

