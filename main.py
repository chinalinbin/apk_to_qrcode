from tkinter import *
import tkinter.filedialog
import time
import socket
import os
import shutil
import threading
from urllib.parse import quote

import windnd
import qrcode
from flask import Flask,make_response,send_from_directory

app = Flask(__name__)
tk = Tk()
label_img = None

def get_host_ip(): 
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def dragged_files(files):
    msg = '\n'.join((item.decode('gbk') for item in files))
    #showinfo('file::',msg)
    gen_qrcode(msg)

def file_open():
    r = tkinter.filedialog.askopenfilename(title='上传文件',
                                           filetypes=[ ('All files', '*')])
    gen_qrcode(r)

def gen_qrcode(path):
    global label_img
    if not os.path.exists('img'):
        os.mkdir('img')
    if not os.path.exists('download'):
        os.mkdir('download')
    ts = str(int(time.time()*1000))
    filepath = 'download/'+ts+'.'+path.split('.')[-1]
    shutil.copy(path,filepath)
    img = qrcode.make("http://{}:5050/".format(get_host_ip())+filepath)
    img_path = 'img/'+ts+'.gif'
    img.save(img_path)
    img = PhotoImage(file=img_path)
    if not label_img:
        label_img = Label(tk, image = img)
        label_img.image = img
        label_img.pack()
        tk.update_idletasks()
    else:
        label_img.configure(image = img)
        label_img.image = img
        tk.update_idletasks()

def main():
    tk.title('文件二维码生成器')
    tk.geometry('400x400')
    b = Button(tk, text='打开文件',  command=file_open)
    b.pack()
    windnd.hook_dropfiles(tk,func=dragged_files)
    tk.mainloop()

@app.route("/", methods=['GET'])
def hello_world():
    return 'hello world'

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    response = make_response(send_from_directory('./download', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(quote(filename))
    return response

def flaskk():
    app.run(host='0.0.0.0',port= 5050)

if __name__ == '__main__':
    t = threading.Thread(target=flaskk,args=())
    t.setDaemon(True)
    t.start()
    main()