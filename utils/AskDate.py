import tkinter as tk

class AskDate():
    def __init__(self) -> None:
        self.response = "" # button that gets clicked

        def click(button: tk.Button):
            self.response = button.cget("text")
            window.destroy()
        
        window = tk.Tk()
        label = tk.Label(window, text="Couldn't read date.\nWhich week are you updating?")
        wk0 = tk.Button(window, text="This week")
        wk0.bind("<Button-1>", lambda: click(wk0))
        wk1 = tk.Button(window, text="Next week")
        wk1.bind("<Button-1>", lambda: click(wk1))
        wk2 = tk.Button(window, text="Two weeks out")
        wk2.bind("<Button-1>", lambda: click(wk2))
        # Add everything to window and open it
        label.pack(side=tk.TOP)
        wk2.pack(side=tk.BOTTOM)
        wk1.pack(side=tk.BOTTOM)
        wk0.pack(side=tk.BOTTOM)
        window.mainloop()
