###############################################################################
#   aim at adding buttons to manipulate UART
###############################################################################

import tkinter
import csv
import time
import socket
import threading
import tkinter.messagebox

from tkinter import *


###############################################################################
def hello():
    print('Hello!')

def show_list():
    if( len(event_list) == 0 ):
        print(tab8 + 'None')
    else:
        for i in range( len(event_list) ):
            print( tab8 + WARNING_LIST.get(event_list[i]) )
    print('.')

class tk_main(threading.Thread):
    def run(self):
        global top
        top = Tk()
        top.title("tk main window")

        screenwidth     =   root.winfo_screenwidth() 
        screenheight    =   root.winfo_screenheight()
        tk_width        =   int(screenwidth/10)
        tk_height       =   int(screenheight/10)   
        root.geometry('{}x{}+{}+{}'.format(tk_width,tk_height, 100, 100)) 
        # top.geometry("100x100")
        button1=Button(top,text='say hello!',command=hello)
        button1.pack()
        # button2=Button(top,text='click me!',command=hello,relief=GROOVE)
        # button2.pack()
        top.mainloop()
        
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
    global f_warning
    def __init__(self, counter):
        threading.Thread.__init__(self)
        self.counter = counter
    def run(self):
        i = self.counter
        global event_list
        flag = 0
        link = 0
        flag_run = 1

        while (flag_run):
            # link to a client
            while (link == 0):
                try:
                    print('Waiting client of thread %d...'%i)
                    client,addr = tk_server.accept()            
                    if(client != None):    
                        print('Client connected !')
                        break
                    else:
                        pass

                except KeyboardInterrupt:
                    print('User have press Ctrl+C during client %d thread .'%i)
                    flag = 1
                    flag_run = 0
                    break

            # receive warning bytes
            link_down_count = 1
            while (flag == 0):
                try:
                    assert (link_down_count < 5)
                    recv_data = client.recv(1)
                    
                    # check if connection failed 
                    if(recv_data == b''):
                        link = 0
                        print('Previous connection failed, try again .')
                        break
                    else:
                        pass

                    if( recv_data in WARNING_LIST ):
                        event_list.append(recv_data) 

                        warn_time   =   time.time()
                        time_str    =   time.strftime("%H:%M:%S")
                        writer.writerow([warn_time,time_str,WARNING_LIST.get(recv_data)])
                        f_warning.flush()
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
                    flag_run = 0
                    break
                    # raise KeyboardInterrupt
        print('A client %d thread has done . '%i)


###############################################################################

# ethernet warning 
WARNING_5BitError   =   b'\xa1'
WARNING_5PacketLose =   b'\xa2'

# sram warning
Warning_Type        =   b'\xa3'
Finish_Type         =   b'\xa4'
Error_Type          =   b'\xa5'
Config_Type         =   b'\xa6'

# control board warning
WARNING_ResetAll_CtrlBoard  =   b'\xaa'

# test board warning 
WARNING_ResetAll_TestBoard  =   b'\xab'
WARNING_ResetAll_0          =   b'\xa7'
WARNING_ResetAll_1          =   b'\xa8'
WARNING_ResetAll_2          =   b'\xa9'
WARNING_ResetAll_3          =   b'\xac'
WARNING_ResetAll_4          =   b'\xad'
WARNING_DFF                 =   b'\xae'             

tab8                =   '        ' 
client_max          =   4       # ctrlboard testboard sram ethernet

global event_list
event_list = []

WARNING_LIST        =   {WARNING_5BitError:'Ethernet have 5 or more bit error !! ',\
    WARNING_5PacketLose:'Ethernet continuously lose 5 or more packet !! ',\
        Warning_Type:'SRAM--Warning ! ',\
            Finish_Type:'SRAM--Finish !',\
                Error_Type:'SRAM--Error !',\
                    Config_Type:'SRAM--Config !',\
                        WARNING_ResetAll_CtrlBoard:'CtrlBoard-ResetAll !',\
                            WARNING_ResetAll_TestBoard:'TestBoard-ResetAll !'} 


###############################################################################
#   Socket
###############################################################################

host = socket.gethostname()       
tk_port     =   4877  

tk_server   =   socket.socket()        
tk_server.bind((host, tk_port))       

# now do not consider button function, fix other error first
# button_port =   4478
# tk_button   =   socket.socket()  
# Button_clr  =   b'\x98\x80'

###############################################################################
#   main
###############################################################################
global f_warning
global writer
filename    =   'Warning-' + time.strftime("%H.%M.%S") + '-log'
f_warning   =   open( filename + ".csv", mode = "w")
writer      =   csv.writer(f_warning)

writer.writerow(['timestamp','time','warning_infomation'])
f_warning.flush()

try:
    tk_server.listen(client_max)                 # wait for client connect

    t_tk = tk_main()
    t_tk.setDaemon(True)
    t_check = tk_check()
    t_check.setDaemon(True)

    t_client_1 = create_client(1)
    t_client_1.setDaemon(True)

    t_client_2 = create_client(2)
    t_client_2.setDaemon(True)

    t_client_3 = create_client(2)
    t_client_3.setDaemon(True)

    t_client_4 = create_client(2)
    t_client_4.setDaemon(True)

    t_tk.start()
    t_check.start()
    t_client_1.start()
    t_client_2.start()
    t_client_3.start()
    t_client_4.start()

    while True:
        pass
    # client.close()                
except KeyboardInterrupt:
    print('Main thread interrupt by Ctrl+C .')
    tk_server.close()
    f_warning.close()
    exit()