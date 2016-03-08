import sqlite3
import datetime
import serial


class Signal_Repository(object):
    '''
    Repository for Signal_Repository information.
    
    Information is stored in 'database.db' - a sqlite database.
    
    Signal_Repository.commits represents the number of records written
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
        Signal_Repository.commits+=1
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
        protocol = [ ('', b'\n\n\n\n'),
                     ('In: OPMOD:', b'RX0'),
                     ('In: SAM_INTV:', b'100'),
                     ('In: CHNUM:', b'C11')]

        reader = Serial_Reader(serial_instance, parse_data, protocol)
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
        #  This is also how Signal_Repository knows that it is finished recording.
        with Signal_Repository(self.name) as device_record:
            # Initialize the protocol to begin transmitting data
            Protocol.start_reading(self.serial_instance, 
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


class Protocol:
    '''
    Methods related to initializing protocols.
    '''
    
    @staticmethod
    def start_reading(serial_connection, protocol_args, parse_data):
        '''
        Performs setup protocol for reading RSSI data.

        WARNING:
            Runs in infinite loop if device is not in state to accept 
        the protocol.
        '''
        ser = serial_connection
        # Having the list end at None, None lets us know that it is finished
        protocol_args.append((None,None))
        
        for i,(expected_prompt, arg) in enumerate(protocol_args):
            if expected_prompt is None:
                return

            next_prompt, next_arg = protocol_args[i+1]
            Protocol.handleArg(ser, expected_prompt, arg, next_prompt, parse_data)


    @staticmethod
    def handleArg(ser, expected_prompt, arg, next_prompt, parse_data):
        '''
        Repeatedly inputs the argument with respect to a prompt.
        When the next_prompt is detected, this function will quit.
        
        Parse_data is used to detect whether the serial connection
        is transmitting the expected output.  If that is the case and
        the next_prompt is None, we assume that this is the last argument
        of the protocol. 
        '''
        print("Handling prompt {}".format(expected_prompt))
        while True:
            cur_line = ser.readline()
            ser.write(arg)
            # If the data matches our input parser,
            #     the protocol is finished. 
            if parse_data(cur_line) is not None and next_prompt is None:
                return
            # If the next prompt has been reached, the current prompt was 
            #     handled
            elif next_prompt is not None and next_prompt in cur_line: 
                return


            

