"""
Application Description:
    TBD
"""


import tkinter as tk

# Create a new Tkinter window
window = tk.Tk()

# Set the window title
window.title("My Tkinter Application")

# Set the size of the window
window.geometry("400x300")

# Create a label widget
label = tk.Label(window, text="Hello, Tkinter!")

# Pack the label widget to display it in the window
label.pack()

# Start the Tkinter event loop
window.mainloop()