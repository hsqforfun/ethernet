import time
import socket

client_demo = socket.socket()         # 创建 socket 对象
host = socket.gethostname()         # 获取本地主机名
print(host)
port = 4877                         # 设置端口

WARNING_TYPE    =   b'\xa3'

link_down_count =   1

sock_flag       =   1
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
        print('Can not link socket server in 10 second.')
        xx = input('Press "e" to exit or other key to ignore and continue ... :')
        if( xx == 'e'):
            sock_flag   =   0
            exit()
        else:
            sock_flag   =   0
            break
        
while sock_flag:
    try:
        a = WARNING_TYPE
        print("Ready to send ...")
        client_demo.send(a)
        time.sleep(6)
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

print('done .')
client_demo.close()                # 关闭连接
