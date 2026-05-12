import tkinter as tk
from tkinter import ttk, messagebox
import json
import webbrowser
from pathlib import Path

from version import APP_VERSION
from update_check import is_newer_version_available
from main import get_variable_names, run_analysis, run_plot, run_preparation
from runtime_paths import BASE_DIR

BASE_DIR = Path(BASE_DIR)
PREPARED_DATA_DIR = BASE_DIR / "data" / "prepared"

def check_for_updates():
    is_newer, release = is_newer_version_available(APP_VERSION)
    if not is_newer or not release:
        return
    
    latest_tag = release.get("tag_name", "unknown")
    html_url = release.get("html_url", "")
    body = release.get("body", "")

    msg = (
        f"A new version is available.\n\n"
        f"Installed: v{APP_VERSION}\n"
        f"New: {latest_tag}\n\n"
        f"Open release-page?"
    )

    if messagebox.askyesno("Update available", msg):
        if html_url:
            webbrowser.open(html_url)

METHOD_CONFIG = {
    "analysis": {
        "df": {"label": "Dataframe", "var_count": 0},
        "describe": {"label": "Describe", "var_count": 1},
        "describeBy": {"label": "Describe By", "var_count": "dep_group"},
        "anova": {"label": "ANOVA", "var_count": "multiple"},
        "chi_square": {"label": "Chi Square", "var_count": 2},
        "logit": {"label": "Logit Model", "var_count": "multiple"},
        "lin_reg": {"label": "Linear Regression", "var_count": "multiple"},
        "paired_ttest": {"label": "Paired t-test", "var_count": 2},
        "unpaired_ttest": {"label": "Unpaired t-test", "var_count": "var_const"},
        "norm_test": {"label": "Normality Test", "var_count": "dep_group"},
        "welch_test": {"label": "Welch Test", "var_count": "dep_group"},
        "correlation": {"label": "Correlation", "var_count": 2},
        "mann_whitney_test": {"label": "Mann-Whitney Test", "var_count": "dep_group"},
    },
    "plot": {
        "histogram": {"label": "Histogram", "var_count": "x"},
        "boxplot": {"label": "Boxplot", "var_count": "x"},
        "boxplot_by_group": {"label": "Boxplot by Group", "var_count": "grouped"},
        "scatterplot": {"label": "Scatterplot", "var_count": "xy"},
        "barplot": {"label": "Barplot", "var_count": "y"},
        "barplot_by_group": {"label": "Barplot by Group", "var_count": "grouped"},
        "lineplot": {"label": "Lineplot", "var_count": "xy"},
    },
    "preparation": {
        "subframe": {"label": "Create a subframe", "var_count": "subframe"},
        "factorize": {"label": "Factorize variable", "var_count": "factorize"},
        "rename": {"label": "Rename variables", "var_count": "rename"},
        "mutate": {"label": "Mutate variables", "var_count": "mutate"},
    }
}


