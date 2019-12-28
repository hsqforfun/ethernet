###################################
# README:
#   Platform:       Ubuntu 18.04.1 
#                   CentOS6.7 verified
#   Python:         3.6.9/3.6.8
#   Required:       pip3 install prettytable 
#   Check Speed:    sudo apt-get install sysstat 
#                   cmd=> sar -n DEV 1 100
#                   or scarpy | wireshark
#   Description:    aim at send and receive data in one loop 
#                   by '--loop num' to set loop times
###################################

import socket
import time
import os
import struct 
from prettytable import PrettyTable
import sys
import threading
from argparse import ArgumentParser

#translation type functions:
def bytes_get_int(recv_data):
	a=int.from_bytes(recv_data, byteorder='big', signed=False)
	return a

def int_to_bytes(int_data, length = 10):
	bytes_data = int_data.to_bytes(length,"big", signed=False)
	return bytes_data

#Parameters: DO NOT CHANGE ME
BUFSIZE     = 1024
ETH_P_DEF   = 0x8874	        #user defined
ETH_P_IP    = 0x0800	        #IP type 
Board_MAC   = b'\xc0\xb1\x3c\x88\x88\x90'
Ubuntu_MAC  = b'\x00\x0c\x29\x18\x7c\x12'
Centos_MAC  = b'\x00\x0c\x29\xbc\xad\xce'
type_DEF    = b'\x88\x74' 
type_IP     = b'\x08\x00'
passme      = b'\x11\x11'
numberID    = 1

#   Parameters: CHANGE ME !!!!!!
NIC = "eth0"
check_type = type_DEF
Dst_MAC = Board_MAC
Src_MAC = Centos_MAC
server_proto = socket.htons(ETH_P_DEF)
client_proto = socket.htons(ETH_P_DEF)

#---------------------------------------------------------------
# Parameters: Used in the loop
parser = ArgumentParser(description='Process some integers.')
parser.add_argument("--loop", help="loop default is 10", type = int)
parser.add_argument("--timewait", help="wait for recv thread\
    , default is 2", type = int)
parser.add_argument("--timeahead", help="send thread time ahead of recv thread\
    , default is 1", type = int)
parser.add_argument("--ms", help="wait ms microsecond in order to match recv speed\
    , default is 5", type = int)    
parser.add_argument("-Ubuntu", help="check sqhuang's ubuntu,\
    default is not", action="store_true")
args = parser.parse_args()

if args.ms:
    ms = args.ms
else:
    ms = 10
    
if args.timewait:
    time_wait = args.timewait
else:
    time_wait = 2

if args.loop:
    loop_num = args.loop
else:
    loop_num = 10

if args.timeahead:
    time_ahead = args.timeahead
else:
    time_ahead = 1

if args.Ubuntu:
    NIC = "ens39"
    check_type = type_DEF
    Dst_MAC = Board_MAC
    Src_MAC = Ubuntu_MAC
    server_proto = socket.htons(ETH_P_DEF)
    client_proto = socket.htons(ETH_P_DEF)
else:
    pass

count = 1
BUFFER_send = []
BUFFER_send_store = []
BUFFER_recv = []
BUFFER_recv_store = []
BUFFER_CHECK = []
BUFFER_ID = []

SEND_DONE = 0

for _ in range(loop_num):
    BUFFER_send.append(0)
    BUFFER_recv.append(0)
    BUFFER_ID.append(0)
    
#--------------------------------------------------------------
# __Main__

#FIXME:socket.htons(ETH_P_DEF) SHOULD BE ANY NUMBE
server = socket.socket( socket.PF_PACKET, socket.SOCK_RAW, server_proto )
server.bind( (NIC, server_proto ) ) 
clientPC = socket.socket( socket.PF_PACKET, socket.SOCK_RAW, client_proto )

header = struct.pack("6s6s2s", Dst_MAC, Src_MAC, type_DEF )

numberID_bytes = int_to_bytes( numberID , 4 )
number = struct.pack( "4s",numberID_bytes[::-1] )

#Start send data with 0
send_data = bytes(1003) + b'\x11'
data_packet =  header + passme + number + send_data

print("Initial data_packet : "),
print( struct.unpack( str(len(data_packet)) + "s", data_packet) )
print("Ready.")
print('----------------------------------------------------------')


