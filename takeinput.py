import rssi


recorder = rssi.Rssi("stream1")
readmore = True
while readmore:
    rssi = raw_input("Enter an rssi value ")
    try:
        value = int(rssi)
        recorder.record_rssi(value, 11)
        
    except ValueError:
        readmore = False


