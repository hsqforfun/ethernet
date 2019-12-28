import tkinter
import csv
import time
import socket
import threading
import tkinter.messagebox
# tkinter.messagebox.showwarning('warning!','Reset-all = 1')

###############################################################################
WARNING_ResetAll    =   b'\xa0'
WARNING_5BitError   =   b'\xa1'
WARNING_5PacketLose =   b'\xa2'

Warning_Type        =   b'\xa3'
Finish_Type         =   b'\xa4'
Error_Type          =   b'\xa5'
Config_Type         =   b'\xa6'


WARNING_LIST        =   {WARNING_ResetAll:'UART Reset All happened !! ',\
     WARNING_5BitError:'Ethernet have 5 or more bit error !! ',\
          WARNING_5PacketLose:'Ethernet have 5 or more packet loss !! ',\
              Warning_Type:'SRAM--Warning ! ',\
                  Finish_Type:'SRAM--Finish !',\
                      Error_Type:'SRAM--Error !',\
                          Config_Type:'SRAM--Config !'} 

tk_server = socket.socket()         # 创建 socket 对象
host = socket.gethostname()         # 获取本地主机名
print(host)
port = 4877                         # 设置端口
tk_server.bind((host, port))        # 绑定端口

client_max          =   5

global event_list
event_list = []
tab8                =   '        '
###############################################################################

def show_list():
    if( len(event_list) == 0 ):
        print(tab8 + 'None')
    else:
        for i in range( len(event_list) ):
            print( tab8 + WARNING_LIST.get(event_list[i]) )
    print('.')

class tk_check (threading.Thread):
    # def __init__(self, threadID):
    #     threading.Thread.__init__(self)
    #     self.threadID = threadID
    def run(self):
        print('Start check thread ...')
        global event_list
        while(True):
            try:
                if( len(event_list) == 0 ):
                    pass
                else:
                    if(     event_list[0] in WARNING_LIST   ):
                        tkinter.messagebox.showwarning('Warning!',WARNING_LIST.get(event_list[0]) )
                        event_list.pop(0)
                        # print('User have checked one warning .')
                        print('')
                        print('User have checked one warning.')
                        print('Warning list :')
                        show_list()

                    else:
                        event_list.pop(0)
                        # print('Receive wrong type data, delete it automatically .')
                        print('Automatically delete one warning')
                        print('Warning list :')
                        show_list()

            except KeyboardInterrupt:
                print('User have press Ctrl+C during tk-check loop .')
                break

class create_client (threading.Thread):
    global writer
    def __init__(self, counter):
        threading.Thread.__init__(self)
        self.counter = counter
    def run(self):
        i = self.counter
        global event_list
        flag = 0
        # client = 'client' + str(i)
        while True:
            try:
                print('Waiting client of thread %d...'%i)
                client,addr = tk_server.accept()     # 建立客户端连接
                if(client != None):    
                    print('Client connected !')
                    break
                else:
                    pass

            except KeyboardInterrupt:
                print('User have press Ctrl+C during client %d thread .'%i)
                flag = 1
                break

        link_down_count = 1
        while (flag == 0):
            try:
                assert (link_down_count < 5)
                recv_data = client.recv(1)
                if( recv_data in WARNING_LIST ):
                    event_list.append(recv_data) 

                    warn_time   =   time.time()
                    time_str    =   time.strftime("%H:%M:%S")
                    writer.writerow([warn_time,time_str,WARNING_LIST.get(recv_data)])
                    print()
                    print('Warning list :')
                    show_list()
                else:
                    continue

            except AssertionError:
                print('Can not link socket server in 10 second, exit thread.')
                client.close()
                break

            except OSError:
                print('Can not link client in %d times. Reconnect ...'%link_down_count)
                link_down_count += 1
                time.sleep(1)
            
            except KeyboardInterrupt:
                print('User have press Ctrl+C during client %d thread .'%i)
                client.close()
                break
                # raise KeyboardInterrupt
        print('A client %d thread has done . '%i)

            
###############################################################################
#   main
###############################################################################
global f_warning
global writer
filename    =   'Warning-' + time.strftime("%H.%M.%S") + '-log'
f_warning   =   open( filename + ".csv ", mode = "w")
writer      =   csv.writer(f_warning)

writer.writerow(['timestamp','time','warning_infomation'])

try:
    tk_server.listen(client_max)                 # 等待客户端连接

    # t_check     =   threading.Thread( target=tk_check, daemon = True )
    # t_client_1  =   threading.Thread( target=create_client(1), daemon = True )
    # t_client_2  =   threading.Thread( target=create_client(2), daemon = True )
    # t_client_3  =   threading.Thread( target=create_client(3), daemon = True )
    # t_client_4  =   threading.Thread( target=create_client(4), daemon = True )
    # t_client_5  =   threading.Thread( target=create_client(5), daemon = True )

    t_check = tk_check()
    t_check.setDaemon(True)

    t_client_1 = create_client(1)
    t_client_1.setDaemon(True)

    t_client_2 = create_client(2)
    t_client_2.setDaemon(True)

    t_check.start()
    t_client_1.start()
    t_client_2.start()
    # t_client_3.start()
    # t_client_4.start()
    # t_client_5.start()
    while True:
        pass
    # client.close()                # 关闭连接
except KeyboardInterrupt:
    print('Main thread interrupt by Ctrl+C .')
    tk_server.close()
    f_warning.close()
    exit()