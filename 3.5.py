import subprocess  # 增加这一行导入subprocess模块
import sys
from pynput import mouse
import tkinter as tk
import _tkinter
import pyautogui
import time
import keyboard
import os
import threading

try:
    from pynput import mouse
except ImportError:
    # 尝试安装pynput
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    # 安装后尝试再次导入，这次应该不会失败
    from pynput import mouse


class AutoCADPrintSelector:
    def __init__(self, root, click_times=10):
        self.root = root
        root.title("AutoCAD打印选择器")
        root.geometry("500x700")

        # Variables
        self.PrePrint_var = tk.BooleanVar()
        self.PDF_AutoOpen = tk.IntVar(value=0)
        self.PrePrintAutoOpen_var = tk.StringVar(value="否")  # Changed default to "否"
        self.total_number_var = tk.IntVar(value=1)
        self.start_number_var = tk.IntVar(value=1)
        self.click_times = click_times

        # Current state for visualization
        self.current_state = 0
        self.ClickedTimes = 1
        self.arr = {}

        # Frame for state visualization
        self.state_frame = tk.Frame(self.root)
        self.state_frame.grid(row=5, column=0, columnspan=3, padx=5, pady=5)
        # Create UI Components
        self.create_components()

        self.lock = threading.Lock()
        # 添加这些新属性
        self.clicked1 = 0
        self.nopage = 1  # 默认起始页号
        self.Totalpage = 0
        #self.PDF_AutoOpen = 0
        self.positions = {
            'activate_cad': (176, 407),
            'name_click': (825, 377),
            'last_print_click': (801, 408),
            'select_print_area': (875, 650),
            'ok_button': (1161, 779),
            'file_name_click': (1267, 715)
        }

        self.calibrating = False
        self.loading = False
        self.printing = False
        self.lock_gui_elements()

    def create_components(self):
        # PrePrint Checkbox
        self.create_state_visualization()

        PrePrint = tk.Checkbutton(
            self.root,
            text="已预打印一份CAD？",
            variable=self.PrePrint_var,
            command=self.checkpreprint_status
        )
        PrePrint.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        # Auto Open Radio Buttons
        label = tk.Label(self.root, text="CAD打印后PDF会自动打开？", anchor='w')
        label.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        PrePrintAutoOpen = tk.Radiobutton(
            self.root,
            text="是",
            value=1,
            variable=self.PDF_AutoOpen,
            command=self.checkpreprintautoopen_status
        )
        PrePrintAutoOpen.grid(row=1, column=1, sticky='e', padx=10, pady=10)

        PrePrintAutoClose = tk.Radiobutton(
            self.root,
            text="否",
            value=0,
            variable=self.PDF_AutoOpen,
            command=self.checkpreprintautoopen_status
        )
        PrePrintAutoClose.grid(row=1, column=2, sticky='e', padx=10, pady=10)

        # Total Number of PDFs
        label2 = tk.Label(self.root, text="本次共需要打印", anchor='w')
        label2.grid(row=2, column=0, sticky='ew', padx=10, pady=10)

        total_number_spinbox = tk.Spinbox(
            self.root,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.total_number_var,
            width=10
        )
        total_number_spinbox.grid(row=2, column=1, sticky='ew', padx=10, pady=10)

        label3 = tk.Label(self.root, text="份PDF", anchor='w')
        label3.grid(row=2, column=2, sticky='ew', padx=10, pady=10)

        # Start Number
        label4 = tk.Label(self.root, text="首页PDF起始编号：", anchor='w')
        label4.grid(row=3, column=0, sticky='ew', padx=10, pady=10)

        start_number_spinbox = tk.Spinbox(
            self.root,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.start_number_var,
            width=10
        )
        start_number_spinbox.grid(row=3, column=1, sticky='ew', padx=10, pady=10)

        # Configure grid to expand
        self.root.grid_columnconfigure(0, weight=1)

        # State Visualization
        self.create_state_visualization()

        # Add the new button frame at the bottom
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=7, column=0, columnspan=3, pady=10)  # Adjust row to place below existing controls

        # 创建按钮框架
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=7, column=0, columnspan=3, pady=10)

        # 按钮
        self.calibrate_button = tk.Button(self.button_frame, text="标定位置", command=self.start_calibration)
        self.calibrate_button.pack(side=tk.LEFT, padx=5)
        self.load_button = tk.Button(self.button_frame, text="载入位置", command=self.load_position)
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.print_button = tk.Button(self.button_frame, text="开始打印", command=self.start_print)
        self.print_button.pack(side=tk.LEFT, padx=5)
        #for text, script in buttons:
        #    btn = tk.Button(self.button_frame, text=text, command=lambda s=script: self.run_script(s))
        #    btn.pack(side=tk.LEFT, padx=5)

        # 添加获取打印页数和起始页的输入框
        #tk.Label(self.root, text="总页数:").grid(row=8, column=0, sticky='e', padx=10, pady=10)
        #tk.Entry(self.root, textvariable=self.total_number_var).grid(row=8, column=1, sticky='w', padx=10, pady=10)

        #tk.Label(self.root, text="起始页编号:").grid(row=9, column=0, sticky='e', padx=10, pady=10)
        #tk.Entry(self.root, textvariable=self.start_number_var).grid(row=9, column=1, sticky='w', padx=10, pady=10)

    def lock_gui_elements(self):
        for widget in [self.PrePrint_var, self.PrePrintAutoOpen_var, self.total_number_var, self.start_number_var]:
            if isinstance(widget, tk.BooleanVar):
                widget.trace_add('write', self.lock_controls)
            else:
                widget.trace_add('write', self.lock_controls)
        self.lock_buttons()

    def lock_controls(self, *args):
        # 确保在任何操作中，控件都是禁用的
        if self.calibrating or self.loading or self.printing:
            self.PrePrint_var.set(False)
            self.PrePrintAutoOpen_var.set("否")
            self.total_number_var.set(1)
            self.start_number_var.set(1)
        # 这个方法不会直接禁用控件，因为trace机制会在值改变时被调用

    def lock_buttons(self):
        # 禁用或启用按钮
        state = tk.DISABLED if self.calibrating or self.loading or self.printing else tk.NORMAL
        self.calibrate_button.config(state=state)
        self.load_button.config(state=state)
        self.print_button.config(state=state)

    def run_scr1pt(self, script_name):
        """运行指定的Python脚本"""
        try:
            subprocess.run(["python", script_name])
        except Exception as e:
            print(f"脚本运行失败: {e}")

    def create_state_visualization(self):
        # Clear existing widgets
        for widget in self.state_frame.winfo_children():
            widget.destroy()

        label5 = tk.Label(self.root, text="标定流程及打印流程：", anchor='w')
        label5.grid(row=4, column=0, sticky='ew', padx=10, pady=10)

        # State Descriptions
        self.state_descriptions = [
            "激活窗口", "Ctrl+P", "点选选择", "点选上一次", "点选窗口",
            "点选左上角", "点选右下角", "确定", "点选更改名字窗口", "确定"
        ]

        # Clean up previous widgets
        for widget in self.state_frame.winfo_children():
            widget.destroy()

        self.squares = []
        self.labels = []
        for i in range(self.click_times):
            # Square
            square = tk.Canvas(self.state_frame, width=20, height=20,
                               bg='gray', highlightthickness=1, highlightbackground='black')
            square.grid(row=i, column=0, padx=5, pady=5)
            self.squares.append(square)

            # Label, now using the correct description
            description = self.state_descriptions[i] if i < len(self.state_descriptions) else "关闭PDF"
            label = tk.Label(self.state_frame, text=description, font=('Arial', 10))
            label.grid(row=i, column=1, sticky='w', padx=5, pady=5)
            self.labels.append(label)

        # Create state control buttons if not already created
        if not hasattr(self, 'button_frame'):
            self.create_state_control_buttons()

    def create_state_control_buttons(self):
        # Button frame
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=6, column=0, columnspan=3, pady=10)

        # Next State Button
        next_button = tk.Button(self.button_frame, text="下一状态", command=self.change_state)
        next_button.pack(side=tk.LEFT, padx=5)

        # Reset Button
        reset_button = tk.Button(self.button_frame, text="重置", command=self.reset_state)
        reset_button.pack(side=tk.LEFT, padx=5)

    def checkpreprint_status(self):
        if self.calibrating: return  # 如果正在标定，则不做任何改变
        print(f"预打印状态: {'已预打印' if self.PrePrint_var.get() else '未预打印'}")
    def start_calibration(self):
        if not self.calibrating:
            self.calibrating = True
            self.lock_gui_elements()
            # Disable UI interactions
            self.PrePrint_var.set(False)
            if not self.PrePrint_var.trace_info():
                self.PrePrint_var.trace_add('write', lambda *args: self.disable_controls())
            self.PrePrintAutoOpen_var.set("否")
            if not self.PrePrintAutoOpen_var.trace_info():
                self.PrePrintAutoOpen_var.trace_add('write', lambda *args: self.disable_controls())
            self.calibrate_button.config(state=tk.DISABLED)
            self.calibrating = True
            self.ClickedTimes = 1
            self.arr = {}

            # Start calibration in a new thread
            self.listener_thread = threading.Thread(target=self.create_pynput_listener, daemon=True)
            self.listener_thread.start()
            self.calibrating = False
            self.end_operation('loading')

    def end_calibration(self):
        # Reset UI interactions
        try:
            #self.PrePrint_var.trace_remove('write', self.PrePrint_var.trace_info()[-1])
            traces = self.PrePrint_var.trace_info()
            if traces:
                cbname = traces[-1][-1]  # 如果trace_info返回的是一个元组列表，取最后一个元组的最后一个元素作为回调名
                self.PrePrint_var.trace_remove('write', cbname)
            else:
                # 如果没有找到trace，直接pass或者进行其他处理
                pass
        except tk.TclError:
            pass  # 如果trace已经不存在，那么忽略此异常
        try:
            #self.PrePrintAutoOpen_var.trace_remove('write', self.PrePrintAutoOpen_var.trace_info()[-1])
            # 对PrePrintAutoOpen_var做同样处理
            traces = self.PrePrintAutoOpen_var.trace_info()
            if traces:
                cbname = traces[-1][-1]  # 假设回调名是元组的最后一个元素
                self.PrePrintAutoOpen_var.trace_remove('write', cbname)
        except tk.TclError:
            pass  # 同样，如果trace已经不存在，那么忽略此异常
        self.calibrate_button.config(state=tk.NORMAL)
        self.calibrating = False

    def checkpreprintautoopen_status(self):
        try:
            if self.PrePrintAutoOpen_var.get() == "是":
                self.click_times = 11
                if "关闭PDF" not in self.state_descriptions:
                    self.state_descriptions.append("关闭PDF")
            else:
                self.click_times = 10
                if "关闭PDF" in self.state_descriptions:
                    self.state_descriptions.pop()
            print(f"自动打开PDF: {self.PrePrintAutoOpen_var.get()}")
            self.create_state_visualization()  # Recreate visualization with new states
        except ValueError as e:
            print(e)

    def change_state(self):
        # Move to next state
        self.current_state = (self.current_state + 1) % self.click_times
        self.update_state_visualization()

    def reset_state(self):
        # Reset to initial state
        self.current_state = 0
        self.update_state_visualization()

    def update_state_visualization(self):
        # Update square colors
        for i, square in enumerate(self.squares):
            color = 'red' if i <= self.current_state else 'gray'
            square.configure(bg=color)

        # Update label styles
        for i, label in enumerate(self.labels):
            if i == self.current_state:
                label.config(
                    fg='red',
                    font=('Arial', 10, 'bold')
                )
            else:
                label.config(
                    fg='black',
                    font=('Arial', 10)
                )

    def start_print(self):
        if not self.printing:
            self.printing = True
            self.lock_gui_elements()

            print("开始打印的代码应该在这里")
            self.Totalpage = int(self.total_number_var.get())
            self.nopage = int(self.start_number_var.get())
            self.PDF_AutoOpen = 1 if self.PrePrintAutoOpen_var.get() == "是" else 0

            for i in range(1, self.Totalpage + 1):
                # 激活CAD窗口
                pyautogui.moveTo(*self.positions['activate_cad'], duration=0.25)
                time.sleep(0.15)
                pyautogui.click(*self.positions['activate_cad'])
                time.sleep(0.35)

                pyautogui.hotkey('ctrl', 'p')
                time.sleep(0.5)
                # 移动到“名称”并点击
                pyautogui.moveTo(*self.positions['name_click'], duration=0.25)
                time.sleep(0.15)
                pyautogui.click(*self.positions['name_click'])

                # 选择上一次打印并点击
                pyautogui.moveTo(*self.positions['last_print_click'], duration=0.25)
                time.sleep(0.15)
                pyautogui.click(*self.positions['last_print_click'])

                # “选择打印区域”
                pyautogui.moveTo(*self.positions['select_print_area'], duration=0.5)
                time.sleep(0.15)
                pyautogui.click(*self.positions['select_print_area'])

                def on_click_print(x, y, button, pressed):
                    if button == mouse.Button.left:
                        if pressed:
                            self.clicked1 += 1
                            print(f"Left click detected at position: ({x}, {y})")
                            time.sleep(0.85)
                            if self.clicked1 >= 2:
                                return False

                with mouse.Listener(on_click=on_click_print) as listener:
                    listener.join()

                if self.clicked1 >= 2:
                    self.clicked1 = 0
                    # 点击确定按钮
                    pyautogui.moveTo(*self.positions['ok_button'], duration=0.5)
                    time.sleep(0.15)
                    pyautogui.click(*self.positions['ok_button'])

                    # 移动到文件名
                    pyautogui.moveTo(*self.positions['file_name_click'], duration=0.5)
                    time.sleep(0.15)
                    pyautogui.click(*self.positions['file_name_click'])
                    time.sleep(0.5)

                    keyboard.press_and_release('backspace')
                    time.sleep(0.35)
                    pyautogui.typewrite(str(self.nopage), interval=0.025)
                    pyautogui.press('enter')
                    time.sleep(0.35)

                    if self.PDF_AutoOpen == 1:
                        print('PDF打印完成后请输入回车键')
                        keyboard.wait('enter')
                        pyautogui.moveTo(1895, 10, duration=0.5)
                        time.sleep(0.15)
                        pyautogui.click(1895, 10)
                    else:
                        time.sleep(1)

                    print("第" + str(self.nopage) + "页，打印完成")

                    if i == self.Totalpage - 1:
                        print("\n所有内容打印完成")
                    self.nopage += 1

                    #self.end_operation('printing')
                    self.printing = False  # 确保这行在打印结束后执行
                    self.end_operation('printing')
    # 假设其他的函数类似地被定义
    def load_position(self):
        if not self.loading:
            self.loading = True
            self.lock_gui_elements()

            print("载入位置的代码应该在这里")

            self.loading = False  # 确保这行在载入结束后执行
            self.end_operation('loading')

    def calibrate_position(self):
        if not self.calibrating:
            self.calibrating = True
            self.lock_gui_elements()
            print("标定顺序：\n  "
                  "1.0我已预打印PDF。"
                  "1.点空白CAD软件区域，激活CAD窗口。\n "
                  "1a.Ctrl+P,激活打印窗口"
                  "2.点击开始按钮"
                  "3.选择上一次打印"
                  "4.点击窗口按钮"
                  "5.框选范围左上角"
                  "6.框选范围右下角"
                  "7.点击确定"
                  "8.改名并确定"
                  "9.关闭已打开的PDF窗口")
            print("请点击CAD空白区域")
            self.listener_thread = threading.Thread(target=self.create_pynput_listener, daemon=True)
            self.listener_thread.start()
            self.calibrating = False  # 确保这行在标定结束后执行
            self.end_operation('calibrating')

    def create_pynput_listener(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def end_operation(self, operation):
        if operation == 'calibrating':
            self.calibrating = False
        elif operation == 'loading':
            self.loading = False
        elif operation == 'printing':
            self.printing = False
        else:
            raise ValueError(f"Unknown operation: {operation}")
        self.unlock_gui_elements()


    def unlock_gui_elements(self):
        if not (self.calibrating or self.loading or self.printing):
            # 只要有一个操作没有在进行中，就可以解锁GUI元素
            for widget in [self.PrePrint_var, self.PrePrintAutoOpen_var, self.total_number_var, self.start_number_var]:
                widget.trace_remove('write', self.lock_controls)
            #self.lock_buttons()  # 这里调用lock_buttons来重置按钮状态
            self.calibrate_button.config(state=tk.NORMAL)
            self.load_button.config(state=tk.NORMAL)
            self.print_button.config(state=tk.NORMAL)

    def on_click(self, x, y, button, pressed):
        with self.lock:
            if button == mouse.Button.left and pressed:
                self.arr[self.ClickedTimes] = (x, y)
                print(f"第{self.ClickedTimes}次点击,位置为：{(x, y)}")

                time.sleep(0.35)
                self.ClickedTimes += 1

                if self.ClickedTimes > self.click_times:  # 框选图形范围，需要鼠标点两次
                    print("标定结束")
                    # Save positions to file
                    with open('C:\\Users\\PositionData.txt', 'w') as f:
                        for i in range(1, len(self.arr) + 1):
                            x, y = self.arr[i]
                            f.write(f'{i}:({x},{y})\n')
                    self.root.after(0, self.end_calibration)  # 使用after来确保在主线程中更新UI状态
                    return False


    def disable_controls(self):
        self.PrePrint_var.set(False)
        self.PrePrintAutoOpen_var.set("否")

def main():
    root = tk.Tk()
    app = AutoCADPrintSelector(root)
    root.mainloop()


if __name__ == "__main__":
    main()
