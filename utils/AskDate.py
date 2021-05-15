import tkinter as tk

class AskDate():
    def __init__(self) -> None:
        self.window = tk.Tk() # pop-up window
        self.response = tk.StringVar(value="This week") # button that gets clicked

        # Configure window:
        self.window.title("Choose a week")
        def disable():
            pass
        self.window.protocol("WM_DELETE_WINDOW", disable)

        # Window contents:
        label = tk.Frame(borderwidth=10)
        text = tk.Label(master=label, text="Which week are you updating?")
        wk0 = tk.Radiobutton(
            text="This week",
            variable=self.response,
            value="This week"
        )
        wk1 = tk.Radiobutton(
            text="Next week",
            variable=self.response,
            value="Next week"
        )
        wk2 = tk.Radiobutton(
            text="Two weeks out",
            variable=self.response,
            value="Two weeks out"
        )
        buttons = tk.Frame(borderwidth=10)
        cancel = tk.Button(master=buttons, text="Cancel", command=exit)
        def close():
            self.window.destroy()
        submit = tk.Button(master=buttons, text="Submit", command=close)

        # Add everything to self.window and open it
        text.pack()
        label.pack(side=tk.TOP)
        cancel.pack(side=tk.LEFT, padx=10)
        submit.pack(side=tk.RIGHT, padx=10)
        buttons.pack(side=tk.BOTTOM)
        #cancel.pack(anchor=tk.W, side=tk.BOTTOM)
        #submit.pack(anchor=tk.W, side=tk.BOTTOM)
        wk2.pack(anchor=tk.W, side=tk.BOTTOM)
        wk1.pack(anchor=tk.W, side=tk.BOTTOM)
        wk0.pack(anchor=tk.W, side=tk.BOTTOM)
        self.window.mainloop()
