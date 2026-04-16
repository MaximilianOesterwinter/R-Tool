import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path

from main import get_variable_names, run_analysis as execute_backend_analysis
from runtime_paths import BASE_DIR

BASE_DIR = Path(BASE_DIR)
PREPARED_DATA_DIR = BASE_DIR / "data" / "prepared"


def get_available_datasets():
    if not PREPARED_DATA_DIR.exists():
        return []

    return sorted(
        p.name for p in PREPARED_DATA_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".csv"
    )


def load_names(dataset_name: str):
    out_path = str(BASE_DIR / "variables.json")
    result = get_variable_names(out_path, dataset_name)

    if result.returncode != 0:
        raise RuntimeError(result.stderr or "Error while loading variables")

    with open(out_path, "r", encoding="utf-8") as f:
        return json.load(f)


root = tk.Tk()
root.title("R-Tool")
root.minsize(200, 200)
root.maxsize(1280, 1080)
root.geometry("800x800+50+50")

two_variables_needed = [
    "chi-square", "paired-t-test", "unpaired-t-test", "normality-test",
    "welch-test", "describeBy", "correlation", "mann-whitney-u-test"
]
more_variables_needed = ["logistic-regression", "linear-regression", "anova"]
one_variable_needed = ["describe"]

variable_entries = []
variable_names = {}
variable_display = []
display_to_name = {}

available_datasets = get_available_datasets()
selected_dataset = tk.StringVar()

if available_datasets:
    selected_dataset.set(available_datasets[0])
else:
    selected_dataset.set("")


def refresh_variable_mappings():
    global variable_names, variable_display, display_to_name

    dataset_name = selected_dataset.get().strip()
    if not dataset_name:
        variable_names = {}
        variable_display = []
        display_to_name = {}
        return

    variable_names = load_names(dataset_name) or {}
    variable_display = [f"{name}: {var_type}" for name, var_type in variable_names.items()]
    display_to_name = {f"{name}: {var_type}": name for name, var_type in variable_names.items()}


def clear_input_fields():
    global variable_entries
    for widget in input_frame.winfo_children():
        widget.destroy()
    variable_entries = []


def add_variable_field():
    combo = ttk.Combobox(input_frame, values=variable_display, state="readonly")
    tk.Label(input_frame, text=f"Variable {len(variable_entries) + 1}").pack()
    combo.pack(fill="x", padx=5, pady=2)

    if variable_display:
        combo.set("Select variable")
    else:
        combo.set("No variables available")

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
        tk.Button(input_frame, text="Additional variables", command=add_variable_field).pack(pady=5)


def on_dataset_change(event=None):
    try:
        refresh_variable_mappings()
        update_input_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def run_analysis():
    analysis = combobox.get()
    dataset_name = selected_dataset.get().strip()

    if not dataset_name:
        messagebox.showerror("Error", "Please select a prepared dataset.")
        return

    variables = []
    for entry in variable_entries:
        display_value = entry.get()
        if display_value in display_to_name:
            variables.append(display_to_name[display_value])

    try:
        result = execute_backend_analysis(analysis, variables, dataset_name)

        if result.returncode != 0:
            raise RuntimeError(result.stderr or "Unknown error in the R script.")

        messagebox.showinfo("Success", result.stdout or "Analysis executed successfully.")

    except Exception as e:
        messagebox.showerror("Error", str(e))


combobox = ttk.Combobox(
    root,
    values=[
        "dataframe", "describe", "describeBy", "anova", "chi-square", "logistic-regression",
        "linear-regression", "paired-t-test", "unpaired-t-test", "normality-test",
        "welch-test", "correlation", "mann-whitney-u-test"
    ],
    state="readonly"
)
combobox.set("Select Analysis")
combobox.pack(fill="x", padx=5, pady=5)
combobox.bind("<<ComboboxSelected>>", update_input_fields)

input_frame = tk.Frame(root)
input_frame.pack(fill="x", padx=5, pady=5)

bottom_frame = tk.Frame(root)
bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

dataset_label = tk.Label(bottom_frame, text="Prepared dataset:")
dataset_label.pack(side="right", padx=(5, 0))

dataset_combobox = ttk.Combobox(
    bottom_frame,
    textvariable=selected_dataset,
    values=available_datasets,
    state="readonly",
    width=35
)
dataset_combobox.pack(side="right")
dataset_combobox.bind("<<ComboboxSelected>>", on_dataset_change)

tk.Button(root, text="Execute analysis", command=run_analysis).pack(pady=10)

refresh_variable_mappings()
update_input_fields()

root.mainloop()