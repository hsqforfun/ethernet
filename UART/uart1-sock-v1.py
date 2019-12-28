###############################################################################
#   Python      :   python 3.6.8
#   Requisite   :   keyboard
#                   prettytable
#   purpose     :   specify csv output
#                   real time check reset-all == 1 warning      unideal
#                   0x input write                              done~
###############################################################################
import socket
import serial
import time
import struct
import os
import csv
import threading
import keyboard
from prettytable import PrettyTable
from argparse import ArgumentParser

import tkinter
import tkinter.messagebox


###############################################################################
#   cmd parameters :
###############################################################################

parser = ArgumentParser(description='Set some parameters or use default setting .')
parser.add_argument("--port", help="set the COM port,\
     default is COM8 .", type = str)
parser.add_argument("--sleep", help="set the sleep time every loop,\
     default is 1.0 .", type = float)   
parser.add_argument("--timeout", help="set the timeout of read function,\
     default is 1.0 .", type = float)   
args = parser.parse_args()

if args.port:
    port    =   args.port
else:
    port    =   '/dev/ttyUSB0'

# None:wait forever; 0:do not wait; n:timeout is n second
if args.timeout:
    user_timeout    =   args.timeout
else:
    user_timeout    =   1.0

if args.sleep:
    sleep_time    =   args.sleep
else:
    sleep_time    =   1.0
# Use code below to test which port is available
# port_list = list( serial.tools.list_ports.comports() )
# print(port_list)
# if len(port_list) == 0:
#    print('No port available . ')
# else:
#     for i in range(0,len(port_list)):
#         print(port_list[i]) 

###############################################################################
#   Static Parameters :
###############################################################################

READ    =   ( 0b0 << 7 )
WRITE   =   ( 0b1 << 7 )

baudrate        =   9600    
READ_SIZE       =   4       # read up to 4 bytes
WRITE_SIZE      =   1       # write data is 8 bit, 1 byte 

#   R
Time            =   0x00
Err_sram        =   0x04
Err_pllser      =   0x05
Err_pllsys      =   0x06
Err_plleth      =   0x07
Err_pll1        =   0x08
Err_pll2        =   0x09
Err_pllcas      =   0x0A
Err_dff         =   0x0B
Err_dffinv      =   0x0C
Err_lane0       =   0x0D
Err_lane1       =   0x0E
Err_linkdown0   =   0x0F
Err_linkdown1   =   0x10
Err_linkrecvy0  =   0x11
Err_linkrecvy1  =   0x12
Err_cpu         =   0x13
Reset_ALL       =   0x1C

#   W/R
Pll_freq        =   0x14
Clr_err_ser     =   0x15
Clr_err_eth     =   0x16
Clr_err_sram    =   0x17
Clr_err_pll     =   0x18
Clr_err_dff     =   0x19
Reset_ser       =   0x1A
Reset_sram      =   0x1B

read_reg        =   [0 for _ in range(18)]
read_reg[0]     =   Time
read_reg[1]     =   Err_sram
read_reg[2]     =   Err_pllser
read_reg[3]     =   Err_pllsys
read_reg[4]     =   Err_plleth
read_reg[5]     =   Err_pll1
read_reg[6]     =   Err_pll2
read_reg[7]     =   Err_pllcas
read_reg[8]     =   Err_dff
read_reg[9]     =   Err_dffinv
read_reg[10]    =   Err_lane0
read_reg[11]    =   Err_lane1
read_reg[12]    =   Err_linkdown0
read_reg[13]    =   Err_linkdown1
read_reg[14]    =   Err_linkrecvy0
read_reg[15]    =   Err_linkrecvy1
read_reg[16]    =   Err_cpu
read_reg[17]    =   Reset_ALL

client_uart1 = socket.socket()         # 创建 socket 对象
host = socket.gethostname()         # 获取本地主机名
user_port = 4877                         # 设置端口
WARNING_ResetAll    =   b'\xa0'
###############################################################################
#   File and Print related :
###############################################################################
# filename    =   time.strftime("%Y.%m.%d-%H.%M.%S") + '--' + 'log'
# f_uart      =   open( 'Uart-' + filename + ".txt ", mode = "w")

filename    = 'Uart1-' + time.strftime("%Y.%m.%d-%H.%M.%S") + '-' + 'log'
f_uart      = open( filename + ".csv ", mode = "w")
writer      =   csv.writer(f_uart)
writer.writerow(["timestamp","timenow","Time","Err_sram","Err_pllser","Err_pllsys",\
    "Err_plleth","Err_pll1","Err_pll2","Err_pllcas","Err_dff","Err_dffinv","Err_cpu","Reset_ALL"])


row_reg1    =   ["Time","Err_sram","Err_pllser","Err_pllsys","Err_plleth","Err_pll1"]
row_reg2    =   ["Err_pll2","Err_pllcas","Err_dff","Err_dffinv","Err_cpu","Reset_ALL"]

data = ["data"]


###############################################################################
#   Define functions :
###############################################################################

def bytes_to_int(recv_data):    # helper function
    int_num =   int.from_bytes(recv_data, byteorder='big', signed=False)
    return int_num

