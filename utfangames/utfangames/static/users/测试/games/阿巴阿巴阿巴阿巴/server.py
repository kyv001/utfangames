import socket
import sys
import tkinter as tk
from threading import Thread

lawyer = socket.gethostname()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((lawyer, 3001))
s.listen(5)
g_conn = []


def con():
    while 1:
        cs, addr = s.accept()
        print("{} is connecting".format(str(addr)))
        g_conn.append(cs)
        tl = Thread(target=recv, args=(cs,))
        tl.start()


def recv(cs):
    while 1:
        txt = cs.recv(1024).decode()
        for i in g_conn:
            if i != cs:
                i.sendall(txt.encode())

        lb.insert("end", ":".join(map(str, cs.getsockname())) + "：" + txt)


def del_window():
    root.destroy()
    sys.exit(0)


def send():
    for i in g_conn:
        i.sendall(send_box.get().encode())
    lb.insert("end", "我：" + send_box.get())
    send_box.delete("0","end")


root = tk.Tk()
root.config(bg="red")
lb = tk.Listbox(root, width=100, height=30)
lb.pack(padx=5, pady=5)
send_box = tk.Entry(root, width=90)
send_box.pack(pady=5, padx=5, side="left")
send_button = tk.Button(root,text="发送",width=8,command=send)
send_button.pack(padx=5, pady=5, side="right")
Thread(target=con).start()
root.mainloop()
