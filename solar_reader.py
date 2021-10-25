import threading

def run():
    print("starting solar reader")
    t1 = threading.Thread(target=reader)
    t2 = threading.Thread(target=writer)
    t1.start()
    t2.start()

def solar_reader():
    pass


class SolarReader():
    pass






run()
