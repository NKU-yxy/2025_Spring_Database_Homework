# main.py
import tkinter as tk
from window import App

def main():
    root = tk.Tk()
    root.geometry("1000x1000")  # 设置更大的窗口尺寸以适应新的内容
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()



