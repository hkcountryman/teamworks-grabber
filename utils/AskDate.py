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
        label = tk.Label(self.window, text="Which week are you updating?")
        wk0 = tk.Radiobutton(
            self.window,
            text="This week",
            variable=self.response,
            value="This week"
        )
        wk1 = tk.Radiobutton(
            self.window,
            text="Next week",
            variable=self.response,
            value="Next week"
        )
        wk2 = tk.Radiobutton(
            self.window,
            text="Two weeks out",
            variable=self.response,
            value="Two weeks out"
        )
        cancel = tk.Button(self.window, text="Cancel", command=exit)
        def close():
            self.window.destroy()
        submit = tk.Button(self.window, text="Submit", command=close)

        # Add everything to self.window and open it
        label.pack(side=tk.TOP)
        cancel.pack(side=tk.BOTTOM)
        submit.pack(side=tk.BOTTOM)
        wk2.pack(side=tk.BOTTOM)
        wk1.pack(side=tk.BOTTOM)
        wk0.pack(side=tk.BOTTOM)
        self.window.mainloop()
