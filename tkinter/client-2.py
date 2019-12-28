import tkinter
import time
import socket

import tkinter.messagebox
# tkinter.messagebox.showwarning('warning!','Reset-all = 1')

client_demo = socket.socket()         # 创建 socket 对象
host = socket.gethostname()         # 获取本地主机名
print(host)
port = 4877                         # 设置端口

link_down_count = 1
while(True):
    try: 
        assert (link_down_count < 5)
        client_demo.connect((host, port))        # 连接端口
        link_down_count = 1
        break
    except OSError:
        print('Can not link socket server in %d times. Reconnect ...'%link_down_count)
        link_down_count += 1
        time.sleep(1)
    except AssertionError:
        print('Can not link socket server in 10 second, exit .')
        exit()
        
while True:
    try:
        a = b'\xa1' + b'\x00' + b'\xa1' + b'\x00'
        print("Ready to send ...")
        client_demo.send(a)
        time.sleep(10)
    except OSError:
        print('Can not link socket server, retry again .')
        time.sleep(1)
        try:
            client_demo.connect((host, port))
        except:
            print('Link down. Exit')
            exit()
    except KeyboardInterrupt:
        print('User have press Ctrl+C during tk-client loop .')
        client_demo.close()
        exit()

client_demo.close()                # 关闭连接