def user_read( addr ):
    read_signal         =   ( READ | addr )
    read_signal_byte    =   read_signal.to_bytes( 1, "big", signed=False )
    
    # fixme: what if after write, the connection shut down and resume again?
    flag_recv           =   0
    while(flag_recv==0):
        try:
            write_byte_width    =   ser.write( read_signal_byte )
            read_data           =   ser.read( READ_SIZE )

            # assert  write_byte_width    ==  1
            assert  len(read_data)      ==  4
            # assert  read_data  == 1
            flag_recv = 1

        except AssertionError:
            print('Something wrong during the read function of : %d. '%addr)
            print('Maybe timeout of read . ')
            time.sleep(1)
        except serial.SerialTimeoutException:
            time.sleep(1)
        except KeyboardInterrupt:
            print('Interruption Ctrl+C in read function . ')
            f_uart.close()
            exit()
        except :
            print('Unpredictable exception occurs in the user_read function !! ')
            time.sleep(1)

    data_int            =   bytes_to_int(read_data)
    # print( data_read )
    # print( struct.unpack( str(len(data_read)) + "s", data_read) )

    return data_int

def user_write():
    global write_occur
    while( True ):
        keyboard.wait('0')
        write_info()
    
def write_info():
    global write_occur
    write_occur =   1
    print('please input 0x and hex type address, then press ENTER : ',end='')
    addr_info_str   =   input()
    print('please input 0x and hex type data, then press ENTER : ',end='')
    data_info_str   =   input()

    try:
        assert len(addr_info_str) == 4
        assert len(data_info_str) == 4
    except AssertionError:
        print('Sorry. You have input incorrect bit number . ')
        print('Please input 0x and 2 bit hex information, try again . ')
        # write_info()
        time.sleep(1)
        write_occur =   0
        return 0

    addr_info_int   =   int( addr_info_str, 16 )
    addr_info_byte  =   addr_info_int.to_bytes( 1, "big", signed = False )

    data_info_int   =   int( data_info_str, 16 )
    data_info_byte  =   data_info_int.to_bytes( 1, "big", signed = False )

    ser.write(addr_info_byte)
    print('Address information has been sended ! ')
    ser.write(data_info_byte)
    print('Data information has been sended ! ')
    write_occur =   0
    
# exception serial.SerialException
# exception serial.SerialTimeoutException
#     Exception that is raised on write timeouts.

###############################################################################
#   MAIN
###############################################################################


link_down_count =   1
sock_flag       =   1
while(True):
    try: 
        assert (link_down_count < 5)
        client_uart1.connect((host, user_port))        # 连接端口
        link_down_count = 1
        break
    except OSError:
        print('Can not link socket server in %d times. Reconnect ...'%link_down_count)
        link_down_count += 1
        time.sleep(1)
    except AssertionError:
        print('Can not link socket server in 10 second.')
        xx = input('Press "e" to exit, "r" to retry, or other key to ignore and continue ... :')
        if( xx == 'e'):
            sock_flag   =   0
            exit()
        elif( xx == 'r'):
            link_down_count = 1
            continue
        else:
            sock_flag   =   0
            break

if __name__=='__main__':
    global write_occur

    # filename    =   time.strftime("%Y.%m.%d-%H.%M.%S") + '--' + 'log'
    # f_uart      =   open( 'Uart-' + filename + ".txt ", mode = "w")

    try:
        ser = serial.Serial( port, baudrate, timeout=user_timeout ) 
        ser.bytesize    =   8
        ser.open()
        print('COM is open .')
    except serial.SerialException:
        print('Can not found device, raise SerialException .')

    t_write = threading.Thread( target = user_write, daemon = True)
    t_write.start()

    try:
        write_occur =    0
        while(True):
                        
            if( write_occur == 0 ):
                print('read loop')
                # entering read loop
                data_tmp        =   []
                tb              =   PrettyTable()
                # fixme: time do not change
                tb.field_names  =   ["UART1",' ',"time",time.strftime("%H:%M:%S"),\
                    "timestamp",round(time.time(),4)]
                
                for reg in read_reg:
                    data_tmp.append( user_read( reg ) )

                    if(len(hex(reg)) < 4 ):
                        reg_name = hex(reg)[0:2] + '0' + hex(reg)[-1]
                    else:
                        reg_name = hex(reg)
                    print('Read %s reg done . '%reg_name )

                if ( sock_flag & (data_tmp[-1] == 1) ):
                    try:
                        warn_info = WARNING_ResetAll
                        print("Ready to send UART1 warning...")
                        client_uart1.send(warn_info)
                    except OSError:
                        print('Can not link socket server.')
                        sock_flag = 0
                        client_uart1.close()
                    except KeyboardInterrupt:
                        print('User have press Ctrl+C during uart1 loop .')
                        client_uart1.close()
                        f_uart.close()
                        ser.close()
                        exit()


                tb.add_row(row_reg1)
                row_data1    =    data_tmp[0:6]
                tb.add_row(row_data1)

                tb.add_row(row_reg2)
                row_data2    =    data_tmp[6:12]
                tb.add_row(row_data2)

                print(tb)

                writer.writerow( [round(time.time(),4),time.strftime("%H:%M:%S")] + data_tmp )

                data_tmp.clear()
                tb.clear()

                time.sleep( sleep_time )

            else:
                time.sleep( sleep_time )

    except KeyboardInterrupt:
        print('Interruption Ctrl+C in main thread, ready to exit . ')
        f_uart.close()
        ser.close()
        if sock_flag:
            client_uart1.close()
        else:
            pass
    except serial.SerialException:
        print('The link down during the loop! ')
    except serial.SerialTimeoutException:
        print('Exception of Timeout .')
    except :
        print('Unexpectable error happened ! ')
        f_uart.close()
        ser.close()
        if sock_flag:
            client_uart1.close()
        else:
            pass
        
    f_uart.close()
    ser.close()
    if sock_flag:
        client_uart1.close()
    else:
        pass