# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 13:55:35 2025

@author: satellite
"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory, askopenfilenames
import os
from tkinter import simpledialog
import sys

class FolderSelector(tk.Tk):
    def __init__(self, process_callback, show_buttons=None):
        super().__init__()
        self.title("工作站DRT数据处理v0.4")
        self.selected_items = None  # 存储选择的文件或文件夹路径列表
        self.button_text = None  # 存储当前选择的按钮文本
        self.as_one = False  # 存储一个布尔值
        self.flag_text = '仅保留第一个x轴'
        self.lambda_value = 10.0
        self.process_callback = process_callback
        self.dop_value = 10.0  # DOP参数默认值
        self.ask_for_dop = False  # 是否需要询问DOP参数
        self.is_file_selection = False  # 标记是否选择了文件

        self.protocol("WM_DELETE_WINDOW", self.on_closing)        # 添加窗口关闭事件处理

        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 设置窗口初始大小为屏幕的90%
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # 设置窗口位置为屏幕中央
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        
        # 设置窗口大小和位置
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # 允许窗口调整大小
        self.minsize(int(screen_width * 0.5), int(screen_height * 0.5))
        
        # 创建左侧框架用于放置按钮和标签
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.path_label = tk.Label(self.left_frame, 
                                   text="工作站数据转换\n有问题请联系duangs@zju.edu.cn\n请选择文件夹或文件",
                                   wraplength=300) 
        self.path_label.pack(pady=10)

        # 创建选择文件夹按钮
        self.add_folder_button = ttk.Button(self.left_frame, text="选择文件夹",
                                            command=self.add_folder, width=40)
        self.add_folder_button.pack(pady=5)  # 让按钮填充可用宽度
        
        # 创建选择文件按钮
        self.add_file_button = ttk.Button(self.left_frame, text="选择文件 (CHI/gamry/BioLogic/ZPlot/RelaxIs)",
                                          command=self.add_file, width=40)
        self.add_file_button.pack(pady=5)  # 让按钮填充可用宽度

        # 创建用于显示所选路径的标签
        self.path_var = tk.StringVar(value="未选择文件夹或文件")
        self.path_label = tk.Label(self.left_frame, textvariable=self.path_var, wraplength=300)
        self.path_label.pack(pady=10)
        
        # 选择是否只保留一个x轴
        self.as_one_button = ttk.Button(self.left_frame, text=f"{self.flag_text}: {self.as_one}",
                                        command=self.as_one_fuc, width=40)
        self.as_one_button.pack(pady=10)
        
        # 默认显示的按钮列表
        default_buttons = ["EIS", "ZView", "CA", "CV", "Tafel", "CP", "LSV"]
        if show_buttons is None:
            show_buttons = default_buttons

            # 数据类型选择提示
            self.button_label = tk.Label(self.left_frame, text="请选择数据类型")
            self.button_label.pack(pady=10)
        
        elif show_buttons == []:
            self.lambda_button = ttk.Button(self.left_frame, text="设置lambda值 (当前: 10)",
                                            command=self.set_lambda_value, width=40)
            self.lambda_button.pack(pady=10)
        
        for button_name in show_buttons:
            self.create_button(button_name)

        self.end_button = ttk.Button(self.left_frame, text="结束选择", command=self.on_end, width=40)
        self.end_button.pack(pady=10)
        
        # 设置左侧框架权重，使其不随窗口变大而变宽
        self.grid_columnconfigure(0, weight=1)
        
        # 创建右侧框架用于放置绘图区域
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 设置右侧框架权重，使其随窗口变大而变宽
        self.grid_columnconfigure(1, weight=3)

    def create_button(self, key):
        """动态创建按钮并传递不同的值"""
        button = ttk.Button(self.left_frame, text=key, command=lambda: self.key_select(key))
        button.pack(pady=10)  # 让按钮填充可用宽度

    def add_folder(self):
        """选择文件夹功能"""
        folder_selected = askdirectory()
        if folder_selected:
            self.selected_items = [folder_selected]  # 存储为列表
            self.is_file_selection = False
            # 更新显示所选路径的标签内容
            self.path_var.set(folder_selected)

    def add_file(self):
        """选择文件功能"""
        files_selected = askopenfilenames(
            filetypes=[("CHI txt files", "*.txt"),
                       ("CHI csv files", "*.csv"),
                       ("Gamry files", "*.DTA"), 
                       ("BioLogic files", "*.mpr"), 
                       ("All files", "*.*")]
        )
        if files_selected:
            self.selected_items = list(files_selected)  # 存储为列表
            self.is_file_selection = True
            if len(files_selected) == 1:
                file_name = os.path.basename(files_selected[0])
                self.path_var.set(f"已选择文件: {file_name}")
            else:
                self.path_var.set(f"已选择 {len(files_selected)} 个文件")

    def as_one_fuc(self):
        """更新是否仅保留一列x轴或者开启DOP"""
        self.as_one = not self.as_one  # 更新选择的按钮文本
        self.ask_for_dop = self.as_one  # 更新询问标志
        self.as_one_button.config(text=f"{self.flag_text}: {self.as_one}")

        # 如果开启DOP，弹出对话框让用户输入参数
        if self.ask_for_dop and self.flag_text == '是否开启DOP':
            self.ask_dop_parameter()

    def ask_dop_parameter(self):
        """弹出对话框让用户输入DOP参数"""
        try:
            # 弹出输入对话框，默认值为10
            new_value = simpledialog.askfloat(
                "DOP参数设置", 
                "请输入DOP分析的lambda值:",
                minvalue=0.000001, 
                maxvalue=1000.0,
                initialvalue=self.dop_value
            )
            
            if new_value is not None:  # 用户未取消输入
                self.dop_value = new_value
                # 更新按钮提示信息
            self.as_one_button.config(text=f"{self.flag_text}: {self.as_one} (DOP={self.dop_value:.3f})")

        except ValueError:
            # 输入非数字时的处理
            tk.messagebox.showerror("输入错误", "请输入有效的浮点数!")
            self.as_one = not self.as_one  # 回滚开关状态
            self.as_one_button.config(text=f"{self.flag_text}: {self.as_one}")
    
    def set_lambda_value(self):
        """弹出对话框让用户输入lambda值"""
        try:
            # 弹出输入对话框，默认值为10
            new_value = simpledialog.askfloat("输入lambda值", "请输入lambda值:", 
                                             minvalue=0.000001, maxvalue=1000.0,
                                             initialvalue=self.lambda_value)
            if new_value is not None:  # 用户未取消输入
                self.lambda_value = new_value
                self.lambda_button.config(text=f"设置lambda值 (当前: {self.lambda_value:.6f})")
        except ValueError:
            # 输入非数字时的处理
            tk.messagebox.showerror("输入错误", "请输入有效的浮点数!")

    def key_select(self, button_text):
        """根据点击的按钮返回不同的值"""
        self.button_label.config(text=f"选择了{button_text}格式")
        self.button_text = button_text  # 更新选择的按钮文本

    def get_selected_items(self):
        """获取所有选择的项目（文件或文件夹）"""
        return self.selected_items or []

    def on_end(self):
        """结束选择，调用处理函数"""
        if self.selected_items:
            self.process_callback()
            self.selected_items = None
            self.is_file_selection = False
            self.path_var.set("未选择文件夹或文件")
            
            # 处理完数据后检查是否需要退出
            if not self.winfo_exists():
                sys.exit(0)
        else:
            tk.messagebox.showwarning("警告", "请先选择文件夹或文件!")
        
    def on_closing(self):
        """处理窗口关闭事件"""
        try:
            self.destroy()    # 销毁 Tkinter 窗口
            sys.exit(0)
        except Exception as e:
            print(f"Error closing window: {e}")
