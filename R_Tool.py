import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path

from main import get_variable_names, run_analysis, run_plot
from runtime_paths import BASE_DIR

BASE_DIR = Path(BASE_DIR)
PREPARED_DATA_DIR = BASE_DIR / "data" / "prepared"


METHOD_CONFIG = {
    "analysis": {
        "df": {"label": "Dataframe", "var_count": 0},
        "describe": {"label": "Describe", "var_count": 1},
        "describeBy": {"label": "Describe By", "var_count": 2},
        "anova": {"label": "ANOVA", "var_count": "multiple"},
        "chi_square": {"label": "Chi Square", "var_count": 2},
        "logit": {"label": "Logit Model", "var_count": "multiple"},
        "lin_reg": {"label": "Linear Regression", "var_count": "multiple"},
        "paired_ttest": {"label": "Paired t-test", "var_count": 2},
        "unpaired_ttest": {"label": "Unpaired t-test", "var_count": 2},
        "norm_test": {"label": "Normality Test", "var_count": 2},
        "welch_test": {"label": "Welch Test", "var_count": 2},
        "correlation": {"label": "Correlation", "var_count": 2},
        "mann_whitney_test": {"label": "Mann-Whitney Test", "var_count": 2},
    },
    "plot": {
        "histogram": {"label": "Histogram", "var_count": 1},
        "boxplot": {"label": "Boxplot", "var_count": 1},
        "boxplot_by_group": {"label": "Boxplot by Group", "var_count": 2},
        "scatterplot": {"label": "Scatterplot", "var_count": 2},
        "barplot": {"label": "Barplot", "var_count": 1},
        "barplot_by_group": {"label": "Barplot by Group", "var_count": 2},
        "lineplot": {"label": "Lineplot", "var_count": 2},
    }
}


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


class RToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("R-Tool")
        self.root.minsize(300, 300)
        self.root.maxsize(1280, 1080)
        self.root.geometry("900x850+50+50")

        self.variable_entries = []
        self.variable_names = {}
        self.variable_display = []
        self.display_to_name = {}

        self.available_datasets = get_available_datasets()

        self.selected_dataset = tk.StringVar()
        self.mode_var = tk.StringVar(value="analysis")

        if self.available_datasets:
            self.selected_dataset.set(self.available_datasets[0])
        else:
            self.selected_dataset.set("")

        self.build_ui()
        self.refresh_variable_mappings()
        self.refresh_method_dropdown()
        self.update_input_fields()

    def build_ui(self):
        self.method_combobox = ttk.Combobox(self.root, state="readonly")
        self.method_combobox.pack(fill="x", padx=8, pady=8)
        self.method_combobox.bind("<<ComboboxSelected>>", self.update_input_fields)

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill="x", padx=8, pady=8)

        self.execute_button = tk.Button(
            self.root,
            text="Execute",
            command=self.execute_selected_action
        )
        self.execute_button.pack(pady=10)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.mode_frame = tk.Frame(self.bottom_frame)
        self.mode_frame.pack(side="left")

        tk.Radiobutton(
            self.mode_frame,
            text="Analysis",
            variable=self.mode_var,
            value="analysis",
            command=self.on_mode_change
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            self.mode_frame,
            text="Graphics",
            variable=self.mode_var,
            value="plot",
            command=self.on_mode_change
        ).pack(side="left", padx=5)

        self.dataset_label = tk.Label(self.bottom_frame, text="Prepared dataset:")
        self.dataset_label.pack(side="right", padx=(5, 0))

        self.dataset_combobox = ttk.Combobox(
            self.bottom_frame,
            textvariable=self.selected_dataset,
            values=self.available_datasets,
            state="readonly",
            width=35
        )
        self.dataset_combobox.pack(side="right")
        self.dataset_combobox.bind("<<ComboboxSelected>>", self.on_dataset_change)

    def refresh_variable_mappings(self):
        dataset_name = self.selected_dataset.get().strip()

        if not dataset_name:
            self.variable_names = {}
            self.variable_display = []
            self.display_to_name = {}
            return

        self.variable_names = load_names(dataset_name) or {}
        self.variable_display = [
            f"{name}: {var_type}" for name, var_type in self.variable_names.items()
        ]
        self.display_to_name = {
            f"{name}: {var_type}": name for name, var_type in self.variable_names.items()
        }

    def refresh_method_dropdown(self):
        mode = self.mode_var.get()
        method_labels = [
            config["label"] for config in METHOD_CONFIG[mode].values()
        ]   
        self.method_combobox["values"] = method_labels

        self.label_to_method = {
            config["label"]: key
            for key, config in METHOD_CONFIG[mode].items()
        }

        if method_labels:
            self.method_combobox.set(method_labels[0])
        else:
            self.method_combobox.set("")
        

    def clear_input_fields(self):
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.variable_entries = []

    def add_variable_field(self):
        label = tk.Label(self.input_frame, text=f"Variable {len(self.variable_entries) + 1}")
        label.pack(anchor="w")

        combo = ttk.Combobox(
            self.input_frame,
            values=self.variable_display,
            state="readonly"
        )
        combo.pack(fill="x", padx=5, pady=2)

        if self.variable_display:
            combo.set("Select variable")
        else:
            combo.set("No variables available")

        self.variable_entries.append(combo)

    def add_additional_variable_button(self):
        button = tk.Button(
            self.input_frame,
            text="Additional variables",
            command=self.add_variable_field
        )
        button.pack(pady=5)

    def update_input_fields(self, event=None):
        self.clear_input_fields()

        mode = self.mode_var.get()
        selected_label = self.method_combobox.get()
        method = self.label_to_method.get(selected_label)

        if not method:
            return

        config = METHOD_CONFIG[mode].get(method)

        var_count = config["var_count"]

        if var_count == 0:
            return
        if var_count == 1:
            self.add_variable_field()
            return
        if var_count == 2:
            self.add_variable_field()
            self.add_variable_field()
            return
        if var_count == "multiple":
            self.add_variable_field()
            self.add_variable_field()
            self.add_additional_variable_button()

    def collect_selected_variables(self):
        variables = []

        for entry in self.variable_entries:
            display_value = entry.get().strip()

            if not display_value or display_value in ("Select variable", "No variables available"):
                continue

            if display_value in self.display_to_name:
                variables.append(self.display_to_name[display_value])

        return variables

    def validate_variable_count(self, mode, method, variables):
        config = METHOD_CONFIG[mode][method]
        var_count = config["var_count"]

        if var_count == 0:
            return

        if var_count == 1 and len(variables) < 1:
            raise ValueError("Please select 1 variable.")

        if var_count == 2 and len(variables) < 2:
            raise ValueError("Please select 2 variables.")

        if var_count == "multiple" and len(variables) < 2:
            raise ValueError("Please select at least 2 variables.")

    def on_mode_change(self):
        self.refresh_method_dropdown()
        self.update_input_fields()

    def on_dataset_change(self, event=None):
        try:
            self.refresh_variable_mappings()
            self.update_input_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def execute_selected_action(self):
        dataset_name = self.selected_dataset.get().strip()
        mode = self.mode_var.get()
        selected_label = self.method_combobox.get()
        method = self.label_to_method.get(selected_label)
        variables = self.collect_selected_variables()

        try:
            if not dataset_name:
                raise ValueError("Please select a prepared dataset.")

            if not method:
                raise ValueError("Please select a method.")

            self.validate_variable_count(mode, method, variables)

            if mode == "analysis":
                result = run_analysis(method, variables, dataset_name)
            elif mode == "plot":
                result = run_plot(method, variables, dataset_name)
            else:
                raise ValueError(f"Unknown mode: {mode}")

            if result.returncode != 0:
                raise RuntimeError(result.stderr or "Unknown backend error.")

            messagebox.showinfo("Success", result.stdout or "Action executed successfully.")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = RToolGUI(root)
    root.mainloop()