def get_available_datasets():
    if not PREPARED_DATA_DIR.exists():
        return []

    return sorted(
        p.name for p in PREPARED_DATA_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".rds"
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
        self.root.title("R-Tool version 1.3.0")
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
        self.pivot_longer_var = tk.BooleanVar(value=False)
        self.remove_na_var = tk.BooleanVar(value=False)
        self.subframe_name_var = tk.StringVar()
        self.factor_levels_var = tk.StringVar()
        self.factor_labels_var = tk.StringVar()
        self.rename_entries = []

        self.mutate_new_var_name = tk.StringVar()
        self.mutate_operation_var = tk.StringVar()
        self.mutate_operator_var = tk.StringVar()
        self.mutate_na_rm_var = tk.BooleanVar(value=False)
        self.mutate_variable_entries = []
        self.recode_entries = []
        self.reverse_min_var = tk.StringVar()
        self.reverse_max_var = tk.StringVar()
        self.mutate_operations = {
            "Arithmetic": "arithmetic",
            "Row mean": "row_mean",
            "Row sum": "row_sum",
            "Log": "log",
            "Z-standardize": "z_standardize",
            "Reverse scale": "reverse_scale",
            "Recode / case_when": "recode"
        }

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
            text="Plots",
            variable=self.mode_var,
            value="plot",
            command=self.on_mode_change
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            self.mode_frame,
            text="Preparation",
            variable=self.mode_var,
            value="preparation",
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

    def refresh_dataset_list(self):
        self.dataset_names = get_available_datasets()
        self.dataset_combobox["values"] = self.dataset_names

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

    def add_variable_field(self, parent=None):
        if parent is None:
            parent = self.input_frame
        
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=5, pady=5)

        label = ttk.Label(
            frame, 
            text=f"Variable {len(self.variable_entries) + 1}"
        )
        label.pack(anchor="w")

        combo = ttk.Combobox(
            frame,
            values=self.variable_display,
            state="readonly"
        )
        combo.pack(fill="x", padx=5, pady=2)

        if self.variable_display:
            combo.set("Select variable")
        else:
            combo.set("No variables available")

        self.variable_entries.append(combo)
    
    def add_variable_field_x(self):
        label = tk.Label(self.input_frame, text="Variable x-axis")
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
    
    def add_variable_field_y(self):
        label = tk.Label(self.input_frame, text="Variable y-axis")
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
    
    def add_variable_field_grouping(self):
        label = tk.Label(self.input_frame, text="Grouping variable")
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
    
    def add_variable_field_dependent(self):
        label = tk.Label(self.input_frame, text="Dependent variable")
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
    
    def add_variable_field_independent(self):
        label = tk.Label(self.input_frame, text="Independent variable")
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
    
    def add_variable_field_write(self):
        label = tk.Label(self.input_frame, text="Variable or constant")
        label.pack(anchor="w")

        combo = ttk.Combobox(
            self.input_frame,
            values=self.variable_display
        )
        combo.pack(fill="x", padx=5, pady=2)

        if self.variable_display:
            combo.set("Select variable or enter constant")
        else:
            combo.set("No variables available")

        self.variable_entries.append(combo)

    def add_additional_variable_button(self, parent=None):
        if parent is None:
            parent = self.input_frame

        button = tk.Button(
            parent,
            text="Additional variables",
            command=self.add_variable_field
        )
        button.pack(pady=5)
    
    def add_pivot_longer_checkbox(self):
        check = ttk.Checkbutton(
            self.input_frame,
            text="Use pivot_longer()",
            variable=self.pivot_longer_var
        )
        check.pack(anchor="w", padx=5, pady=5)
    
    def add_remove_na_checkbox(self):
        check = ttk.Checkbutton(
            self.input_frame,
            text="Remove NA's",
            variable=self.remove_na_var
        )
        check.pack(anchor="w", padx=5, pady=5)
    
    def add_subframe_name_field(self):
        frame = ttk.Frame(self.input_frame)
        frame.pack(fill="x", padx=5, pady=5)

        label = ttk.Label(frame, text="New subframe name:")
        label.pack(side="left")

        entry = ttk.Entry(
            frame,
            textvariable=self.subframe_name_var
        )
        entry.pack(side="left", fill="x", expand=True, padx=5)
    
    def add_factorize_fields(self):
        self.add_variable_field()
        self.add_additional_variable_button()

        levels_label = tk.Label(
            self.input_frame,
            text="Levels, separated by comma, e.g. 1,2,3"
        )
        levels_label.pack(anchor="w")

        levels_entry = ttk.Entry(
            self.input_frame,
            textvariable=self.factor_levels_var
        )
        levels_entry.pack(fill="x", padx=5, pady=2)

        labels_label = tk.Label(
            self.input_frame,
            text="Labels, separated by comma, e.g. low,medium,high"
        )
        labels_label.pack(anchor="w")

        labels_entry = ttk.Entry(
            self.input_frame,
            textvariable=self.factor_labels_var
        )
        labels_entry.pack(fill="x", padx=5, pady=2)
    
    def add_rename_pair_field(self):
        frame = ttk.Frame(self.input_frame)
        frame.pack(fill="x", padx=5, pady=5)

        old_var = tk.StringVar()
        new_var = tk.StringVar()

        old_menu = ttk.Combobox(
            frame,
            textvariable=old_var,
            values=self.variable_display,
            state="readonly"
        )
        old_menu.pack(side="left", fill="x", expand=True, padx=2)

        new_entry = ttk.Entry(
            frame,
            textvariable=new_var
        )
        new_entry.pack(side="left", fill="x", expand=True, padx=2)

        self.rename_entries.append((old_var, new_var))
    
    def add_rename_fields(self):
        self.rename_entries = []

        self.add_rename_pair_field()

        add_button = ttk.Button(
            self.input_frame,
            text="Add variable to rename",
            command=self.add_rename_pair_field
        )
        add_button.pack(pady=5)
    
    def add_mutation_fields(self):
        frame = ttk.Frame(self.input_frame)
        frame.pack(fill="x", padx=5, pady=5)

        label = ttk.Label(frame, text="Name for the new variable:")
        label.pack(side="left")

        entry = ttk.Entry(
            frame,
            textvariable=self.mutate_new_var_name
        )
        entry.pack(side="left", fill="x", expand=True, padx=5)


        label = tk.Label(self.input_frame, text="Operation:")
        label.pack(anchor="w", padx=5, pady=(10, 0))

        combo = ttk.Combobox(
            self.input_frame,
            textvariable=self.mutate_operation_var,
            values=list(self.mutate_operations.keys()),
            state="readonly"
        )
        combo.pack(fill="x", padx=5, pady=2)

        combo.bind(
            "<<ComboboxSelected>>",
            self.update_mutation_operation_fields
        )

        self.mutation_dynamic_frame = ttk.Frame(self.input_frame)
        self.mutation_dynamic_frame.pack(fill="x", padx=5, pady=5)
    
    def update_mutation_operation_fields(self, event=None):
        for widget in self.mutation_dynamic_frame.winfo_children():
            widget.destroy()
        
        self.variable_entries = []
        self.mutate_operator_var.set("")
        self.mutate_na_rm_var.set(False)
        self.reverse_min_var.set("")
        self.reverse_max_var.set("")
        
        operation_label = self.mutate_operation_var.get()
        operation = self.mutate_operations.get(operation_label)

        if operation == "arithmetic":
            self.add_variable_field(parent=self.mutation_dynamic_frame)

            operator_label = ttk.Label(self.mutation_dynamic_frame, text="Operator:")
            operator_label.pack(anchor="w", padx=5)

            operator_combo = ttk.Combobox(
                self.mutation_dynamic_frame,
                textvariable=self.mutate_operator_var,
                values=["+", "-", "*", "/", "^"],
                state="readonly"
            )
            operator_combo.pack(fill="x")

            self.add_variable_field(parent=self.mutation_dynamic_frame)

        elif operation in ["row_mean", "row_sum"]:
            self.add_variable_field(parent=self.mutation_dynamic_frame)
            self.add_variable_field(parent=self.mutation_dynamic_frame)

            self.add_additional_variable_button(
                parent=self.mutation_dynamic_frame
            )   

            check = ttk.Checkbutton(
                self.mutation_dynamic_frame,
                text="Remove NAs",
                variable=self.mutate_na_rm_var
            )
            check.pack(anchor="w", padx=5, pady=5)
        
        elif operation in ["log", "z_standardize"]:
            self.add_variable_field(parent=self.mutation_dynamic_frame)
        
        elif operation == "reverse_scale":
            self.add_variable_field(parent=self.mutation_dynamic_frame)

            min_label = ttk.Label(
                self.mutation_dynamic_frame,
                text="Minimum scale value:"
            )
            min_label.pack(anchor="w", padx=5)

            min_entry = ttk.Entry(
                self.mutation_dynamic_frame,
                textvariable=self.reverse_min_var
            )
            min_entry.pack(fill="x", padx=5, pady=2)

            max_label = ttk.Label(
                self.mutation_dynamic_frame,
                text="Maximum scale value:"
            )
            max_label.pack(anchor="w", padx=5)

            max_entry = ttk.Entry(
                self.mutation_dynamic_frame,
                textvariable=self.reverse_max_var
            )
            max_entry.pack(fill="x", padx=5, pady=2)
        
        elif operation == "recode":
            self.add_variable_field(parent=self.mutation_dynamic_frame)

            self.recode_rules_frame = ttk.Frame(self.mutation_dynamic_frame)
            self.recode_rules_frame.pack(fill="x", pady=5)

            self.add_recode_rule_field()

            button = ttk.Button(
                self.mutation_dynamic_frame,
                text="Add recode rule",
                command=self.add_recode_rule_field
            )
            button.pack(pady=5)
    
    def add_recode_rule_field(self):
        frame = ttk.Frame(self.recode_rules_frame)
        frame.pack(fill="x", pady=2)

        old_var = tk.StringVar()
        new_var = tk.StringVar()

        old_entry = ttk.Entry(
            frame,
            textvariable=old_var
        )
        old_entry.pack(side="left", fill="x", expand=True, padx=2)

        new_entry = ttk.Entry(
            frame,
            textvariable=new_var
        )
        new_entry.pack(side="left", fill="x", expand=True, padx=2)

        self.recode_entries.append((old_var, new_var))
    
    def refresh_after_preparation(self, selected_dataset: str | None = None):
        self.refresh_dataset_list()

        if selected_dataset:
            self.selected_dataset.set(selected_dataset)
        
        self.refresh_variable_mappings()
        self.update_input_fields()

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
        if var_count == "x":
            self.add_variable_field_x()
        if var_count == "y":
            self.add_variable_field_y()
        if var_count == "xy":
            self.add_variable_field_y()
            self.add_variable_field_x()
        if var_count == "grouped":
            self.add_variable_field()
            self.add_variable_field_grouping()
        if var_count == "dep_group":
            self.add_variable_field_dependent()
            self.add_variable_field_grouping()
        if var_count == "var_const":
            self.add_variable_field()
            self.add_variable_field_write()
        if var_count == "subframe":
            self.pivot_longer_var.set(False)
            self.remove_na_var.set(False)
            self.subframe_name_var.set("")

            self.add_subframe_name_field()
            self.add_variable_field()
            self.add_additional_variable_button()
            self.add_pivot_longer_checkbox()
            self.add_remove_na_checkbox()
            return
        if var_count == "factorize":
            self.factor_levels_var.set("")
            self.factor_labels_var.set("")

            self.add_factorize_fields()
            return
        if var_count == "rename":
            self.add_rename_fields()
            return
        if var_count == "mutate":
            self.variable_entries = []

            self.mutate_new_var_name.set("")
            self.mutate_operation_var.set("")
            self.mutate_operator_var.set("")
            self.mutate_na_rm_var.set(False)
            self.reverse_min_var.set("")
            self.reverse_max_var.set("")

            self.add_mutation_fields()
            return

    def collect_selected_variables(self):
        variables = []

        for entry in self.variable_entries:
            value = entry.get().strip()

            if not value or value in (
                "Select variable",
                "No variables available",
                "Select variable or enter constant"
            ):
                continue

            if value in self.display_to_name:
                variables.append(self.display_to_name[value])
            else:
                variables.append(value)

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
            elif mode == "preparation":
                if method == "subframe":
                    if not self.subframe_name_var.get().strip():
                        messagebox.showerror(
                            "Error",
                            "Please enter a subframe name."
                        )
                        return
                    result = run_preparation(
                        method, 
                        variables, 
                        dataset_name, 
                        subframe_name=self.subframe_name_var.get().strip(), 
                        pivot_longer=self.pivot_longer_var.get(),
                        remove_na=self.remove_na_var.get()
                    )

                elif method == "factorize":
                    if not self.factor_levels_var.get().strip():
                        raise ValueError("Please enter factor levels")
                    if not self.factor_labels_var.get().strip():
                        raise ValueError("Please enter factor labels")
                    result = run_preparation(
                        method,
                        variables,
                        dataset_name,
                        levels=self.factor_levels_var.get().strip(),
                        labels=self.factor_lebels_var.get().strip()
                    )
                elif method == "rename":
                    rename_pairs = []
                    
                    for old_var, new_var in self.rename_entries:
                        selected_display = old_var.get().strip()
                        old_name = self.display_to_name.get(selected_display)
                        new_name = new_var.get().strip()

                        if " " in new_name:
                            messagebox.showerror(
                                "Error",
                                "Variable names should not contain spaces."
                            )
                            return

                        if old_name and new_name:
                            rename_pairs.append(f"{old_name}={new_name}")
                    
                    if not rename_pairs:
                        messagebox.showerror(
                            "Error",
                            "Please select at least one variable and enter a new name."
                        )
                        return
                    
                    result = run_preparation(
                        method,
                        variables=[],
                        dataset_name=dataset_name,
                        rename_pairs=rename_pairs
                    )
                elif method == "mutate":
                    new_var_name = self.mutate_new_var_name.get().strip()

                    if not new_var_name:
                        messagebox.showerror(
                            "Error",
                            "Please enter a name for the new variable."
                        )
                        return
                    
                    if " " in new_var_name:
                        messagebox.showerror(
                            "Error",
                            "Variable names should not contain spaces."
                        )
                        return
                    
                    operation_label = self.mutate_operation_var.get()
                    operation = self.mutate_operations.get(operation_label)

                    if not operation:
                        messagebox.showerror(
                            "Error",
                            "Please select a mutate operation."
                        )
                        return
                    
                    if operation == "arithmetic" and not self.mutate_operator_var.get():
                        messagebox.showerror(
                            "Error",
                            "Please select an arithmetic operator."
                        )
                        return
                    
                    if operation == "reverse_scale":
                        if not self.reverse_min_var.get().strip() or not self.reverse_max_var.get().strip():
                            messagebox.showerror(
                                "Error",
                                "Please enter minimum and maximum scale values."
                            )
                            return
                    result = run_preparation(
                        method,
                        variables,
                        dataset_name,
                        new_var_name=new_var_name,
                        mutate_operation=operation,
                        mutate_operator=self.mutate_operator_var.get(),
                        na_rm=self.mutate_na_rm_var.get(),
                        reverse_min=self.reverse_min_var.get().strip(),
                        reverse_max=self.reverse_max_var.get().strip()
                    )

                if result.returncode == 0:
                    if method == "subframe":
                        new_dataset_name = f"{self.subframe_name_var.get().strip()}.rds"
                        self.refresh_after_preparation(
                            selected_dataset=new_dataset_name
                        )
                    else:
                        self.refresh_after_preparation(
                            selected_dataset=self.selected_dataset.get()
                        )
                
                
            else:
                raise ValueError(f"Unknown mode: {mode}")

            if result.returncode != 0:
                raise RuntimeError(result.stderr or "Unknown backend error.")

            messagebox.showinfo("Success", result.stdout or "Action executed successfully.")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    root.after(500, check_for_updates)
    app = RToolGUI(root)
    root.mainloop()