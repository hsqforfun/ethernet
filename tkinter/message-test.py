import tkinter
import time
import tkinter.messagebox

# tkinter.messagebox.showwarning('warning!','Reset-all = 1')

flag = 0
count = 0
while(True):

    if(count>=5):
        flag = 0
        count = 0

    print('666')
    time.sleep(1.0)

    if (flag == 0):
        # tkinter.messagebox.showwarning('warning!','Reset-all = 1')
        
        # warn    =   tkinter.messagebox.showinfo('warning!','Reset-all = 1')
        # print(warn)
        flag = 1
    else:
        pass 

    count += 1