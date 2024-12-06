import pyautogui
import time
import tkinter as tk
from pynput import mouse
import keyboard

clicked1 = 0
#nopage = 1      #起始页号
# Using input()
Totalpage = input("输入总页数: ")
nopage = input("输入第一页编号: ")      #起始页号
PDF_AutoOpen = 0
#Totalpage = 38   #共26页

# 激活CAD窗口
PositionX1 = 176
PositionY1 = 407

# 移动到“名称”并点击
PositionX2 = 825
PositionY2 = 377

# 选择上一次打印并点击
PositionX3 = 801
PositionY3 = 408

# “选择打印区域”
PositionX4 = 875
PositionY4 = 650

# 点击确定按钮
PositionX5 = 1161
PositionY5 = 779

# “选择打印区域”
PositionX6 = 1267
PositionY6 = 715

for i in range(1,int(Totalpage)+1):
    # 激活CAD窗口
    pyautogui.moveTo(PositionX1, PositionY1, duration=0.25)
    time.sleep(0.15)  # Number of seconds
    pyautogui.click(PositionX1, PositionY1)
    time.sleep(0.35)  # Number of seconds

    pyautogui.hotkey('ctrl', 'p')
    time.sleep(0.5)  # Number of seconds
    # 移动到“名称”并点击
    pyautogui.moveTo(PositionX2, PositionY2, duration=0.25)
    time.sleep(0.15)  # Number of seconds
    pyautogui.click(PositionX2, PositionY2)


    pyautogui.moveTo(PositionX3, PositionY3, duration=0.25)
    time.sleep(0.15)  # Number of seconds
    # 选择上一次打印并点击
    pyautogui.click(PositionX3, PositionY3)

    pyautogui.moveTo(PositionX4, PositionY4, duration=0.5)
    time.sleep(0.15)  # Number3
    # of seconds
    # “选择打印区域”
    pyautogui.click(PositionX4, PositionY4)

    def on_click(x, y, button, pressed):
        global clicked1
        if button == mouse.Button.left:
            if pressed:
                clicked1 = clicked1 + 1
                print(f"Left click detected at position: ({x}, {y})")
                time.sleep(0.85)
                if clicked1 >= 2: #框选图形范围，需要鼠标点两次
                    return False

    def create_pynput_listener():
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()


    create_pynput_listener()

    if clicked1 >= 2:
        clicked1 = 0
        pyautogui.moveTo(PositionX5, PositionY5, duration=0.5)
        time.sleep(0.15)  # Number of seconds
        # 点击确定按钮
        pyautogui.click(PositionX5, PositionY5)

        pyautogui.moveTo(PositionX6, PositionY6, duration=0.5)
        time.sleep(0.15)  # Number of seconds
        # 移动到文件名
        pyautogui.click(PositionX6, PositionY6)
        time.sleep(0.5)  # Number of seconds

        # pyautogui.click()
        # pyautogui.PAUSE = 0.5
        keyboard.press_and_release('backspace')
        # pyautogui.press('delete')
        #print("1")
        time.sleep(0.35)  # Number of seconds
        # keyboard.press_and_release('backspace')
        # pyautogui.PAUSE = 0.5
        # pyautogui.press('delete')
        #print("2")
        # time.sleep(1.35)  # Number of seconds
        # pyautogui.keyDown('delete')
        # time.sleep(3.3)
        # pyautogui.keyUp('delete')
        # pyautogui.hotkey('delete')
        # time.sleep(1)
        # pyautogui.hotkey('delete')
        # time.sleep(1)
        # global nopage
        pyautogui.typewrite(str(nopage), interval=0.025)
        pyautogui.press('enter')
        time.sleep(0.35)

        if PDF_AutoOpen == 1 :
            # 等待输入回车
            print('PDF打印完成后请输入回车键')
            keyboard.wait('enter')
            #time.sleep(4.3)  # Number of seconds
            pyautogui.moveTo(1895, 10, duration=0.5)
            time.sleep(0.15)  # Number of seconds
            pyautogui.click(1895, 10)
        else:
            time.sleep(1)

        print("第" + str(nopage) + "页，打印完成")

        if i == int(Totalpage)-1 :
            print("\n所有内容打印完成")
        nopage = int(nopage) + 1