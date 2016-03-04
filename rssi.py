import sqlite3
import datetime
import serial


class Rssi(object):
    def __init__(self, device_id):
        self.device_id = device_id
        self.db_connection = sqlite3.connect('signals.db')
        self.db_connection.execute('CREATE TABLE IF NOT EXISTS connections (date text, device_id text, start_connect boolean);')
        self.db_connection.execute(
                '''INSERT INTO connections VALUES(?, ?, ?);''' ,
                (datetime.datetime.utcnow()
                    ,self.device_id
                    ,True,))
        self.db_connection.execute(
                'CREATE TABLE IF NOT EXISTS recording (device_id text, date text, rssi INTEGER)')
    def __enter__(self):
        return self 
    def record_rssi(self,rssi_value):
        self.db_connection.execute(
                '''INSERT INTO recording VALUES (?, ?, ?);'''
                ,( self.device_id
                , datetime.datetime.utcnow()
                , rssi_value,))
        self.db_connection.commit()
    def __exit__(self, exc_type, exc_value, traceback):
        self.db_connection.execute(
                '''INSERT INTO connections VALUES(?, ?, ?);'''
                ,( datetime.datetime.utcnow()
                , self.device_id
                , False, ))
        self.db_connection.commit()

        self.db_connection.close()

import threading 
class Serial_Reader(threading.Thread):
    def __init__(self, serial_instance):
        self._stopevent = threading.Event() 
        self.name = serial_instance.port_name
        Thread.__init__(self, name=self.name)
        self.serial_instance = serial_instance
        
    def run(self):
        with Rssi(self.name) as device_record:
            while self._stopevent.isSet():
                raw_data =self.serial_instance.readline()
                device_record.record_rssi(int(raw_data))
        print("Instance {} closing".format(self.name))

    def join(self, timeout=self.serial_instance.timeout):
        self._stopevent.set()
        threading.Thread.join(self, timeout)



