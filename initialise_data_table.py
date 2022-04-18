from solar_reader_v3 import Scraper, camel_to_snake
import mysql.connector

database = None
db_cursor = None
# create table data ( type varchar(255) , value int , machine varchar(255));
try:
    database = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="lol12345",
        database="solar"
    )
    db_cursor = database.cursor()
except Exception as e:
    print(f"Failed to connect to database. Error: {e}")

base_url = 'http://81.187.83.190:844'

scraper = Scraper('/api/v1/token', 'http://81.187.83.190:844', 'machine-1')
scraper.login()
data = scraper.poll_api()

for k, v in data.items():
    stmt = f"""
    INSERT INTO data(type, value, machine)
    VALUES ('{camel_to_snake(k)}', '{-1}', 'machine-1');
    """
    db_cursor.execute(stmt)
    database.commit()

for k, v in data.items():
    stmt = f"""
    INSERT INTO data(type, value, machine)
    VALUES ('{camel_to_snake(k)}', '{-1}', 'machine-2');
    """
    db_cursor.execute(stmt)
    database.commit()