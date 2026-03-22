import tkinter as tk
from tkinter import ttk
import subprocess

root = tk.Tk()

root.title("R-Tool")
root.minsize(200, 200)
root.maxsize(1280, 1080)
root.geometry("800x800+50+50")

two_variables_needed = ["chi_square", "paired_ttest", "unpaired_ttest", "norm_ttest", "welch_test", "describeBy"]
more_variables_needed = ["logit", "lin_reg", "anova"]
one_variable_needed = ["describe"]

variable_entries = []

def clear_input_fields():
    global variable_entries
    for widget in input_frame.winfo_children():
        widget.destroy()
    variable_entries = []

def add_variable_field():
    entry = tk.Entry(input_frame)
    tk.Label(input_frame, text=f"Variable {len(variable_entries) + 1}").pack()
    entry.pack(fill="x", padx=5, pady=2)
    variable_entries.append(entry)

def update_input_fields(event=None):
    analysis = combobox.get()
    clear_input_fields()

    if analysis in one_variable_needed:
        add_variable_field()

    elif analysis in two_variables_needed:
        add_variable_field()
        add_variable_field()

    elif analysis in more_variables_needed:
        add_variable_field()
        add_variable_field()

        add_button = tk.Button(input_frame, text="Weitere Variable", command=add_variable_field)
        add_button.pack(pady=5)

def run_analysis():
    analysis = combobox.get()
    variables = [entry.get().strip() for entry in variable_entries if entry.get().strip()]

    command = ["python", "main.py", analysis, *variables]
    print(command)  # zum Debuggen
    subprocess.run(command)

combobox = ttk.Combobox(
    root,
    values=[
        "df",
        "describe",
        "describeBy",
        "anova",
        "chi_square",
        "logit",
        "lin_reg",
        "paired_ttest",
        "unpaired_ttest",
        "norm_ttest",
        "welch_test"
    ]
)
combobox.set("df")
combobox.pack(fill="x", padx=5, pady=5)
combobox.bind("<<ComboboxSelected>>", update_input_fields)

input_frame = tk.Frame(root)
input_frame.pack(fill="x", padx=5, pady=5)

tk.Button(root, text="Analyse ausführen", command=run_analysis).pack(pady=10)

update_input_fields()

root.mainloop()