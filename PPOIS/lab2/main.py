import tkinter as tk
from controller import Controller

if __name__ == '__main__':
    root = tk.Tk()
    root.title("")
    root.geometry("1920x1080")
    app = Controller(root)
    root.mainloop()