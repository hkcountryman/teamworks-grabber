import tkinter as tk

class AskDate():
    def __init__(self) -> None:
        self.response = "" # button that gets clicked
        self.window = tk.Tk() # pop-up window

        label = tk.Label(self.window, text="Which week are you updating?")
        wk0 = tk.Button(self.window, text="This week")
        wk0.configure(command=lambda btn=wk0: self.click(btn))
        wk1 = tk.Button(self.window, text="Next week")
        wk1.configure(command=lambda btn=wk1: self.click(btn))
        wk2 = tk.Button(self.window, text="Two weeks out")
        wk2.configure(command=lambda btn=wk2: self.click(btn))
        # Add everything to self.window and open it
        label.pack(side=tk.TOP)
        wk2.pack(side=tk.BOTTOM)
        wk1.pack(side=tk.BOTTOM)
        wk0.pack(side=tk.BOTTOM)
        self.window.mainloop()

    def click(self, button: tk.Button):
        self.response = button.cget("text")
        self.window.destroy()
