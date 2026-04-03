import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import subprocess
import json
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY = os.path.join(BASE_DIR, "main.py")

def load_names():
    out_path = os.path.join(BASE_DIR, "variables.json")

    subprocess.run(
        [
            sys.executable,
            MAIN_PY,
            "get_variables",
            out_path
        ], 
        check=True,
        capture_output=True,
        text=True
    )

    with open(out_path, "r", encoding="utf-8") as f:
        return json.load(f)

root = tk.Tk()

root.title("R-Tool")
root.minsize(200, 200)
root.maxsize(1280, 1080)
root.geometry("800x800+50+50")

two_variables_needed = ["chi_square", 
                        "paired_ttest", 
                        "unpaired_ttest", 
                        "norm_test", 
                        "welch_test", 
                        "describeBy", 
                        "correlation", 
                        "mann_whitney_test"
                        ]
more_variables_needed = ["logit", "lin_reg", "anova"]
one_variable_needed = ["describe"]

variable_entries = []
variable_names = load_names() or []
variable_display = [
    f"{name}: {var_type}"
    for name, var_type in variable_names.items()
]
display_to_name = {
    f"{name}: {var_type}": name
    for name, var_type in variable_names.items()
}

def clear_input_fields():
    global variable_entries
    for widget in input_frame.winfo_children():
        widget.destroy()
    variable_entries = []

def add_variable_field():
    combo = ttk.Combobox(input_frame, values=variable_display, state="readonly")
    tk.Label(input_frame, text=f"Variable {len(variable_entries) + 1}").pack()
    combo.pack(fill="x", padx=5, pady=2)
    combo.set("Select variable")
    variable_entries.append(combo)

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

        add_button = tk.Button(input_frame, text="Additional variables", command=add_variable_field)
        add_button.pack(pady=5)

def run_analysis():
    analysis = combobox.get()

    selected_displays = [
        entry.get().strip()
        for entry in variable_entries
    ]
    if any(value == "Select variable" or not value for value in selected_displays):
        messagebox.showwarning("Missing input", "Please select all required variables.")
        return

    variables = [display_to_name[display] 
                for display in selected_displays
                ]

    command = [sys.executable, MAIN_PY, analysis, *variables]
    print(command)  # zum Debuggen
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        messagebox.showinfo("Success", result.stdout or "Analysis executed successfully.")
    except subprocess.CalledProcessError as e:
        print("RETURN CODE:", e.returncode)
        print("STDOUT", e.stdout)
        print("STDERR", e.stderr)
        messagebox.showerror(
            "Error",
            e.stderr or e.stdout or str(e)
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))

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
        "norm_test",
        "welch_test",
        "correlation",
        "mann_whitney_test"
    ]
)
combobox.set("df")
combobox.pack(fill="x", padx=5, pady=5)
combobox.bind("<<ComboboxSelected>>", update_input_fields)

input_frame = tk.Frame(root)
input_frame.pack(fill="x", padx=5, pady=5)

tk.Button(root, text="Execute analysis", command=run_analysis).pack(pady=10)

update_input_fields()

root.mainloop()