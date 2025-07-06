# window.py
# 导入所需的模块
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import db  # 导入数据库操作模块
from PIL import Image, ImageTk
import os

class EntityTab(ttk.Frame):
    """实体标签页的基类，提供通用的UI和功能"""
    def __init__(self, parent, refresh_logs):
        super().__init__(parent)
        self.refresh_logs = refresh_logs  # 刷新日志的回调函数
        self.tree = None  # 树形视图控件
        self.input_vars = {}  # 输入变量字典
        self.selected_id = None  # 当前选中的记录ID
        
        # 设置界面样式
        style = ttk.Style()
        # 配置自定义按钮样式
        style.configure("Custom.TButton", padding=6, relief="flat", background="#4a90e2")
        # 配置自定义框架样式
        style.configure("Custom.TFrame", background="#f5f5f5")
        # 配置自定义标签框样式
        style.configure("Custom.TLabelframe", background="#f5f5f5")
        style.configure("Custom.TLabelframe.Label", font=('Helvetica', 10, 'bold'))
        # 配置树形视图样式
        style.configure("Treeview", rowheight=25, font=('Helvetica', 9))
        style.configure("Treeview.Heading", font=('Helvetica', 9, 'bold'))
        
        # 构建用户界面
        self.build_ui()

    def clear_inputs(self):
        """清空所有输入框"""
        for var in self.input_vars.values():
            var.set("")
        self.selected_id = None

    def create_input_field(self, frame, row, label, var_name):
        """创建输入字段
        
        参数:
            frame: 父框架
            row: 行号
            label: 标签文本
            var_name: 变量名
        """
        ttk.Label(frame, text=label, font=('Helvetica', 9)).grid(row=row, column=0, sticky=tk.W, padx=5)
        self.input_vars[var_name] = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.input_vars[var_name], font=('Helvetica', 9))
        entry.grid(row=row, column=1, padx=5, pady=3, sticky=tk.EW)
        if var_name == "id":
            entry.configure(state='readonly')  # ID字段设为只读
        return entry

    def on_tree_select(self, event):
        """树形视图选择事件处理"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.tree.item(item)['values']
        self.selected_id = values[0]  # 第一列总是ID
        
        # 填充输入框
        self.input_vars["id"].set(str(values[0]))
        self.fill_input_fields(values)

    def fill_input_fields(self, values):
        """填充输入字段（由子类实现）"""
        pass

    def build_ui(self):
        """构建用户界面（由子类实现）"""
        pass

    def refresh_data(self):
        """刷新数据（由子类实现）"""
        pass

    def add_person(self):
        """添加人物（触发器控制）"""
        if not self.input_vars["name"].get() or not self.input_vars["country"].get():
            messagebox.showerror("错误", "姓名和国家是必填项！")
            return
            
        try:
            db.insert_person(
                self.input_vars["name"].get(),
                self.input_vars["country"].get(),
                self.input_vars["masterpiece"].get(),
                self.input_vars["brief_intro"].get()
            )
            messagebox.showinfo("成功", "添加成功！触发器已记录此操作。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def update_person(self):
        """更新人物信息（存储过程控制）"""
        if not self.input_vars["id"].get() or not self.input_vars["name"].get():
            messagebox.showerror("错误", "ID和姓名是必填项！")
            return
            
        try:
            db.update_person_with_procedure(
                int(self.input_vars["id"].get()),
                self.input_vars["name"].get(),
                self.input_vars["country"].get(),
                self.input_vars["masterpiece"].get(),
                self.input_vars["brief_intro"].get()
            )
            messagebox.showinfo("成功", "修改成功！存储过程已执行。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def delete_person(self):
        """删除人物（事务控制）"""
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请输入要删除的记录ID！")
            return
            
        if not messagebox.askyesno("确认", "确定要删除这条记录吗？此操作将在事务中执行。"):
            return
            
        try:
            db.delete_person_with_transaction(int(self.input_vars["id"].get()))
            messagebox.showinfo("成功", "删除成功！事务已完成。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def show_summary(self):
        """显示人物简要信息（视图查询）"""
        summary_window = tk.Toplevel(self)
        summary_window.title("人物简要信息视图")
        
        tree = ttk.Treeview(summary_window, columns=("ID", "姓名", "国家", "代表作"), show="headings")
        for col in ["ID", "姓名", "国家", "代表作"]:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(summary_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 从视图获取数据
        summary_data = db.get_people_summary()
        for item in summary_data:
            tree.insert("", tk.END, values=(
                item['people_id'],
                item['name'],
                item['country'],
                item['masterpiece']
            ))

class PeopleTab(EntityTab):
    """人物管理标签页"""
    def fill_input_fields(self, values):
        """填充人物信息到输入框"""
        if not values:
            return
        self.input_vars["name"].set(values[1] if len(values) > 1 else "")
        self.input_vars["country"].set(values[2] if len(values) > 2 else "")
        self.input_vars["masterpiece"].set(values[3] if len(values) > 3 else "")
        self.input_vars["brief_intro"].set(values[4] if len(values) > 4 else "")

    def build_ui(self):
        """构建人物管理界面"""
        self.columnconfigure(0, weight=1)
        
        # 创建输入区域
        input_frame = ttk.LabelFrame(self, text="人物信息输入", padding="10", style="Custom.TLabelframe")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        input_frame.columnconfigure(1, weight=1)

        # 创建输入字段
        self.create_input_field(input_frame, 0, "ID:", "id")
        self.create_input_field(input_frame, 1, "姓名:", "name")
        self.create_input_field(input_frame, 2, "国家:", "country")
        self.create_input_field(input_frame, 3, "代表作:", "masterpiece")
        self.create_input_field(input_frame, 4, "简介:", "brief_intro")

        # 创建按钮区域
        button_frame = ttk.Frame(self, style="Custom.TFrame")
        button_frame.grid(row=1, column=0, pady=10)

        # 定义按钮
        buttons = [
            ("新增", self.add_person),
            ("修改", self.update_person),
            ("删除", self.delete_person),
            ("查看简要信息", self.show_summary),
            ("刷新", self.refresh_data),
            ("管理获奖记录", self.show_awards),
            ("查看详细信息", self.show_details)
        ]

        # 创建按钮
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, style="Custom.TButton")
            btn.grid(row=0, column=i, padx=5)

        # 创建数据显示区域
        data_frame = ttk.LabelFrame(self, text="人物列表", padding="10", style="Custom.TLabelframe")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        # 创建树形视图框架
        tree_frame = ttk.Frame(data_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # 创建树形视图
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "姓名", "国家", "代表作", "简介"), show="headings")
        
        # 设置列属性
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("姓名", width=100, anchor=tk.W)
        self.tree.column("国家", width=100, anchor=tk.W)
        self.tree.column("代表作", width=150, anchor=tk.W)
        self.tree.column("简介", width=200, anchor=tk.W)
        
        # 设置列标题
        for col in ["ID", "姓名", "国家", "代表作", "简介"]:
            self.tree.heading(col, text=col)

        # 添加滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局树形视图和滚动条
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def refresh_data(self):
        """刷新人物数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取并显示新数据
        people = db.fetch_all_people()
        for person in people:
            self.tree.insert("", tk.END, values=(
                person['people_id'],
                person['name'],
                person['country'],
                person['masterpiece'],
                person['brief_intro']
            ))
        self.refresh_logs()

    def show_awards(self):
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请先选择一个人物！")
            return

        people_id = int(self.input_vars["id"].get())
        person_name = self.input_vars["name"].get()
        awards_window = tk.Toplevel(self)
        awards_window.title(f"获奖记录 - {person_name}")
        awards_window.geometry("600x500")
        
        # 显示现有获奖记录
        awards_frame = ttk.LabelFrame(awards_window, text="获奖记录", padding="10", style="Custom.TLabelframe")
        awards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(awards_frame, columns=("奖项", "类别", "获奖年份"), show="headings")
        for col in ["奖项", "类别", "获奖年份"]:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(awards_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        awards = db.get_person_awards(people_id)
        for award in awards:
            tree.insert("", tk.END, values=(
                award['award_name'],
                award['award_category'],
                award['award_year']
            ))
        
        # 添加新获奖记录
        add_frame = ttk.LabelFrame(awards_window, text="添加获奖记录", padding="10", style="Custom.TLabelframe")
        add_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 获取所有可用奖项
        all_awards = db.fetch_all_awards()
        award_choices = [(award['award_id'], f"{award['name']} ({award['category']})") for award in all_awards]
        
        # 创建下拉列表
        ttk.Label(add_frame, text="选择奖项:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        award_var = tk.StringVar()
        award_combo = ttk.Combobox(add_frame, textvariable=award_var, state="readonly", width=40)
        award_combo['values'] = [choice[1] for choice in award_choices]
        award_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="获奖年份:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        award_year_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=award_year_var).grid(row=1, column=1, padx=5, pady=5)
        
        def add_award():
            if not award_var.get() or not award_year_var.get():
                messagebox.showerror("错误", "请填写完整信息！")
                return
            
            try:
                # 从选择中获取award_id
                selected_index = award_combo.current()
                if selected_index < 0:
                    messagebox.showerror("错误", "请选择一个奖项！")
                    return
                
                award_id = award_choices[selected_index][0]
                
                db.add_person_award(
                    people_id,
                    award_id,
                    int(award_year_var.get())
                )
                messagebox.showinfo("成功", "添加获奖记录成功！")
                
                # 刷新获奖记录列表
                tree.delete(*tree.get_children())
                awards = db.get_person_awards(people_id)
                for award in awards:
                    tree.insert("", tk.END, values=(
                        award['award_name'],
                        award['award_category'],
                        award['award_year']
                    ))
                
                # 清空输入
                award_var.set("")
                award_year_var.set("")
                
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        ttk.Button(add_frame, text="添加", command=add_award, style="Custom.TButton").grid(row=2, column=0, columnspan=2, pady=10)

    def show_details(self):
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请先选择一个人物！")
            return

        people_id = int(self.input_vars["id"].get())
        details = db.get_person_details(people_id)
        if not details:
            messagebox.showerror("错误", "未找到该人物信息！")
            return

        details_window = tk.Toplevel(self)
        details_window.title(f"人物详细信息 - {details['basic_info']['name']}")
        details_window.geometry("600x800")

        # 基本信息
        basic_frame = ttk.LabelFrame(details_window, text="基本信息", padding="5")
        basic_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(basic_frame, text=f"姓名: {details['basic_info']['name']}").pack(anchor=tk.W)
        ttk.Label(basic_frame, text=f"国家: {details['basic_info']['country']}").pack(anchor=tk.W)
        ttk.Label(basic_frame, text=f"代表作: {details['basic_info']['masterpiece']}").pack(anchor=tk.W)
        ttk.Label(basic_frame, text=f"简介: {details['basic_info']['brief_intro']}").pack(anchor=tk.W)

        # 获奖信息
        awards_frame = ttk.LabelFrame(details_window, text="获奖记录", padding="5")
        awards_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        awards_tree = ttk.Treeview(awards_frame, columns=("奖项", "类别", "年份"), show="headings")
        for col in ["奖项", "类别", "年份"]:
            awards_tree.heading(col, text=col)
            awards_tree.column(col, width=100)
        
        for award in details['awards']:
            awards_tree.insert("", tk.END, values=(
                award['award_name'],
                award['award_category'],
                award['award_year']
            ))
        
        awards_tree.pack(fill=tk.BOTH, expand=True)

class MoviesTab(EntityTab):
    # 填充电影信息到输入框
    def fill_input_fields(self, values):
        if not values:
            return
        self.input_vars["title"].set(values[1] if len(values) > 1 else "")
        self.input_vars["release_year"].set(values[2] if len(values) > 2 else "")
        self.input_vars["director"].set(values[3] if len(values) > 3 else "")
        self.input_vars["genre"].set(values[4] if len(values) > 4 else "")
        self.input_vars["box_office"].set(values[5] if len(values) > 5 else "")
        self.input_vars["description"].set(values[6] if len(values) > 6 else "")

    # 构建电影管理界面
    def build_ui(self):
        self.columnconfigure(0, weight=1)
        
        # 创建输入区域
        input_frame = ttk.LabelFrame(self, text="电影信息输入", padding="10", style="Custom.TLabelframe")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        input_frame.columnconfigure(1, weight=1)

        # 创建输入字段
        self.create_input_field(input_frame, 0, "ID:", "id")
        self.create_input_field(input_frame, 1, "标题:", "title")
        self.create_input_field(input_frame, 2, "上映年份:", "release_year")
        self.create_input_field(input_frame, 3, "导演:", "director")
        self.create_input_field(input_frame, 4, "类型:", "genre")
        self.create_input_field(input_frame, 5, "票房:", "box_office")
        self.create_input_field(input_frame, 6, "描述:", "description")

        # 创建按钮区域
        button_frame = ttk.Frame(self, style="Custom.TFrame")
        button_frame.grid(row=1, column=0, pady=10)

        # 定义按钮
        buttons = [
            ("新增", self.add_movie),
            ("修改", self.update_movie),
            ("删除", self.delete_movie),
            ("查看简要信息", self.show_summary),
            ("刷新", self.refresh_data),
            ("管理获奖记录", self.show_awards),
            ("查看详细信息", self.show_details),
            ("管理演员", self.show_actors)
        ]

        # 创建按钮
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, style="Custom.TButton")
            btn.grid(row=0, column=i, padx=5)

        # 创建数据显示区域
        data_frame = ttk.LabelFrame(self, text="电影列表", padding="10", style="Custom.TLabelframe")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        # 创建树形视图框架
        tree_frame = ttk.Frame(data_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # 创建树形视图
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "标题", "年份", "导演", "类型", "票房", "描述"), show="headings")
        
        # 设置列属性
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("标题", width=150, anchor=tk.W)
        self.tree.column("年份", width=70, anchor=tk.CENTER)
        self.tree.column("导演", width=100, anchor=tk.W)
        self.tree.column("类型", width=80, anchor=tk.W)
        self.tree.column("票房", width=100, anchor=tk.E)
        self.tree.column("描述", width=200, anchor=tk.W)
        
        # 设置列标题
        for col in ["ID", "标题", "年份", "导演", "类型", "票房", "描述"]:
            self.tree.heading(col, text=col)

        # 添加滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局树形视图和滚动条
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    # 刷新电影数据
    def refresh_data(self):
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取并显示新数据
        movies = db.fetch_all_movies()
        for movie in movies:
            self.tree.insert("", tk.END, values=(
                movie['movie_id'],
                movie['title'],
                movie['release_year'],
                movie['director'],
                movie['genre'],
                movie['box_office'],
                movie['description']
            ))
        self.refresh_logs()

    # 添加电影（触发器控制）
    def add_movie(self):
        if not self.input_vars["title"].get():
            messagebox.showerror("错误", "电影标题是必填项！")
            return
            
        try:
            db.insert_movie(
                self.input_vars["title"].get(),
                int(self.input_vars["release_year"].get() or 0),
                self.input_vars["director"].get(),
                self.input_vars["genre"].get(),
                float(self.input_vars["box_office"].get() or 0),
                self.input_vars["description"].get()
            )
            messagebox.showinfo("成功", "添加成功！触发器已记录此操作。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 更新电影信息（存储过程控制）
    def update_movie(self):
        if not self.input_vars["id"].get() or not self.input_vars["title"].get():
            messagebox.showerror("错误", "ID和标题是必填项！")
            return
            
        try:
            db.update_movie_with_procedure(
                int(self.input_vars["id"].get()),
                self.input_vars["title"].get(),
                int(self.input_vars["release_year"].get() or 0),
                self.input_vars["director"].get(),
                self.input_vars["genre"].get(),
                float(self.input_vars["box_office"].get() or 0),
                self.input_vars["description"].get()
            )
            messagebox.showinfo("成功", "修改成功！存储过程已执行。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 删除电影（事务控制）
    def delete_movie(self):
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请输入要删除的电影ID！")
            return
            
        if not messagebox.askyesno("确认", "确定要删除这部电影吗？此操作将在事务中执行。"):
            return
            
        try:
            db.delete_movie_with_transaction(int(self.input_vars["id"].get()))
            messagebox.showinfo("成功", "删除成功！事务已完成。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 显示电影简要信息（视图查询）
    def show_summary(self):
        summary_window = tk.Toplevel(self)
        summary_window.title("电影简要信息视图")
        
        tree = ttk.Treeview(summary_window, columns=("ID", "标题", "年份", "导演", "类型"), show="headings")
        for col, width in [("ID", 50), ("标题", 150), ("年份", 70), ("导演", 100), ("类型", 80)]:
            tree.heading(col, text=col)
            tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(summary_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 从视图获取数据
        summary_data = db.get_movies_summary()
        for item in summary_data:
            tree.insert("", tk.END, values=(
                item['movie_id'],
                item['title'],
                item['release_year'],
                item['director'],
                item['genre']
            ))

    # 管理电影获奖记录
    def show_awards(self):
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请先选择一部电影！")
            return

        movie_id = int(self.input_vars["id"].get())
        movie_title = self.input_vars["title"].get()
        awards_window = tk.Toplevel(self)
        awards_window.title(f"获奖记录 - {movie_title}")
        awards_window.geometry("600x500")
        
        # 显示现有获奖记录
        awards_frame = ttk.LabelFrame(awards_window, text="获奖记录", padding="10", style="Custom.TLabelframe")
        awards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(awards_frame, columns=("奖项", "类别", "获奖年份"), show="headings")
        for col in ["奖项", "类别", "获奖年份"]:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(awards_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 获取获奖记录数据
        awards = db.get_movie_awards(movie_id)
        for award in awards:
            tree.insert("", tk.END, values=(
                award['award_name'],
                award['award_category'],
                award['award_year']
            ))
        
        # 添加新获奖记录区域
        add_frame = ttk.LabelFrame(awards_window, text="添加获奖记录", padding="10", style="Custom.TLabelframe")
        add_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 获取所有可用奖项
        all_awards = db.fetch_all_awards()
        award_choices = [(award['award_id'], f"{award['name']} ({award['category']})") for award in all_awards]
        
        # 创建下拉列表
        ttk.Label(add_frame, text="选择奖项:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        award_var = tk.StringVar()
        award_combo = ttk.Combobox(add_frame, textvariable=award_var, state="readonly", width=40)
        award_combo['values'] = [choice[1] for choice in award_choices]
        award_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="获奖年份:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        award_year_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=award_year_var).grid(row=1, column=1, padx=5, pady=5)
        
        # 添加获奖记录功能
        def add_award():
            if not award_var.get() or not award_year_var.get():
                messagebox.showerror("错误", "请填写完整信息！")
                return
            
            try:
                # 从选择中获取award_id
                selected_index = award_combo.current()
                if selected_index < 0:
                    messagebox.showerror("错误", "请选择一个奖项！")
                    return
                
                award_id = award_choices[selected_index][0]
                
                db.add_movie_award(
                    movie_id,
                    award_id,
                    int(award_year_var.get())
                )
                messagebox.showinfo("成功", "添加获奖记录成功！")
                
                # 刷新获奖记录列表
                tree.delete(*tree.get_children())
                awards = db.get_movie_awards(movie_id)
                for award in awards:
                    tree.insert("", tk.END, values=(
                        award['award_name'],
                        award['award_category'],
                        award['award_year']
                    ))
                
                # 清空输入
                award_var.set("")
                award_year_var.set("")
                
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        ttk.Button(add_frame, text="添加", command=add_award, style="Custom.TButton").grid(row=2, column=0, columnspan=2, pady=10)

    def show_details(self):
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请先选择一部电影！")
            return

        movie_id = int(self.input_vars["id"].get())
        details = db.get_movie_details(movie_id)
        if not details:
            messagebox.showerror("错误", "未找到该电影信息！")
            return

        details_window = tk.Toplevel(self)
        details_window.title(f"电影详细信息 - {details['basic_info']['title']}")
        details_window.geometry("600x800")

        # 基本信息
        basic_frame = ttk.LabelFrame(details_window, text="基本信息", padding="5")
        basic_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(basic_frame, text=f"标题: {details['basic_info']['title']}").pack(anchor=tk.W)
        ttk.Label(basic_frame, text=f"年份: {details['basic_info']['release_year']}").pack(anchor=tk.W)
        ttk.Label(basic_frame, text=f"导演: {details['basic_info']['director']}").pack(anchor=tk.W)
        ttk.Label(basic_frame, text=f"类型: {details['basic_info']['genre']}").pack(anchor=tk.W)
        ttk.Label(basic_frame, text=f"票房: {details['basic_info']['box_office']}").pack(anchor=tk.W)
        ttk.Label(basic_frame, text=f"描述: {details['basic_info']['description']}").pack(anchor=tk.W)

        # 获奖信息
        awards_frame = ttk.LabelFrame(details_window, text="获奖记录", padding="5")
        awards_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        awards_tree = ttk.Treeview(awards_frame, columns=("奖项", "类别", "年份"), show="headings")
        for col in ["奖项", "类别", "年份"]:
            awards_tree.heading(col, text=col)
            awards_tree.column(col, width=100)
        
        for award in details['awards']:
            awards_tree.insert("", tk.END, values=(
                award['award_name'],
                award['award_category'],
                award['award_year']
            ))
        
        awards_tree.pack(fill=tk.BOTH, expand=True)

        # 演员阵容
        actors_frame = ttk.LabelFrame(details_window, text="演员阵容", padding="5")
        actors_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        actors_tree = ttk.Treeview(actors_frame, columns=("姓名", "角色", "是否主演"), show="headings")
        for col in ["姓名", "角色", "是否主演"]:
            actors_tree.heading(col, text=col)
        actors_tree.column("姓名", width=150)
        actors_tree.column("角色", width=150)
        actors_tree.column("是否主演", width=100)
        
        for actor in details['actors']:
            actors_tree.insert("", tk.END, values=(
                actor['name'],
                actor['role'],
                "是" if actor['is_protagonist'] else "否"
            ))
        
        actors_tree.pack(fill=tk.BOTH, expand=True)

        # 相关公司
        companies_frame = ttk.LabelFrame(details_window, text="相关公司", padding="5")
        companies_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        companies_tree = ttk.Treeview(companies_frame, columns=("公司名称", "关系类型"), show="headings")
        for col in ["公司名称", "关系类型"]:
            companies_tree.heading(col, text=col)
            companies_tree.column(col, width=200)
        
        for company in details['companies']:
            companies_tree.insert("", tk.END, values=(
                company['name'],
                company['relationship_type']
            ))
        
        companies_tree.pack(fill=tk.BOTH, expand=True)

    def show_actors(self):
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请先选择一部电影！")
            return

        movie_id = int(self.input_vars["id"].get())
        actors_window = tk.Toplevel(self)
        actors_window.title("演员管理")
        
        # 显示现有演员
        actors_frame = ttk.LabelFrame(actors_window, text="演员列表", padding="5")
        actors_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        tree = ttk.Treeview(actors_frame, columns=("演员", "角色", "是否主演"), show="headings")
        for col in ["演员", "角色", "是否主演"]:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        actors = db.get_movie_actors(movie_id)
        for actor in actors:
            tree.insert("", tk.END, values=(
                actor['actor_name'],
                actor['role'],
                "是" if actor['is_protagonist'] else "否"
            ))
        
        # 添加新演员
        add_frame = ttk.LabelFrame(actors_window, text="添加演员", padding="5")
        add_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        actor_id_var = tk.StringVar()
        role_var = tk.StringVar()
        is_protagonist_var = tk.BooleanVar()
        
        ttk.Label(add_frame, text="演员ID:").grid(row=0, column=0)
        ttk.Entry(add_frame, textvariable=actor_id_var).grid(row=0, column=1)
        
        ttk.Label(add_frame, text="角色:").grid(row=1, column=0)
        ttk.Entry(add_frame, textvariable=role_var).grid(row=1, column=1)
        
        ttk.Checkbutton(add_frame, text="是否主演", variable=is_protagonist_var).grid(row=2, column=0, columnspan=2)
        
        def add_actor():
            try:
                db.add_movie_actor(
                    movie_id,
                    int(actor_id_var.get()),
                    role_var.get(),
                    is_protagonist_var.get()
                )
                messagebox.showinfo("成功", "添加演员成功！")
                actors_window.destroy()
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        ttk.Button(add_frame, text="添加", command=add_actor).grid(row=3, column=0, columnspan=2, pady=5)

# 公司管理标签页
class CompaniesTab(EntityTab):
    # 填充公司信息到输入框
    def fill_input_fields(self, values):
        if not values:
            return
        self.input_vars["name"].set(values[1] if len(values) > 1 else "")
        self.input_vars["country"].set(values[2] if len(values) > 2 else "")
        self.input_vars["founded_year"].set(values[3] if len(values) > 3 else "")
        self.input_vars["industry"].set(values[4] if len(values) > 4 else "")
        self.input_vars["revenue"].set(values[5] if len(values) > 5 else "")
        self.input_vars["description"].set(values[6] if len(values) > 6 else "")

    # 构建公司管理界面
    def build_ui(self):
        self.columnconfigure(0, weight=1)
        
        # 创建输入区域
        input_frame = ttk.LabelFrame(self, text="公司信息输入", padding="10", style="Custom.TLabelframe")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        input_frame.columnconfigure(1, weight=1)

        # 创建输入字段
        self.create_input_field(input_frame, 0, "ID:", "id")
        self.create_input_field(input_frame, 1, "公司名称:", "name")
        self.create_input_field(input_frame, 2, "国家:", "country")
        self.create_input_field(input_frame, 3, "成立年份:", "founded_year")
        self.create_input_field(input_frame, 4, "行业:", "industry")
        self.create_input_field(input_frame, 5, "营收:", "revenue")
        self.create_input_field(input_frame, 6, "描述:", "description")

        # 创建按钮区域
        button_frame = ttk.Frame(self, style="Custom.TFrame")
        button_frame.grid(row=1, column=0, pady=10)

        # 定义按钮
        buttons = [
            ("新增", self.add_company),
            ("修改", self.update_company),
            ("删除", self.delete_company),
            ("查看简要信息", self.show_summary),
            ("刷新", self.refresh_data)
        ]

        # 创建按钮
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, style="Custom.TButton")
            btn.grid(row=0, column=i, padx=5)

        # 创建数据显示区域
        data_frame = ttk.LabelFrame(self, text="公司列表", padding="10", style="Custom.TLabelframe")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        # 创建树形视图框架
        tree_frame = ttk.Frame(data_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # 创建树形视图
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "名称", "国家", "成立年份", "行业", "营收", "描述"), show="headings")
        
        # 设置列属性
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("名称", width=150, anchor=tk.W)
        self.tree.column("国家", width=80, anchor=tk.W)
        self.tree.column("成立年份", width=70, anchor=tk.CENTER)
        self.tree.column("行业", width=100, anchor=tk.W)
        self.tree.column("营收", width=100, anchor=tk.E)
        self.tree.column("描述", width=200, anchor=tk.W)
        
        # 设置列标题
        for col in ["ID", "名称", "国家", "成立年份", "行业", "营收", "描述"]:
            self.tree.heading(col, text=col)

        # 添加滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局树形视图和滚动条
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    # 刷新公司数据
    def refresh_data(self):
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取并显示新数据
        companies = db.fetch_all_companies()
        for company in companies:
            self.tree.insert("", tk.END, values=(
                company['company_id'],
                company['name'],
                company['country'],
                company['founded_year'],
                company['industry'],
                company['revenue'],
                company['description']
            ))
        self.refresh_logs()

    # 添加公司（触发器控制）
    def add_company(self):
        if not self.input_vars["name"].get():
            messagebox.showerror("错误", "公司名称是必填项！")
            return
            
        try:
            db.insert_company(
                self.input_vars["name"].get(),
                self.input_vars["country"].get(),
                int(self.input_vars["founded_year"].get() or 0),
                self.input_vars["industry"].get(),
                float(self.input_vars["revenue"].get() or 0),
                self.input_vars["description"].get()
            )
            messagebox.showinfo("成功", "添加成功！触发器已记录此操作。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 更新公司信息（存储过程控制）
    def update_company(self):
        if not self.input_vars["id"].get() or not self.input_vars["name"].get():
            messagebox.showerror("错误", "ID和公司名称是必填项！")
            return
            
        try:
            db.update_company_with_procedure(
                int(self.input_vars["id"].get()),
                self.input_vars["name"].get(),
                self.input_vars["country"].get(),
                int(self.input_vars["founded_year"].get() or 0),
                self.input_vars["industry"].get(),
                float(self.input_vars["revenue"].get() or 0),
                self.input_vars["description"].get()
            )
            messagebox.showinfo("成功", "修改成功！存储过程已执行。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 删除公司（事务控制）
    def delete_company(self):
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请输入要删除的公司ID！")
            return
            
        if not messagebox.askyesno("确认", "确定要删除这家公司吗？此操作将在事务中执行。"):
            return
            
        try:
            db.delete_company_with_transaction(int(self.input_vars["id"].get()))
            messagebox.showinfo("成功", "删除成功！事务已完成。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 显示公司简要信息（视图查询）
    def show_summary(self):
        summary_window = tk.Toplevel(self)
        summary_window.title("公司简要信息视图")
        
        tree = ttk.Treeview(summary_window, columns=("ID", "名称", "国家", "行业", "成立年份"), show="headings")
        for col, width in [("ID", 50), ("名称", 150), ("国家", 80), ("行业", 100), ("成立年份", 70)]:
            tree.heading(col, text=col)
            tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(summary_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 从视图获取数据
        summary_data = db.get_companies_summary()
        for item in summary_data:
            tree.insert("", tk.END, values=(
                item['company_id'],
                item['name'],
                item['country'],
                item['industry'],
                item['founded_year']
            ))

# 奖项管理标签页
class AwardsTab(EntityTab):
    # 填充奖项信息到输入框
    def fill_input_fields(self, values):
        if not values:
            return
        self.input_vars["name"].set(values[1] if len(values) > 1 else "")
        self.input_vars["category"].set(values[2] if len(values) > 2 else "")
        self.input_vars["year"].set(values[3] if len(values) > 3 else "")
        self.input_vars["description"].set(values[4] if len(values) > 4 else "")

    # 构建奖项管理界面
    def build_ui(self):
        self.columnconfigure(0, weight=1)
        
        # 创建输入区域
        input_frame = ttk.LabelFrame(self, text="奖项信息输入", padding="10", style="Custom.TLabelframe")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        input_frame.columnconfigure(1, weight=1)

        # 创建输入字段
        self.create_input_field(input_frame, 0, "ID:", "id")
        self.create_input_field(input_frame, 1, "奖项名称:", "name")
        self.create_input_field(input_frame, 2, "类别:", "category")
        self.create_input_field(input_frame, 3, "年份:", "year")
        self.create_input_field(input_frame, 4, "描述:", "description")

        # 创建按钮区域
        button_frame = ttk.Frame(self, style="Custom.TFrame")
        button_frame.grid(row=1, column=0, pady=10)

        # 定义按钮
        buttons = [
            ("新增", self.add_award),
            ("修改", self.update_award),
            ("删除", self.delete_award),
            ("查看简要信息", self.show_summary),
            ("刷新", self.refresh_data)
        ]

        # 创建按钮
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, style="Custom.TButton")
            btn.grid(row=0, column=i, padx=5)

        # 创建数据显示区域
        data_frame = ttk.LabelFrame(self, text="奖项列表", padding="10", style="Custom.TLabelframe")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        # 创建树形视图框架
        tree_frame = ttk.Frame(data_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # 创建树形视图
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "名称", "类别", "年份", "描述"), show="headings")
        
        # 设置列属性
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("名称", width=150, anchor=tk.W)
        self.tree.column("类别", width=100, anchor=tk.W)
        self.tree.column("年份", width=70, anchor=tk.CENTER)
        self.tree.column("描述", width=200, anchor=tk.W)
        
        # 设置列标题
        for col in ["ID", "名称", "类别", "年份", "描述"]:
            self.tree.heading(col, text=col)

        # 添加滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局树形视图和滚动条
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    # 刷新奖项数据
    def refresh_data(self):
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取并显示新数据
        awards = db.fetch_all_awards()
        for award in awards:
            self.tree.insert("", tk.END, values=(
                award['award_id'],
                award['name'],
                award['category'],
                award['year'],
                award['description']
            ))
        self.refresh_logs()

    # 添加奖项（触发器控制）
    def add_award(self):
        if not self.input_vars["name"].get():
            messagebox.showerror("错误", "奖项名称是必填项！")
            return
            
        try:
            db.insert_award(
                self.input_vars["name"].get(),
                self.input_vars["category"].get(),
                int(self.input_vars["year"].get() or 0),
                self.input_vars["description"].get()
            )
            messagebox.showinfo("成功", "添加成功！触发器已记录此操作。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 更新奖项信息（存储过程控制）
    def update_award(self):
        if not self.input_vars["id"].get() or not self.input_vars["name"].get():
            messagebox.showerror("错误", "ID和奖项名称是必填项！")
            return
            
        try:
            db.update_award_with_procedure(
                int(self.input_vars["id"].get()),
                self.input_vars["name"].get(),
                self.input_vars["category"].get(),
                int(self.input_vars["year"].get() or 0),
                self.input_vars["description"].get()
            )
            messagebox.showinfo("成功", "修改成功！存储过程已执行。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 删除奖项（事务控制）
    def delete_award(self):
        if not self.input_vars["id"].get():
            messagebox.showerror("错误", "请输入要删除的奖项ID！")
            return
            
        if not messagebox.askyesno("确认", "确定要删除这个奖项吗？此操作将在事务中执行。"):
            return
            
        try:
            db.delete_award_with_transaction(int(self.input_vars["id"].get()))
            messagebox.showinfo("成功", "删除成功！事务已完成。")
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 显示奖项简要信息（视图查询）
    def show_summary(self):
        summary_window = tk.Toplevel(self)
        summary_window.title("奖项简要信息视图")
        
        tree = ttk.Treeview(summary_window, columns=("ID", "名称", "类别", "年份"), show="headings")
        for col, width in [("ID", 50), ("名称", 150), ("类别", 100), ("年份", 70)]:
            tree.heading(col, text=col)
            tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(summary_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 从视图获取数据
        summary_data = db.get_awards_summary()
        for item in summary_data:
            tree.insert("", tk.END, values=(
                item['award_id'],
                item['name'],
                item['category'],
                item['year']
            ))

class App:
    # 初始化应用程序
    def __init__(self, root):
        self.root = root
        self.root.title("电影数据库管理系统")
        
        # 设置窗口大小和位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#fff5f5')
        
        # 设置界面样式
        style = ttk.Style()
        
        # 配置马卡龙主题颜色
        colors = {
            'pink': '#ffd1dc',        # 柔和淡粉色
            'mint': '#c9e4d6',        # 柔和薄荷绿
            'lavender': '#e6e6fa',    # 淡紫色
            'peach': '#ffe5d4',       # 柔和蜜桃色
            'sky': '#bae1ff',         # 柔和天蓝色
            'cream': '#fff5f5',       # 奶油色
            'dark_text': '#4a4a4a',   # 深灰色文字
            'light_pink': '#fff0f3',  # 更浅的粉色
            'border': '#ffb5c5'       # 边框粉色
        }
        
        # 配置基础样式
        style.configure('Custom.TFrame', background=colors['cream'])
        style.configure('Custom.TNotebook', background=colors['cream'])
        
        # 配置选项卡样式
        style.configure('Custom.TNotebook.Tab', 
                       padding=[20, 8],
                       background=colors['lavender'],
                       foreground=colors['dark_text'],
                       font=('Microsoft YaHei', 10, 'bold'))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', colors['light_pink'])],
                 foreground=[('selected', colors['dark_text'])])
        
        # 配置标签框样式
        style.configure('Custom.TLabelframe', 
                       background=colors['peach'],
                       bordercolor=colors['border'],
                       relief='groove')
        style.configure('Custom.TLabelframe.Label', 
                       font=('Microsoft YaHei', 10, 'bold'),
                       foreground=colors['dark_text'],
                       background=colors['peach'],
                       padding=[10, 5])
        
        # 配置按钮样式
        style.configure('Custom.TButton',
                       padding=[15, 8],
                       background=colors['sky'],
                       foreground=colors['dark_text'],
                       font=('Microsoft YaHei', 9, 'bold'),
                       relief='raised',
                       borderwidth=2)
        style.map('Custom.TButton',
                 background=[('active', colors['mint']),
                           ('pressed', colors['pink'])],
                 foreground=[('active', colors['dark_text'])],
                 relief=[('pressed', 'sunken')])
        
        # 配置树形视图样式
        style.configure('Treeview',
                       background='white',
                       fieldbackground='white',
                       font=('Microsoft YaHei', 9),
                       rowheight=28,
                       relief='flat')
        style.configure('Treeview.Heading',
                       background=colors['lavender'],
                       foreground=colors['dark_text'],
                       font=('Microsoft YaHei', 9, 'bold'),
                       relief='raised',
                       padding=[5, 5])
        style.map('Treeview',
                 background=[('selected', colors['light_pink'])],
                 foreground=[('selected', colors['dark_text'])])
                 
        # 配置输入框样式
        style.configure('TEntry',
                       fieldbackground='white',
                       font=('Microsoft YaHei', 9),
                       padding=[5, 3])
                       
        # 配置标签样式
        style.configure('TLabel',
                       background=colors['peach'],
                       foreground=colors['dark_text'],
                       font=('Microsoft YaHei', 9),
                       padding=[5, 3])
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, style='Custom.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 创建搜索框
        self.create_search_bar()
        
        # 调整主框架的行权重
        self.main_frame.grid_rowconfigure(0, weight=1)  # 搜索栏
        self.main_frame.grid_rowconfigure(1, weight=12)  # 选项卡
        self.main_frame.grid_rowconfigure(2, weight=3)  # 日志区域
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # 创建选项卡
        self.create_tabs()
        
        # 创建日志区域
        self.create_log_area()
        
        # 刷新数据
        self.refresh_all()

    def create_search_bar(self):
        """创建搜索栏
        
        创建一个全局搜索框，用于在当前标签页中搜索数据。
        包含搜索输入框和搜索/清除按钮。
        """
        search_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        search_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # 让搜索框容器可以自适应
        search_frame.grid_columnconfigure(1, weight=1)  # 搜索输入框列可以扩展
        
        # 搜索标签
        ttk.Label(search_frame, text="快速搜索:", 
                 font=('Microsoft YaHei', 9, 'bold')).grid(row=0, column=0, padx=5)
        
        # 搜索输入框
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=0, column=2, padx=5)
        
        # 搜索和清除按钮
        ttk.Button(btn_frame, text="搜索", 
                  command=self.perform_search, 
                  style='Custom.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="清除", 
                  command=self.clear_search, 
                  style='Custom.TButton').pack(side=tk.LEFT, padx=2)
        
        # 绑定回车键
        search_entry.bind('<Return>', lambda e: self.perform_search())

    def perform_search(self):
        """执行搜索
        
        在当前标签页的数据中执行搜索操作。
        搜索是不区分大小写的，会在所有列中查找匹配项。
        如果没有找到匹配项，会显示提示信息并恢复显示所有数据。
        """
        search_text = self.search_var.get().lower()
        if not search_text:
            return
            
        current_tab = self.get_current_tab()
        if not hasattr(current_tab, 'tree'):
            return
            
        # 恢复所有项目的显示
        for item in current_tab.tree.get_children():
            current_tab.tree.reattach(item, '', 'end')
        
        # 隐藏不匹配的项目
        items_to_hide = []
        for item in current_tab.tree.get_children():
            values = [str(v).lower() for v in current_tab.tree.item(item)['values']]
            if not any(search_text in v for v in values):
                items_to_hide.append(item)
        
        # 从树中移除不匹配的项目
        for item in items_to_hide:
            current_tab.tree.detach(item)
        
        if not current_tab.tree.get_children():
            messagebox.showinfo("搜索结果", "未找到匹配项")
            # 恢复所有项目的显示
            for item in items_to_hide:
                current_tab.tree.reattach(item, '', 'end')

    def clear_search(self):
        """清除搜索
        
        清空搜索框并恢复显示所有数据。
        同时清除当前选中的项目。
        """
        self.search_var.set('')
        current_tab = self.get_current_tab()
        if hasattr(current_tab, 'tree'):
            # 恢复所有项目的显示
            for item in current_tab.tree.detached():
                current_tab.tree.reattach(item, '', 'end')
            # 清除选择
            current_tab.tree.selection_remove(*current_tab.tree.selection())

    def get_current_tab(self):
        """获取当前选项卡
        
        返回当前选中的标签页对象。
        如果没有选中的标签页，返回 None。
        """
        current = self.notebook.select()
        if current:
            return self.notebook.nametowidget(current)
        return None

    def create_tabs(self):
        """创建选项卡
        
        创建应用程序的主要标签页，包括：
        - 人物管理
        - 电影管理
        - 公司管理
        - 奖项管理
        """
        # 创建选项卡
        self.notebook = ttk.Notebook(self.main_frame, style="Custom.TNotebook")
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 创建各个选项卡
        self.people_tab = PeopleTab(self.notebook, self.refresh_logs)
        self.movies_tab = MoviesTab(self.notebook, self.refresh_logs)
        self.companies_tab = CompaniesTab(self.notebook, self.refresh_logs)
        self.awards_tab = AwardsTab(self.notebook, self.refresh_logs)

        self.notebook.add(self.people_tab, text="人物管理")
        self.notebook.add(self.movies_tab, text="电影管理")
        self.notebook.add(self.companies_tab, text="公司管理")
        self.notebook.add(self.awards_tab, text="奖项管理")

    def create_log_area(self):
        """创建日志区域
        
        创建用于显示操作日志的区域，包括：
        - 时间
        - 操作类型
        - 表名
        - 记录ID
        使用树形视图显示，支持滚动。
        """
        # 日志显示区域
        log_frame = ttk.LabelFrame(self.main_frame, text="操作日志", padding="10", style="Custom.TLabelframe")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 创建带滚动条的树形视图
        tree_frame = ttk.Frame(log_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.log_tree = ttk.Treeview(tree_frame, columns=("时间", "操作", "表", "记录ID"), show="headings", height=6)
        
        # 设置列宽和对齐方式
        self.log_tree.column("时间", width=250, anchor=tk.CENTER)
        self.log_tree.column("操作", width=120, anchor=tk.CENTER)
        self.log_tree.column("表", width=180, anchor=tk.CENTER)
        self.log_tree.column("记录ID", width=120, anchor=tk.CENTER)
        
        for col in ["时间", "操作", "表", "记录ID"]:
            self.log_tree.heading(col, text=col)

        # 添加滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.log_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.log_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def refresh_logs(self):
        """刷新日志
        
        从数据库获取最新的操作日志并显示。
        新的日志会显示在顶部。
        """
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        logs = db.get_operation_logs()
        for log in logs:
            self.log_tree.insert("", 0, values=(
                log['operation_time'],
                log['operation_type'],
                log['table_name'],
                log['record_id']
            ))

    def refresh_all(self):
        """刷新所有数据
        
        刷新所有标签页的数据显示。
        这个方法会在应用程序启动时调用，
        也可以在需要全局刷新时调用。
        """
        if hasattr(self, 'people_tab'):
            self.people_tab.refresh_data()
        if hasattr(self, 'movies_tab'):
            self.movies_tab.refresh_data()
        if hasattr(self, 'companies_tab'):
            self.companies_tab.refresh_data()
        if hasattr(self, 'awards_tab'):
            self.awards_tab.refresh_data()
