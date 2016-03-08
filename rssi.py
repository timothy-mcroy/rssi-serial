import sqlite3
import datetime
import serial


class Rssi(object):
    '''
    Repository for Rssi information.
    
    Information is stored in 'signals.db' - a sqlite database.
    
    Rssi.commits represents the number of records written
        during this connection.  
        It is NOT the total number of records. 

    '''
    commits = 0
    def __init__(self, device_id):
        '''
        device_id : str - Identifies the device in the database
        '''
        self.device_id = device_id
        # We want to know that a connection happened
        self.db_connection = sqlite3.connect('signals.db')
        self.db_connection.execute(
                'CREATE TABLE IF NOT EXISTS connections (date text, device_id text, start_connect boolean);')
        args = (datetime.datetime.utcnow(), self.device_id, True,)
        self.db_connection.execute(
                '''INSERT INTO connections VALUES(?, ?, ?);''' 
                ,args)
        self.db_connection.execute(
                'create table if not exists recording (device_id text, date text, channel integer, rssi integer)')
    def __enter__(self):
        return self 
    def record_rssi(self,channel,rssi_value):
        '''
        channel : int - The channel that the rssi value was recorded on
        rssi_value : int 
        '''
        args = (self.device_id, datetime.datetime.now(),channel, rssi_value,)
        self.db_connection.execute(
                '''INSERT INTO recording VALUES (?, ?, ?, ?);'''
                ,args)
        self.db_connection.commit()
        Rssi.commits+=1
    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Closes the database connection after recording an end-connection entry.
        '''
        args = (datetime.datetime.now(), self.device_id, False,)
        self.db_connection.execute(
                '''INSERT INTO connections VALUES(?, ?, ?);'''
                ,args)
        self.db_connection.commit()

        self.db_connection.close()

import protocol_init
import threading 
class Serial_Reader(threading.Thread):
    """
    Usage
    ```
        import serial
        import time
        serial_instance = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
        def parse_data(data):
            return data_as_parsed_tuple(data)
        reader = Serial_Reader(serial_instance, parse_data)
        reader.start()
        # Record for 5 seconds
        time.sleep(5)  
        # End recording and close the thread.
        reader.join()
    ```
    """
    def __init__(self, serial_instance, parse_data, protocol, address = None):
        '''
        parse_data should parse the data read by the serial_instance
        and return (channel_num, rssi)
        '''
        self._stopevent = threading.Event() 
        self.parse_data = parse_data
        if address is None:
            threading.Thread.__init__(self, name=serial_instance.name)
        else:
            threading.Thread.__init__(self, name=str(address))
        self.serial_instance = serial_instance
        self.times_data_failed_to_match = 0
        self.protocol = protocol
        
    def run(self):
        '''
        This method should not be directly called.
        '''
        # Using `with` is important to ensure automatic disposal of resources
        #  This is also how Rssi knows that it is finished recording.
        with Rssi(self.name) as device_record:
            # Initialize the protocol to begin transmitting data
            protocol_init.start_reading(self.serial_instance, 
                    self.protocol, self.parse_data)
            print("Collecting data on {}".format(self.name))
            # Collect rssi information until self.join() is called.
            while not self._stopevent.isSet():
                # Get data from serial connection
                raw_data =self.serial_instance.readline()
                # Parse data into tuple to be recorded
                reported = self.parse_data(raw_data)
                if reported is None:
                    self.times_data_failed_to_match +=1
                    continue
                #expand the tuple into the arguments for record_rssi
                device_record.record_rssi(*reported)
        print("Instance {} closing".format(self.name))

    def join(self, timeout=None):
        if timeout == None:
            self.serial_instance.timeout
        # _stopevent is the loop invariant.
        self._stopevent.set()
        threading.Thread.join(self, timeout)