#***********************  multi threading  *************************
def recv():
    global SEND_DONE 
    global BUFFER_recv
    global BUFFER_recv_store
    global count_recv
    print('')
    print("Entering recv function!!!")
    count_recv = 0
    clientPC.setblocking(False)

    while(count_recv < loop_num):
        print('wait for receiving the Num.%d data .' %(count_recv+1) )
        
        if( SEND_DONE == 0 ):
            try:
                DATA = clientPC.recv(BUFSIZE)
                print("--------Num.%d Data is received--------" %(count_recv+1) )

                print("Receive packet type is : ",end='')
                print( struct.unpack( "!2s", DATA[12:14] ) )

                recv_id_bytes = DATA[16:20]
                recv_id_bytes = recv_id_bytes[::-1]
                recv_id_int = bytes_get_int(recv_id_bytes)
                BUFFER_ID[count_recv] = recv_id_int

                recv_data_bytes = DATA[20:1024]
                recv_data_int = bytes_get_int(recv_data_bytes)
                print("The data recv is : %d"%(recv_data_int) )
                BUFFER_recv[count_recv] = (recv_data_int)

                count_recv += 1
            except BlockingIOError:
                #print('...')
                pass
            except :
                print("Something wrong.")
        else:
            print('Ready to close recv thread. ')
            break

    BUFFER_recv_store = BUFFER_recv.copy()
    # BUFFER_recv.clear()
    clientPC.close() 
    SEND_DONE = 0
    print('Recv thread is done!!!')

def send():
    global SEND_DONE 
    global BUFFER_send
    global BUFFER_send_store
    global numberID

    print('')
    print("Entering send function!!!")
    count_send = 0
    while(count_send < loop_num):

        numberID_bytes = int_to_bytes( numberID , 4 )
        number = struct.pack( "4s",numberID_bytes[::-1] )
        data_packet =  header + passme + number + send_data

        server.send(data_packet)
        print( "*******Num.%d Data is sending..."%(count_send+1) )

        send_data_int = bytes_get_int(send_data)
        print("The data send is : %d"%(send_data_int) )
        BUFFER_send[count_send] = send_data_int
        count_send += 1
        numberID += 2
        time.sleep(0.001 * ms)

    time.sleep(time_wait)
    SEND_DONE = 1
    BUFFER_send_store = BUFFER_send.copy()
    # BUFFER_send.clear()
    server.close()
    print('Send thread is done!!!')
    print('')

def test_speed():
    print('')
    print('Time   IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s   ifutil')
    cmd = 'sar -n DEV 1 5 |grep ' + NIC
    os.system(cmd)

def check():
    print('')
    print('Enter check thread : ')

    gap=len(BUFFER_send_store)-len(BUFFER_recv_store)
    if (gap > 0):
        for _ in range(gap):
            BUFFER_recv_store.append(0)
    # print(len(BUFFER_send))
    # print(len(BUFFER_send_store))
    # print(len(BUFFER_recv))
    # print(len(BUFFER_recv_store))
    # print(len(BUFFER_send))

    for i in range( len(BUFFER_send) ):
        BUFFER_CHECK.append(0)

    for ii in range( len(BUFFER_send) ):
        if ( (BUFFER_send_store[ii] == BUFFER_recv_store[ii]) ):
            BUFFER_CHECK[ii] = 1
        else:
            pass

    print("Buffer Check is :")     
    print(BUFFER_CHECK)
    print('Incorrect amout is %d .'%BUFFER_CHECK.count(0) )
    BUFFER_send_store.clear()
    BUFFER_recv_store.clear()
    # BUFFER_CHECK.clear()
    print('check done.')
        

t_recv = threading.Thread(target=recv,daemon = True)
t_send = threading.Thread(target=send,daemon = True)
sar = threading.Thread(target=test_speed,daemon = True)
check = threading.Thread(target=check,daemon = True)

#sar.start()
t_send.start()
time.sleep(time_ahead)
t_recv.start()

#sar.join()
t_send.join()
t_recv.join()

check.start()
check.join()

#************************ main thread ************************
time.sleep(2)
SEND_DONE = 0

print('')
print("Buffer send is :")
print(BUFFER_send)
print('')
print("Buffer receive is :")
print(BUFFER_recv)
print('')
print("Buffer ID is :")
print(BUFFER_ID)
print('')
print('Complete %.2f %%' %( (count_recv/loop_num)*100 ) )
print('Main thread is done')
   
