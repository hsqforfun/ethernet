import tkinter
import time
import socket
import threading
import tkinter.messagebox
# tkinter.messagebox.showwarning('warning!','Reset-all = 1')

###############################################################################
WARNING_ResetAll    =   b'\xa0'
WARNING_5BitError   =   b'\xa1'
WARNING_5PacketLose =   b'\xa2'

tk_server = socket.socket()         # 创建 socket 对象
host = socket.gethostname()         # 获取本地主机名
print(host)
port = 4877                         # 设置端口
tk_server.bind((host, port))        # 绑定端口

client_max          =   5
global event_list
event_list = []

###############################################################################

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
                    if(     event_list[0] == WARNING_ResetAll   ):
                        tkinter.messagebox.showwarning('Warning!','Reset-All = 1')
                        event_list.pop(0)
                        print('Check one warning .')
                        print('event_list is :',end='')
                        print(event_list)

                    elif(   event_list[0] == WARNING_5BitError  ):
                        tkinter.messagebox.showwarning('Warning!','Ethernet Transmition have 5 \
                            or more bit error !')
                        event_list.pop(0)
                        print('Check one warning .')
                        print('event_list is :',end='')
                        print(event_list)

                    elif(   event_list[0] == WARNING_5PacketLose):
                        tkinter.messagebox.showwarning('Warning!','Ethernet Transmition have 5 \
                            or more Packet miss !')
                        event_list.pop(0)
                        print('Check one warning .')
                        print('event_list is :',end='')
                        print(event_list)

                    else:
                        # receive wrong type data, delete it !
                        event_list.pop(0)
                        print('receive wrong type data, delete it automatically .')
                        print('event_list is :',end='')
                        print(event_list)
            except KeyboardInterrupt:
                print('User have press Ctrl+C during tk-check loop .')
                break

# def tk_check():
#     print('Start check thread ...')
#     global event_list
#     while(True):
#         try:
#             if( len(event_list) == 0 ):
#                 pass
#             else:
#                 if(     event_list[0] == WARNING_ResetAll   ):
#                     tkinter.messagebox.showwarning('Warning!','Reset-All = 1')
#                     event_list.pop(0)
#                     print('Check one warning .')
#                     print('event_list is :',end='')
#                     print(event_list)

#                 elif(   event_list[0] == WARNING_5BitError  ):
#                     tkinter.messagebox.showwarning('Warning!','Ethernet Transmition have 5 \
#                         or more bit error !')
#                     event_list.pop(0)
#                     print('Check one warning .')
#                     print('event_list is :',end='')
#                     print(event_list)

#                 elif(   event_list[0] == WARNING_5PacketLose):
#                     tkinter.messagebox.showwarning('Warning!','Ethernet Transmition have 5 \
#                         or more Packet miss !')
#                     event_list.pop(0)
#                     print('Check one warning .')
#                     print('event_list is :',end='')
#                     print(event_list)

#                 else:
#                     # receive wrong type data, delete it !
#                     event_list.pop(0)
#                     print('receive wrong type data, delete it automatically .')
#                     print('event_list is :',end='')
#                     print(event_list)
#         except KeyboardInterrupt:
#             print('User have press Ctrl+C during tk-check loop .')
#             break


class create_client (threading.Thread):
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
                if( (recv_data == b'\xa0') or (recv_data == b'\xa1') or (recv_data == b'\xa2') ):
                    event_list.append(recv_data) 
                    print('event_list is :',end='')
                    print(event_list)
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

# def create_client(i):
#     global event_list
#     flag = 0
#     # client = 'client' + str(i)
#     while True:
#         try:
#             print('Waiting client of thread %d...'%i)
#             client,addr = tk_server.accept()     # 建立客户端连接
#             if(client != None):    
#                 print('Client connected !')
#                 break
#             else:
#                 pass

#         except KeyboardInterrupt:
#             print('User have press Ctrl+C during client %d thread .'%i)
#             flag = 1
#             break

#     link_down_count = 1
#     while (flag == 0):
#         try:
#             assert (link_down_count < 5)
#             recv_data = client.recv(1)
#             if( (recv_data == b'\xa0') or (recv_data == b'\xa1') or (recv_data == b'\xa2') ):
#                 event_list.append(recv_data) 
#                 print('event_list is :',end='')
#                 print(event_list)
#             else:
#                 continue

#         except AssertionError:
#             print('Can not link socket server in 10 second, exit thread.')
#             client.close()
#             break

#         except OSError:
#             print('Can not link client in %d times. Reconnect ...'%link_down_count)
#             link_down_count += 1
#             time.sleep(1)
        
#         except KeyboardInterrupt:
#             print('User have press Ctrl+C during client %d thread .'%i)
#             client.close()
#             break
#             # raise KeyboardInterrupt
#     print('A client %d thread has done . '%i)
            
###############################################################################

try:
    tk_server.listen(client_max)                 # 等待客户端连接

    # t_check     =   threading.Thread( target=tk_check, daemon = True )
    # t_client_1  =   threading.Thread( target=create_client(1), daemon = True )
    # t_client_2  =   threading.Thread( target=create_client(2), daemon = True )
    # t_client_3  =   threading.Thread( target=create_client(3), daemon = True )
    # t_client_4  =   threading.Thread( target=create_client(4), daemon = True )
    # t_client_5  =   threading.Thread( target=create_client(5), daemon = True )

    t_check = tk_check()
    t_client_1 = create_client(1)
    t_client_2 = create_client(2)

    t_check.start()
    # time.sleep(1)
    t_client_1.start()
    t_client_2.start()
    # tk_check()
    # t_client_3.start()
    # t_client_4.start()
    # t_client_5.start()


    # t_check  =   threading.Thread( target=tk_check, daemon = True )
    # t_check.start()


    # client.close()                # 关闭连接
except KeyboardInterrupt:
    print('Main thread interrupt by Ctrl+C .')
    tk_server.close()