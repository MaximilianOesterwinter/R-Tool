"""
MIT License

Copyright (c) 2026 Maximilian Oesterwinter

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import webbrowser
from pathlib import Path

from version import APP_VERSION
from update_check import is_newer_version_available
from r_tool.commands import run_analysis, run_plot, run_preparation, get_variable_names
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
        "dataframe": {"label": "Overview over the dataframe", "code": "dataframe"},
        "describe": {"label": "Describe a variable", "code": "describe"},
        "anova": {"label": "ANOVA", "code": "anova"},
        "chi_square": {"label": "Chi Square", "code": "chi_square"},
        "correlation": {"label": "Correlation", "code": "correlation"},
        "logit": {"label": "Logit Model (WIP)", "code": "multiple"},
        "lin_reg": {"label": "Linear Regression (WIP)", "code": "multiple"},
        "paired_ttest": {"label": "Paired t-test (WIP)", "code": 2},
        "unpaired_ttest": {"label": "Unpaired t-test (WIP)", "code": "var_const"},
        "norm_test": {"label": "Normality Test (WIP)", "code": "dep_group"},
        "welch_test": {"label": "Welch Test (WIP)", "code": "dep_group"},
        "mann_whitney_test": {"label": "Mann-Whitney Test (WIP)", "code": "dep_group"},
    },
    "plot": {
        "scatterplot": {"label": "Scatterplot", "code": "scatterplot"},
        "barplot": {"label": "Barplot or Column chart", "code": "barplot"},
        "histogram": {"label": "Histogram", "code": "histogram"},
        "boxplot": {"label": "Boxplot", "code": "boxplot"},
    },
    "preparation": {
        "subframe": {"label": "Create a subframe", "code": "subframe"},
        "factorize": {"label": "Factorize variable", "code": "factorize"},
        "rename": {"label": "Rename variables", "code": "rename"},
        "mutate": {"label": "Mutate variables", "code": "mutate"},
        "summarise": {"label": "Create summary dataset", "code": "summary"}
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
        self.root.title("R-Tool version 2.0.0")
        self.root.minsize(300, 300)
        self.root.maxsize(1280, 1080)
        self.root.geometry("900x850+50+50")

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.method_combobox = ttk.Combobox(self.main_frame, state="readonly")
        self.method_combobox.pack(fill="x", padx=8, pady=8)
        self.method_combobox.bind("<<ComboboxSelected>>", self.update_input_fields)

        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill="x")

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill="x", pady=10)

        self.variable_entries = []
        self.group_var_widget = None
        self.facet_var_widget = None
        self.weight_var_widget = None
        self.variable_names = {}
        self.variable_display = []
        self.display_to_name = {}

        self.na_rm_var = tk.BooleanVar(value=False)

        self.available_datasets = get_available_datasets()

        self.beside_var = tk.BooleanVar(value=False)
        self.flip_var = tk.BooleanVar(value=False)
        self.barplot_stat_identity_var = tk.BooleanVar(value=False)
        self.jitter_var = tk.BooleanVar(value=False)
        
        self.main_label_var = tk.StringVar()
        self.x_label_var = tk.StringVar()
        self.y_label_var = tk.StringVar()

        self.selected_dataset = tk.StringVar()
        self.mode_var = tk.StringVar(value="analysis")
        self.pivot_longer_var = tk.BooleanVar(value=False)
        self.remove_na_var = tk.BooleanVar(value=False)
        self.subframe_name_var = tk.StringVar()
        self.factor_levels_var = tk.StringVar()
        self.factor_labels_var = tk.StringVar()
        self.rename_entries = []

        self.binwidth_var = tk.StringVar()
        self.relative_frequencies_var = tk.BooleanVar(value=False)
        self.normal_distribution_var = tk.BooleanVar(value=False)
        self.use_density_var = tk.BooleanVar(value=False)
        self.show_outliers_var = tk.BooleanVar(value=False)
        self.show_points_var = tk.BooleanVar(value=False)
        self.show_mean_var = tk.BooleanVar(value=False)
        self.show_notches_var = tk.BooleanVar(value=False)
        self.show_n_var = tk.BooleanVar(value=False)
        self.color_by_group_var = tk.BooleanVar(value=False)
        self.sort_groups_var = tk.BooleanVar(value=False)
        self.anova_post_hoc_var = tk.BooleanVar(value=False)
        self.anova_effect_size_var = tk.BooleanVar(value=False)
        self.anova_levene_test_var = tk.BooleanVar(value=False)

        self.mutate_new_var_name = tk.StringVar()
        self.mutate_operation_var = tk.StringVar()
        self.mutate_operator_var = tk.StringVar()
        self.mutate_na_rm_var = tk.BooleanVar(value=False)
        self.mutate_variable_entries = []
        self.recode_entries = []
        self.recode_else_var = tk.StringVar()
        self.reverse_min_var = tk.StringVar()
        self.reverse_max_var = tk.StringVar()
        self.pivot_names_to_var = tk.StringVar()
        self.pivot_values_to_var = tk.StringVar()
        self.mutate_operations = {
            "Arithmetic": "arithmetic",
            "Row mean": "row_mean",
            "Row sum": "row_sum",
            "Log": "log",
            "Z-standardize": "z_standardize",
            "Reverse scale": "reverse_scale",
            "Recode / case_when": "recode"
        }

        self.summary_name_var = tk.StringVar()
        self.summary_na_rm_var = tk.BooleanVar(value=False)
        self.summary_function_var = []
        self.summary_functions = {
            "Mean": "mean",
            "Median": "median",
            "Standard deviation": "sd",
            "Minimum": "min",
            "Maximum": "max",
            "Sum": "sum",
            "Observations": "n",
            "Distinct observations": "n_distinct"
        }
        self.correlation_methods = {
            "Person's r": "pearson",
            "Kendall's tau": "kendall",
            "Spearman's rho": "spearman"
        }
        self.correlation_method_var = []

        self.describe_summary_var = tk.BooleanVar(value=False)
        self.describe_sd_var = tk.BooleanVar(value=False)
        self.describe_variance_var = tk.BooleanVar(value=False)
        self.describe_skew_var = tk.BooleanVar(value=False)
        self.describe_kurtosis_var = tk.BooleanVar(value=False)
        self.describe_normality_var = tk.BooleanVar(value=False)

        if self.available_datasets:
            self.selected_dataset.set(self.available_datasets[0])
        else:
            self.selected_dataset.set("")

        self.build_ui()
        self.refresh_variable_mappings()
        self.refresh_method_dropdown()
        self.update_input_fields()

    def build_ui(self):

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.execute_button = tk.Button(
            self.bottom_frame,
            text="Execute",
            command=self.execute_selected_action
        )
        self.execute_button.pack(pady=10)

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
        self.dataset_label.pack(side="left", padx=(150, 0))

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

        self.variable_entries.clear()
        self.group_var_widget = None
        self.facet_var_widget = None
        self.weight_var_widget = None

        for widget in self.button_frame.winfo_children():
            widget.destroy()
    
    def input_field(
        self, 
        field_type, 
        frame=None, 
        label=None,
        storage=None, 
        tk_variable=None, 
        textvariable=None,
        values=None, 
        state=None,
        side=None,
        width=None,
        padx=None, 
        pady=None,
        fill="x"
        ):
        if frame is None:
            frame = self.input_frame
        if values is None:
            values = self.variable_display
        if state is None:
            state = "readonly"
        if padx is None:
            padx = 5
        if pady is None:
            pady = 5
        if side is None:
            side = "left"
        if label is None:
            label = "test"
        if tk_variable is None:
            tk_variable = self.na_rm_var
        if width is None:
            width = 35

        if field_type == "combobox":
            ttk.Label(
            frame,
            text=label
            ).pack(anchor="w")

            combo = ttk.Combobox(
                frame,
                values=values,
                state=state
            )
            combo.pack(fill=fill, padx=padx, pady=pady)

            if values:
                combo.set("Select variable")
            else:
                combo.set("No variables available")
            
            if storage is None:
                self.variable_entries.append(combo)
            elif storage == "group":
                self.group_var_widget = combo
            elif storage == "facet":
                self.facet_var_widget = combo
            elif storage == "weight":
                self.weight_var_widget = combo
            elif storage == "summary":
                self.summary_function_var.append(combo)
            elif storage == "correlation":
                self.correlation_method_var.append(combo)
        
        elif field_type == "checkbox":
            check = ttk.Checkbutton(
                frame,
                text=label,
                variable=tk_variable
            )
            check.pack(anchor="w", padx=padx, pady=pady)
        
        elif field_type == "entry":
            ttk.Label(
                frame,
                text=label
            ).pack(side=side)

            entry = ttk.Entry(
                frame,
                textvariable=textvariable,
                width=width
            )
            entry.pack(side=side, fill=fill, expand=True, padx=padx, pady=pady)
    
    def add_additional_variable_button(
        self, 
        field_type="combobox", 
        frame=None,
        frame_button=None,
        label=None,
        text=None,
        storage=None, 
        tk_variable=None, 
        textvariable=None,
        values=None, 
        state=None,
        side=None,
        width=None,
        padx=None, 
        pady=None,
        fill="x"
        ):
        if frame_button is None:
            frame_button = self.button_frame
        if frame is None:
            frame = self.input_frame
        if values is None:
            values = self.variable_display
        if state is None:
            state = "readonly"
        if padx is None:
            padx = 5
        if pady is None:
            pady = 5
        if side is None:
            side = "left"
        if label is None:
            label = "test"
        if tk_variable is None:
            tk_variable = self.na_rm_var
        if width is None:
            width = 35
        if text is None:
            text = "Additional variables"

        button = tk.Button(
            frame_button,
            text=text,
            command=lambda: self.input_field(
                field_type, 
                frame, 
                label,
                storage, 
                tk_variable, 
                textvariable,
                values, 
                state,
                side,
                width,
                padx, 
                pady,
                fill
            )
        )
        button.pack(pady=5)

    def add_variable_field(
        self, 
        parent=None, 
        label=None,
        variable=None
        ):
        if parent is None:
            parent = self.input_frame
        if variable is None:
            variable = self.variable_entries
        if label is None:
            label = f"Variable {len(variable)+1}"
        
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(
            frame, 
            text=label
        ).pack(anchor="w")

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

        variable.append(combo)
    
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
    
    def add_pivot_longer_checkbox(self):
        check = ttk.Checkbutton(
            self.input_frame,
            text="Use pivot_longer()",
            variable=self.pivot_longer_var,
            command=self.update_pivot_fields
        )
        check.pack(anchor="w", padx=5, pady=5)

        self.pivot_frame = ttk.Frame(self.input_frame)
        self.pivot_frame.pack(fill="x", padx=5, pady=5)

    def update_pivot_fields(self, event=None):
        for widget in self.pivot_frame.winfo_children():
            widget.destroy()

        if not self.pivot_longer_var.get():
            return

        ttk.Label(self.pivot_frame, text="Names to:").pack(side="left")

        ttk.Entry(
            self.pivot_frame,
            textvariable=self.pivot_names_to_var
        ).pack(side="left", fill="x", expand=True, padx=5)

        ttk.Label(self.pivot_frame, text="Values to:").pack(side="left")
        
        ttk.Entry(
            self.pivot_frame,
            textvariable=self.pivot_values_to_var
        ).pack(side="left", fill="x", expand=True, padx=5)
    
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
        self.input_field(
            field_type="combobox",
            label="Variable to factorize:"
        )

        self.input_field(
            field_type="entry",
            label="Levels, separated by comma, e.g. 1,2,3",
            textvariable=self.factor_levels_var,
            side="top"
        )

        self.input_field(
            field_type="entry",
            label="Labels, separated by comma, e.g. low,medium,high",
            textvariable=self.factor_labels_var,
            side="top"
        )
    
    def add_rename_pair_field(self):
        old_var = tk.StringVar()
        new_var = tk.StringVar()

        old_menu = ttk.Combobox(
            self.input_frame,
            textvariable=old_var,
            values=self.variable_display,
            state="readonly"
        )
        old_menu.pack(side="top", fill="x", expand=True, padx=2, pady=(10, 5))

        self.input_field(
            field_type="entry",
            textvariable=new_var,
            padx=2,
            pady=(10, 5),
            label="Choose variable and rename below",
            side="top"
        )

        self.rename_entries.append((old_var, new_var))
    
    def add_rename_fields(self):
        self.rename_entries = []

        self.add_rename_pair_field()

        add_button = ttk.Button(
            self.button_frame,
            text="Add variable to rename",
            command=self.add_rename_pair_field
        )
        add_button.pack(pady=5)

    def add_summary_fields(self):
        frame = ttk.Frame(self.input_frame)
        frame.pack(fill="x", padx=5, pady=5)

        self.input_field(
            field_type="entry",
            label="Name for the new dataframe:",
            textvariable=self.summary_name_var,
            side="top"
        )

        self.input_field(
            field_type="combobox",
            label="Summary function:",
            values=list(self.summary_functions.keys()),
            storage="summary"
        )

        self.input_field(
            field_type="checkbox",
            label="Remove NAs",
            tk_variable=self.na_rm_var
        )

        self.input_field(
            field_type="combobox",
            label="Variable to summarise:",
            storage=self.variable_entries
        )
        
        add_target_button = ttk.Button(
            self.input_frame,
            text="Add another variable to summarise",
            command=lambda: self.input_field(
                field_type="combobox",
                label="Variable to summarise:",
            )
        )
        add_target_button.pack(anchor="w", padx=5, pady=5)

        self.input_field(
            field_type="combobox",
            label="Grouping variable optional:",
            storage="group"
        )

    def add_mutation_fields(self):
        self.input_field(
            field_type="entry",
            label="Name for the new variable:",
            textvariable=self.mutate_new_var_name,
            side="top"
        )

        label = tk.Label(self.input_frame, text="Operation:")
        label.pack(anchor="w", padx=5, pady=(10, 0))

        combo = ttk.Combobox(
            self.input_frame,
            textvariable=self.mutate_operation_var,
            values=list(self.mutate_operations.keys()),
            state="readonly"
        )
        combo.pack(side="top", fill="x", padx=5, pady=2)

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
            self.input_field(
                field_type="combobox",
                frame=self.mutation_dynamic_frame,
                label="Variable 1:",
                side="top"
            )
            
            operator_label = ttk.Label(self.mutation_dynamic_frame, text="Operator:")
            operator_label.pack(anchor="w", padx=5)

            operator_combo = ttk.Combobox(
                self.mutation_dynamic_frame,
                textvariable=self.mutate_operator_var,
                values=["+", "-", "*", "/", "^"],
                state="readonly"
            )
            operator_combo.pack(fill="x")
            
            self.input_field(
                field_type="combobox",
                frame=self.mutation_dynamic_frame,
                label="Variable 2:",
                side="top"
            )

        elif operation in ["row_mean", "row_sum"]:
            self.input_field(
                field_type="combobox",
                frame=self.mutation_dynamic_frame,
                label="Variable for operation:",
                side="top"
            )
            
            self.input_field(
                field_type="combobox",
                frame=self.mutation_dynamic_frame,
                label="Variable for operation:",
                side="top"
            )

            self.add_additional_variable_button(
                parent=self.mutation_dynamic_frame,
                label="Variable for operation:",
                variable=None
            ) 

            self.input_field(
                field_type="checkbox",
                frame=self.mutation_dynamic_frame,
                label="Remove NAs",
                tk_variable=self.na_rm_var,
                side="top"
            )  
        
        elif operation in ["log", "z_standardize"]:
            self.input_field(
                field_type="combobox",
                frame=self.mutation_dynamic_frame,
                label="Variable for operation:",
                side="top"
            )
        
        elif operation == "reverse_scale":
            self.input_field(
                field_type="combobox",
                frame=self.mutation_dynamic_frame,
                label="Variable for operation:",
                side="top"
            )

            self.input_field(
                field_type="entry",
                frame=self.mutation_dynamic_frame,
                label="Minimum scale value:",
                textvariable=self.reverse_min_var,
                side="top",
                pady=2
            )

            self.input_field(
                field_type="entry",
                frame=self.mutation_dynamic_frame,
                label="Maximum scale value:",
                textvariable=self.reverse_max_var,
                side="top",
                pady=2
            )
        
        elif operation == "recode":

            self.input_field(
                field_type="combobox",
                frame=self.mutation_dynamic_frame,
                label="Variable to recode:",
                side="top"
            )
            self.add_variable_field(
                parent=self.mutation_dynamic_frame,
                label=None,
                variable=None
                )

            self.recode_entries = []

            self.recode_rules_frame = ttk.Frame(self.mutation_dynamic_frame)
            self.recode_rules_frame.pack(fill="x", padx=5, pady=5)

            self.add_recode_rule_field()

            add_rule_button = ttk.Button(
                self.mutation_dynamic_frame,
                text="Add recode rule",
                command=self.add_recode_rule_field
            )
            add_rule_button.pack(pady=5)

            else_frame = ttk.Frame(self.mutation_dynamic_frame)
            else_frame.pack(fill="x", padx=5, pady=5)

            else_label = ttk.Label(else_frame, text="Else value:")
            else_label.pack(side="left")

            else_entry = ttk.Entry(
                else_frame,
                textvariable=self.recode_else_var
            )
            else_entry.pack(side="left", fill="x", expand=True, padx=5)
    
    def add_recode_rule_field(self):
        frame = ttk.Frame(self.recode_rules_frame)
        frame.pack(fill="x", pady=2)

        operator_var = tk.StringVar()
        value_var = tk.StringVar()
        result_var = tk.StringVar()

        if_label = ttk.Label(frame, text="IF value")
        if_label.pack(side="left", padx=2)

        operator_combo = ttk.Combobox(
            frame,
            textvariable=operator_var,
            values=["==", "!=", ">", ">=", "<", "<="],
            state="readonly",
            width=5
        )
        operator_combo.pack(side="left", padx=2)

        value_entry = ttk.Entry(
            frame,
            textvariable=value_var,
            width=12
        )
        value_entry.pack(side="left", padx=2)

        then_label = ttk.Label(frame, text="THEN")
        then_label.pack(side="left", padx=2)

        result_entry = ttk.Entry(
            frame,
            textvariable=result_var,
            width=12
        )
        result_entry.pack(side="left", padx=2)

        self.recode_entries.append(
            (operator_var, value_var, result_var)
        )
    
    def add_plot_label_fields(self):
        self.input_field(
            field_type="entry",
            label="Main title:",
            textvariable=self.main_label_var,
            pady=2,
            side="top"
        )

        self.input_field(
            field_type="entry",
            label="X label:",
            textvariable=self.x_label_var,
            pady=2,
            side="top"
        )

        self.input_field(
            field_type="entry",
            label="Y label:",
            textvariable=self.y_label_var,
            pady=2,
            side="top"
        )
    
    def add_boxplot_options(self):
        self.input_field(
            field_type="combobox",
            label="Variable y-axis:",
            side="top"
        )
        
        self.input_field(
            field_type="combobox",
            label="Grouping variable optional:",
            storage="group",
            side="top"
        )

        self.input_field(
            field_type="combobox",
            label="Facet variable optional:",
            storage="facet",
            side="top"
        )
        
        self.input_field(
            field_type="combobox",
            label="Weight variable optional:",
            storage="weight",
            side="top"
        )

        self.add_plot_label_fields()

        self.input_field(
            field_type="checkbox",
            label="Flip coordinates",
            tk_variable=self.flip_var
        )
        
        self.input_field(
            field_type="checkbox",
            label="Show outliers",
            tk_variable=self.show_outliers_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show points",
            tk_variable=self.show_points_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show mean",
            tk_variable=self.show_mean_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show notches",
            tk_variable=self.show_notches_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show n",
            tk_variable=self.show_n_var
        )

        self.input_field(
            field_type="checkbox",
            label="Color by group (needs grouping variable)",
            tk_variable=self.color_by_group_var
        )

        self.input_field(
            field_type="checkbox",
            label="Sort groups (needs grouping variable)",
            tk_variable=self.sort_groups_var
        )
    
    def add_bar_column_options(self):
        self.input_field(
            field_type="combobox",
            label="Variable x-axis:"
        )
        
        self.input_field(
            field_type="combobox",
            label="Variable y-axis optional:"
        )

        self.input_field(
            field_type="combobox",
            label="Grouping variable optional:",
            storage=self.group_var_widget
        )

        self.add_plot_label_fields()

        self.input_field(
            field_type="checkbox",
            label="Flip coordinates",
            tk_variable=self.flip_var
        )

        self.input_field(
            field_type="checkbox",
            label="Bars beside each other (needs grouping variable)",
            tk_variable=self.beside_var
        )

        self.input_field(
            field_type="checkbox",
            label="Stat='identity' (Use, if you set a variable on the y-axis)",
            tk_variable=self.barplot_stat_identity_var
        )
    
    def add_scatterplot_options(self):
        self.input_field(
            field_type="combobox",
            label="Variable x-axis:"
        )

        self.input_field(
            field_type="combobox",
            label="Variable y-axis:"
        )

        self.input_field(
            field_type="combobox",
            label="Grouping variable optional:",
            storage="group"
        )

        self.add_plot_label_fields()

        self.input_field(
            field_type="checkbox",
            label="Use jitter-option",
            tk_variable=self.jitter_var
        )
    
    def add_histogram_options(self):
        self.input_field(
            field_type="combobox",
            label="Variable x-axis:"
        )

        self.add_plot_label_fields()

        self.input_field(
            field_type="entry",
            label="Binwidth (provide an integer or float)",
            textvariable=self.binwidth_var,
            width=10,
            padx=(2, 200),
            fill=None,
            side="left"
        )

        self.input_field(
            field_type="checkbox",
            label="Show normal distribution (Also use density)",
            tk_variable=self.normal_distribution_var
        )

        self.input_field(
            field_type="checkbox",
            label="Use density",
            tk_variable=self.use_density_var
        )

    def add_describe_options(self):
        self.input_field(
            field_type="combobox",
            label="Variable to describe:"
        )

        self.input_field(
            field_type="combobox",
            label="Grouping variable optional:",
            storage="group"
        )

        self.input_field(
            field_type="checkbox",
            label="Show summary",
            tk_variable=self.describe_summary_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show standard deviation",
            tk_variable=self.describe_sd_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show variance",
            tk_variable=self.describe_variance_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show skew",
            tk_variable=self.describe_skew_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show kurtosis",
            tk_variable=self.describe_kurtosis_var
        )

        self.input_field(
            field_type="checkbox",
            label="Show normality distribution (Shapiro-Wilk test)",
            tk_variable=self.describe_normality_var
        )

        self.input_field(
            field_type="checkbox",
            label="Remove NAs (recommended)",
            tk_variable=self.na_rm_var
        )
    
    def add_anova_options(self):
        self.input_field(
            field_type="combobox",
            label="Dependent variable:",
        )

        self.input_field(
            field_type="combobox",
            label="Independent variable:"
        )

        self.add_additional_variable_button(
            frame_button=self.button_frame,
            text="Add additional independent variable",
            label="Independent variable"
        )

        self.input_field(
            field_type="checkbox",
            label="Perform post-hoc test (only for one-way ANOVA)",
            tk_variable=self.anova_post_hoc_var
        )

        self.input_field(
            field_type="checkbox",
            label="Calculate effect size (Cohen's f)(only for one-way ANOVA)",
            tk_variable=self.anova_effect_size_var
        )

        self.input_field(
            field_type="checkbox",
            label="Perform levene test (only for two-way ANOVA)",
            tk_variable=self.anova_levene_test_var
        )
    
    def add_chi_square_options(self):
        self.input_field(
            field_type="combobox",
            label="Variable 1:"
        )

        self.input_field(
            field_type="combobox",
            label="Variable 2:"
        )

    def add_correlation_options(self):
        self.input_field(
            field_type="combobox",
            label="Variable 1:"
        )

        self.input_field(
            field_type="combobox",
            label="Variable 2:"
        )

        self.input_field(
            field_type="combobox",
            label="Correlation koefficient:",
            values=list(self.correlation_methods.keys()),
            storage="correlation"
        )

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

        code = config["code"]

        if code == "dataframe":
            return
        if code == "describe":
            self.variable_entries = []
            self.group_var_widget = None

            self.add_describe_options()
            return
        if code == "anova":
            self.variable_entries = []

            self.add_anova_options()
            return
        if code == "chi_square":
            self.variable_entries = []

            self.add_chi_square_options()
            return
        if code == "correlation":
            self.variable_entries = []
            self.correlation_method_var = []

            self.add_correlation_options()
            return
        if code == 1:
            self.add_variable_field()
            return
        if code == 2:
            self.add_variable_field()
            self.add_variable_field()
            return
        if code == "multiple":
            self.add_variable_field()
            self.add_variable_field()
            self.add_additional_variable_button()
        if code == "x":
            self.add_variable_field_x()
        if code == "y":
            self.add_variable_field_y()
        if code == "xy":
            self.add_variable_field_y()
            self.add_variable_field_x()
        if code == "grouped":
            self.add_variable_field()
            self.add_variable_field_grouping()
        if code == "dep_group":
            self.add_variable_field_dependent()
            self.add_variable_field_grouping()
        if code == "var_const":
            self.add_variable_field()
            self.add_variable_field_write()
        
        if code == "boxplot":
            self.variable_entries = []
            self.group_var_widget = None
            self.facet_var_widget = None
            self.weight_var_widget = None

            self.main_label_var.set("")
            self.x_label_var.set("")
            self.y_label_var.set("")

            self.add_boxplot_options()
            return

        if code == "scatterplot":
            self.variable_entries = []
            self.group_var_widget = None

            self.main_label_var.set("")
            self.x_label_var.set("")
            self.y_label_var.set("")

            self.add_scatterplot_options()
            return
        if code == "barplot":
            self.variable_entries = []
            self.group_var_widget = None

            self.flip_var.set(False)
            self.beside_var.set(False)
            self.barplot_stat_identity_var.set(False)
            self.main_label_var.set("")
            self.x_label_var.set("")
            self.y_label_var.set("")

            self.add_bar_column_options()
            return
        if code == "histogram":
            self.variable_entries = []

            self.binwidth_var.set("0.5")
            self.add_histogram_options()


        if code == "subframe":
            self.variable_entries = []

            self.pivot_longer_var.set(False)
            self.remove_na_var.set(False)
            self.subframe_name_var.set("")

            self.add_subframe_name_field()
            self.add_variable_field()
            self.add_additional_variable_button()
            self.add_pivot_longer_checkbox()
            self.add_remove_na_checkbox()
            return
        if code == "factorize":
            self.variable_entries = []

            self.factor_levels_var.set("")
            self.factor_labels_var.set("")

            self.add_factorize_fields()
            return
        if code == "rename":
            self.variable_entries = []

            self.add_rename_fields()
            return
        if code == "mutate":
            self.variable_entries = []

            self.mutate_new_var_name.set("")
            self.mutate_operation_var.set("")
            self.mutate_operator_var.set("")
            self.mutate_na_rm_var.set(False)
            self.reverse_min_var.set("")
            self.reverse_max_var.set("")

            self.add_mutation_fields()
            return
        if code == "summary":
            self.variable_entries = []

            self.add_summary_fields()
            return

    def collect_selected_variables(self):
        variables = []
        group_var = ""
        facet_var = ""
        weight_var = ""

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
        
        if (
            self.group_var_widget is not None 
            and self.group_var_widget.winfo_exists()
        ):
            value = self.group_var_widget.get().strip()

            if value in self.display_to_name:
                group_var = self.display_to_name[value]
            else:
                group_var = value

        if (
            self.facet_var_widget is not None
            and self.facet_var_widget.winfo_exists()
        ):
            value = self.facet_var_widget.get().strip()

            if value in self.display_to_name:
                facet_var = self.display_to_name[value]
            else:
                facet_var = value
        
        if (
            self.weight_var_widget is not None
            and self.weight_var_widget.winfo_exists()
        ):
            value = self.weight_var_widget.get().strip()

            if value in self.display_to_name:
                weight_var = self.display_to_name[value]
            else:
                weight_var = value

        return variables, group_var, facet_var, weight_var

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
        variables, group_var, facet_var, weight_var = self.collect_selected_variables()


        try:
            if not dataset_name:
                raise ValueError("Please select a prepared dataset.")

            if not method:
                raise ValueError("Please select a method.")

            if mode == "analysis":
                if method == "dataframe":
                    result = run_analysis(
                        method, 
                        variables, 
                        dataset_name
                    )
                
                if method == "describe":
                    if len(variables) < 1:
                        messagebox.showerror(
                            "Error",
                            "Please select a variable to describe."
                        )
                        return
                    result = run_analysis(
                        method,
                        variables,
                        dataset_name,
                        summary=self.describe_summary_var.get(),
                        sd=self.describe_sd_var.get(),
                        variance=self.describe_variance_var.get(),
                        skew=self.describe_skew_var.get(),
                        kurtosis=self.describe_kurtosis_var.get(),
                        normality=self.describe_normality_var.get(),
                        na_rm=self.na_rm_var.get(),
                        group_var=group_var
                    )
                
                if method == "anova":
                    result = run_analysis(
                        method,
                        variables,
                        dataset_name,
                        post_hoc=self.anova_post_hoc_var.get(),
                        effect_size=self.anova_effect_size_var.get(),
                        levene_test=self.anova_levene_test_var.get()
                    )
                
                if method == "chi_square":
                    result = run_analysis(
                        method,
                        variables,
                        dataset_name
                    )
                
                if method == "correlation":
                    if len(self.correlation_method_var) < 1:
                        messagebox.showerror(
                            "Error",
                            "Please select one correlation koefficient."
                        )
                    for entry in self.correlation_method_var:
                        selected_method = self.correlation_methods[entry.get().strip()]

                    result = run_analysis(
                        method,
                        variables,
                        dataset_name,
                        selected_method=selected_method
                    )

            elif mode == "plot":
                
                if method == "boxplot":
                    if self.color_by_group_var.get() or self.sort_groups_var.get():
                        if group_name == "":
                            messagebox.showerror(
                                "Error",
                                "Please select a grouping variable when 'Color by group` or 'Sort groups' is selected."
                            )
                            return

                    result = run_plot(
                        method,
                        variables,
                        dataset_name,
                        flip=self.flip_var.get(),
                        show_outliers=self.show_outliers_var.get(),
                        show_points=self.show_points_var.get(),
                        show_mean=self.show_mean_var.get(),
                        show_notches=self.show_notches_var.get(),
                        show_n=self.show_n_var.get(),
                        color_by_group=self.color_by_group_var.get(),
                        sort_groups=self.sort_groups_var.get(),
                        main_lab=self.main_label_var.get().strip(),
                        x_lab=self.x_label_var.get().strip(),
                        y_lab=self.y_label_var.get().strip(),
                        group_var=group_var,
                        facet_var=facet_var,
                        weight_var=weight_var
                    )

                if method == "histogram":
                    result = run_plot(
                        method,
                        variables,
                        dataset_name,
                        binwidth=self.binwidth_var.get().strip(),
                        norm=self.normal_distribution_var.get(),
                        show_density=self.use_density_var.get(),
                        main_lab=self.main_label_var.get().strip(),
                        x_lab=self.x_label_var.get().strip(),
                        y_lab=self.y_label_var.get().strip(),
                    )

                if method == "scatterplot":
                    if len(variables) < 2:
                        messagebox.showerror(
                            "Error",
                            "Please select x and y variables."
                        )
                        return

                    result = run_plot(
                        method,
                        variables,
                        dataset_name,
                        jitter=self.jitter_var.get(),
                        main_lab=self.main_label_var.get().strip(),
                        x_lab=self.x_label_var.get().strip(),
                        y_lab=self.y_label_var.get().strip(),
                        group_var=group_var
                    )

                if method == "barplot":
                    if len(variables) < 1:
                        messagebox.showerror(
                            "Error",
                            "Please select an x variable."
                        )
                        return
                    
                    var_x = variables[0]

                    if self.barplot_stat_identity_var.get():
                        if len(variables) < 2:
                            messagebox.showerror(
                                "Error",
                                "Please select a y variable when stat='identity' is enabled."
                            )
                            return

                        var_y = variables[1]
                    
                    else:
                        var_y = ""

                    result = run_plot(
                        method,
                        [var_x, var_y],
                        dataset_name,
                        flip=self.flip_var.get(),
                        beside=self.beside_var.get(),
                        stat_identity=self.barplot_stat_identity_var.get(),
                        main_lab=self.main_label_var.get().strip(),
                        x_lab=self.x_label_var.get().strip(),
                        y_lab=self.y_label_var.get().strip(),
                        group_var=group_var
                    )

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
                        remove_na=self.remove_na_var.get(),
                        names_to=self.pivot_names_to_var.get().strip(),
                        values_to=self.pivot_values_to_var.get().strip()
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
                        labels=self.factor_labels_var.get().strip()
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
                        
                    recode_rules = []
                    if operation == "recode":
                        for operator_var, value_var, result_var in self.recode_entries:
                            operator = operator_var.get().strip()
                            value = value_var.get().strip()
                            result_value = result_var.get().strip()

                            if operator and value and result_value:
                                recode_rules.append(
                                    f"{operator}|{value}|{result_value}"
                                )
                        
                        if not recode_rules:
                            messagebox.showerror(
                                "Error",
                                "Please enter at least one recode rule"
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
                        reverse_max=self.reverse_max_var.get().strip(),
                        recode_else=self.recode_else_var.get().strip(),
                        recode_rules=recode_rules
                    )

                elif method == "summarise":
                    output_name = self.summary_name_var.get().strip()

                    if not output_name:
                        raise ValueError(
                            "Error"
                            "Please enter a name for the new dataframe."
                        )
                    for entry in self.summary_function_var:
                        selected_function = self.summary_functions[entry.get().strip()]
                    
                    na_rm = str(self.na_rm_var.get()).lower()

                    if selected_function != "n" and len(variables) < 1:
                        raise ValueError(
                            "Error"
                            "Please select at least one variable to summarise."
                        )

                    result = run_preparation(
                        method,
                        variables,
                        dataset_name,
                        output_name=output_name,
                        selected_function=selected_function,
                        na_rm=na_rm,
                        group_var=group_var
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
                error_message = result.stderr.strip()

                if not error_message:
                    error_message = result.stdout.strip()

                if not error_message:
                    error_message = "Unknown backend error."

                messagebox.showerror("Backend error", error_message)
                return

            messagebox.showinfo("Success", result.stdout or "Action executed successfully.")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    root.after(500, check_for_updates)
    app = RToolGUI(root)
    root.mainloop()