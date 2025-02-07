from flask import Flask, Response
from PIL import ImageGrab
import io
import time
from threading import Thread
import tkinter as tk
import subprocess



app = Flask(__name__)

# 初始化 BytesIO 对象
img_byte_arr = io.BytesIO()
def gen():
    while True:
        # 捕获屏幕
        screen = ImageGrab.grab()
        
        # 压缩图像质量和/或调整分辨率
        quality_level = compression_quality  # 图像质量，1 (worst) to 95 (best)，默认是 75
        size = (screen.width // 2, screen.height // 2)  # 可选：缩小图像尺寸的一半
        
        # 如果需要调整分辨率，取消下一行的注释
        # screen = screen.resize(size, Image.ANTIALIAS)
        
        # 清空 BytesIO 对象并保存图像为 JPEG 格式
        img_byte_arr.seek(0)  # 将指针移到开头
        img_byte_arr.truncate()  # 清空内容
        screen.save(img_byte_arr, format='JPEG', quality=quality_level)
        frame = img_byte_arr.getvalue()
        
        # 关闭图像对象，释放内存
        screen.close()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # 添加延时，限制帧率
        time.sleep(sleeptime)  # 每帧等待一段时间

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
        <html>
            <head>
                <style>
                    body, html {
                        margin: 0;
                        padding: 0;
                        width: 100%;
                        height: 100%;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    img {
                        max-width: 100%;  /* 最大宽度不超过容器 */
                        max-height: 100%; /* 最大高度不超过容器 */
                        object-fit: contain; /* 自动调整图像大小，保持宽高比 */
                    }
                </style>
            </head>
            <body>
                <img src="/video_feed" />
            </body>
        </html>
    '''





# 图形化设计

# 创建主窗口
root = tk.Tk()
root.title('ipv6投屏')
root.geometry('400x350')
root.resizable(False, False)

# 端口号输入框
ipport_var = tk.StringVar()
ipport_var.set('54250')

ipportlab = tk.Entry(root, textvariable=ipport_var, relief="sunken")
ipportlab.pack()
ipportlab.place(x=50, y=50, width=200, height=20)

# 帧率输入框
zhenlv_var = tk.StringVar()
zhenlv_var.set('30')

zhenlvlab = tk.Entry(root, textvariable=zhenlv_var, relief="sunken")
zhenlvlab.pack()
zhenlvlab.place(x=50, y=100, width=200, height=20)

# 图片质量输入框
quality_var = tk.StringVar()
quality_var.set('10')

qualitylab = tk.Entry(root, textvariable=quality_var, relief="sunken")
qualitylab.pack()
qualitylab.place(x=50, y=150, width=200, height=20)

# ipv4勾选框
ipv4_var = tk.BooleanVar()
ipv4_var.set(False)

ipv4_button = tk.Checkbutton(root, text="使用IPv4而非ipv6", variable=ipv4_var)
ipv4_button.pack()
ipv4_button.place(x=50, y=200)

# ipv6地址显示框
#调用cmd获取ipv6
def get_ipv6_address():
    try:
        # 调用ipconfig命令并获取其输出
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, check=True)
        
        # 解析输出
        lines = result.stdout.split('\n')
        ipv6_addresses = []
        
        for line in lines:
            if '临时 IPv6 地址' in line:
                # 提取IPv6地址，通常位于冒号分隔的字符串中
                address = line.split(': ')[-1].strip()
                if address:  # 去除可能的空字符串
                    ipv6_addresses.append(address)
        
        # 如果没有找到IPv6地址，返回回环地址
        if not ipv6_addresses:
            return '::1'
        
        # 通常情况下，我们只关心第一个IPv6地址（取决于实际需求）
        return ipv6_addresses[0]
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return '::1'

#调用cmd获取ipv4
def get_ipv4_address():
    try:
        # 调用ipconfig命令并获取其输出
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, check=True)
        
        # 解析输出
        lines = result.stdout.split('\n')
        ipv4_addresses = []
        
        for line in lines:
            if ('192.' in line) and ('IPv4 地址' in line):
                # 提取IPv4地址，通常位于冒号分隔的字符串中
                address = line.split(': ')[-1].strip()
                if address:  # 去除可能的空字符串
                    ipv4_addresses.append(address)
        
        # 如果没有找到IPv4地址，返回回环地址
        if not ipv4_addresses:
            return '127.0.0.1'
        
        # 通常情况下，我们只关心第一个IPv4地址（取决于实际需求）
        return ipv4_addresses[0]
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return '127.0.0.1'

ipv6_var = tk.StringVar()
ipv6lab = tk.Entry(root, textvariable=ipv6_var, state="readonly")
ipv6lab.pack()
ipv6lab.place(x=50, y=250, width=200, height=20)

# 增加一些描述
lab1 = tk.Label(root,text='端口号',relief='flat')
lab1.pack()
lab1.place(x=280, y=50)

lab2 = tk.Label(root,text='帧率(-1为不限制)',relief='flat')
lab2.pack()
lab2.place(x=280, y=100)

lab3 = tk.Label(root,text='压缩质量(1-100)',relief='flat')
lab3.pack()
lab3.place(x=280, y=150)

lab4 = tk.Label(root,text='访问地址',relief='flat')
lab4.pack()
lab4.place(x=280, y=250)

# 主按钮
qidong = False
def main():
    global qidong
    if not qidong:
        qidong = True
        # 处理各实时变量
        ipv4 = ipv4_var.get()
        ip = '::'
        if ipv4:
            ip = '0.0.0.0'

        ipport = int(ipport_var.get())
        
        global sleeptime
        frame_rate = int(zhenlv_var.get())  # 帧率 (fps)
        if frame_rate == -1:
            sleeptime = 0
        else:
            sleeptime = 1/frame_rate

        global compression_quality
        compression_quality = int(quality_var.get())  # 图像压缩质量 (1-100)
        compression_quality = round(95*compression_quality/100)
        
        if not ipv4:
            ipv6_var.set('http://[' + get_ipv6_address() + ']:' + ipport_var.get())
        else:
            ipv6_var.set('http://' + get_ipv4_address() + ':' + ipport_var.get())

        # 启动主程序
        def run_flask():
            app.run(host=ip, port=ipport, threaded=True)

        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True  # 设置为守护线程，确保主程序退出时子线程也会退出
        flask_thread.start()

# 定义按钮
buttonmain = tk.Button(root, text='开始投屏', command=main)
buttonmain.pack()
buttonmain.place(x=150, y=300, width=100, height=40)

# 运行应用程序
root.mainloop()
