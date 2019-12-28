import serial
import time
import struct
import os
import keyboard

port    =   '/dev/ttyUSB0'

if __name__=='__main__':
   while True:

        try:
            ser = serial.Serial( port, 9600, timeout=1 ) 
            ser.open()
            print('COM is open .')
            time.sleep(1)

        except serial.SerialException:
            print('Can not found device, raise SerialException .')
            time.sleep(1)

        except KeyboardInterrupt:
            print('Interruption Ctrl+C in main thread, ready to exit . ')
            time.sleep(1)
            exit()
    
        except :
            print('Unexpectable error happened ! ')
            time.sleep(1)

    ser.close()