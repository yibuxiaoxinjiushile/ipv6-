from flask import Flask, Response, request, jsonify
from PIL import ImageGrab
import io
import time
from threading import Thread, Lock
import tkinter as tk
import subprocess
import pyautogui

app = Flask(__name__)

# 全局变量
img_byte_arr = io.BytesIO()
sleeptime = 0.033
compression_quality = 10
enable_simulation = False
screen_width, screen_height = pyautogui.size()
lock = Lock()

def gen():
    while True:
        with lock:
            screen = ImageGrab.grab()
            img_byte_arr.seek(0)
            img_byte_arr.truncate()
            screen.save(img_byte_arr, format='JPEG', quality=compression_quality)
            frame = img_byte_arr.getvalue()
            screen.close()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(sleeptime)

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/click', methods=['POST'])
def handle_click():
    if not enable_simulation:
        return jsonify(status='disabled')
    
    data = request.json
    x_percent = data['x']  # 接收百分比坐标
    y_percent = data['y']
    button = data.get('button', 'left')

    # 将百分比转换为实际坐标
    actual_x = int((x_percent / 100) * screen_width)
    actual_y = int((y_percent / 100) * screen_height)

    if button == 'right':
        pyautogui.rightClick(actual_x, actual_y)
    else:
        pyautogui.click(actual_x, actual_y)
    
    return jsonify(status='success')

@app.route('/keypress', methods=['POST'])
def handle_keypress():
    if not enable_simulation:
        return jsonify(status='disabled')
    
    data = request.json
    key = data['key']
    pyautogui.press(key)
    return jsonify(status='success')

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
                    }
                    #click-area {
                        flex-grow: 1;
                        border: 1px solid black;
                        position: relative;
                        overflow: hidden;
                    }
                    img {
                        width: 100%;
                        height: 100%;
                        object-fit: contain;
                    }
                </style>
            </head>
            <body>
                <div id="click-area">
                    <img src="/video_feed" />
                </div>
                <script>
                    const clickArea = document.getElementById('click-area');

                    clickArea.addEventListener('contextmenu', (event) => {
                        event.preventDefault();
                    });

                    clickArea.addEventListener('mousedown', (event) => {
                        const img = document.querySelector('img');
                        const rect = img.getBoundingClientRect(); // 获取 img 在页面的渲染尺寸

                        const naturalWidth = img.naturalWidth;  // 图片原始宽度
                        const naturalHeight = img.naturalHeight; // 图片原始高度
                        const displayWidth = rect.width;  // 图片在页面上的渲染宽度
                        const displayHeight = rect.height; // 图片在页面上的渲染高度

                        // 计算图片在浏览器中的实际显示区域（去除黑边）
                        const imgAspectRatio = naturalWidth / naturalHeight;
                        const displayAspectRatio = displayWidth / displayHeight;

                        let renderWidth, renderHeight, offsetX, offsetY;

                        if (displayAspectRatio > imgAspectRatio) {
                            // 窗口宽高比 > 图片宽高比 -> 上下有黑边
                            renderHeight = displayHeight;
                            renderWidth = renderHeight * imgAspectRatio;
                            offsetX = (displayWidth - renderWidth) / 2; // 左右黑边宽度
                            offsetY = 0;
                        } else {
                            // 窗口宽高比 <= 图片宽高比 -> 左右有黑边
                            renderWidth = displayWidth;
                            renderHeight = renderWidth / imgAspectRatio;
                            offsetX = 0;
                            offsetY = (displayHeight - renderHeight) / 2; // 上下黑边高度
                        }

                        // 获取点击坐标（去除黑边）
                        const clickX = event.clientX - rect.left - offsetX;
                        const clickY = event.clientY - rect.top - offsetY;

                        // 计算相对于实际图片区域的百分比
                        if (clickX < 0 || clickX > renderWidth || clickY < 0 || clickY > renderHeight) {
                            return; // 点击在黑边上，忽略
                        }

                        const xPercent = (clickX / renderWidth) * 100;
                        const yPercent = (clickY / renderHeight) * 100;

                        const button = event.button === 2 ? 'right' : 'left';

                        fetch('/click', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ x: xPercent, y: yPercent, button }),
                        });
                    });
                    
                    document.addEventListener('keydown', (event) => {
                        const key = event.key;
                        fetch('/keypress', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ key }),
                        });
                    });

                    // 窗口大小变化时重置点击区域
                    window.addEventListener('resize', () => {
                        const img = document.querySelector('img');
                        if (img) {
                            img.style.width = '100%';
                            img.style.height = '100%';
                        }
                    });
                </script>
            </body>
        </html>
    '''

# 图形化设计
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
lab1 = tk.Label(root, text='端口号', relief='flat')
lab1.pack()
lab1.place(x=280, y=50)

lab2 = tk.Label(root, text='帧率(-1为不限制)', relief='flat')
lab2.pack()
lab2.place(x=280, y=100)

lab3 = tk.Label(root, text='压缩质量(1-100)', relief='flat')
lab3.pack()
lab3.place(x=280, y=150)

lab4 = tk.Label(root, text='访问地址', relief='flat')
lab4.pack()
lab4.place(x=280, y=250)

# 模拟功能开关
simulation_var = tk.BooleanVar()
simulation_var.set(False)
simulation_button = tk.Checkbutton(root, text="远程控制", variable=simulation_var)
simulation_button.pack()
simulation_button.place(x=220, y=200)

# 主按钮
qidong = False
def main():
    global qidong, sleeptime, compression_quality, enable_simulation
    if not qidong:
        qidong = True
        # 处理各实时变量
        ipv4 = ipv4_var.get()
        ip = '::'
        if ipv4:
            ip = '0.0.0.0'

        ipport = int(ipport_var.get())
        
        frame_rate = int(zhenlv_var.get())  # 帧率 (fps)
        if frame_rate == -1:
            sleeptime = 0
        else:
            sleeptime = 1 / frame_rate

        compression_quality = int(quality_var.get())  # 图像压缩质量 (1-100)
        compression_quality = round(95 * compression_quality / 100)
        
        enable_simulation = simulation_var.get()  # 是否启用模拟功能
        
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
