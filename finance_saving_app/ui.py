import os
import sqlite3
import sys

from functools import partial
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from finance_saving_app.custom_widgets import CollapsibleWidget
from finance_saving_app.general import (
    CURRENT_DIR,
    calculate_after_tax,
    project_sp500_savings,
    shift_color,
)
from finance_saving_app.style_sheet import dark_style, light_style, pink_style

OBJECT_NAME = "budget_tool"


def get_app():
    app = QtWidgets.QApplication.instance()

    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    return app

class BudgetingTool(QtWidgets.QDialog):
    """Main dialog for the Couples Budgeting Tool."""

    def __init__(self, parent=None, open_on_details=False):
        super().__init__(parent)
        self.setWindowTitle("Couples Budgeting Tool")

        self.collapsible_widget_list = []
        self.default_color_theme = "dark"
        self.color_options = {
            "light": {"button": None,
                      "state": False,
                      "style_sheet": light_style,
                      "base_color": (205, 205, 205)
                      },
            "pink": {"button": None,
                     "state": False,
                     "style_sheet": pink_style,
                     "base_color": (245, 220, 225)
                     },
            "dark": {"button": None,
                     "state": False,
                     "style_sheet": dark_style,
                     "base_color": (42, 42, 42)
                     }
                            }
        self.split_type = "proportional"
        self.expense_split_types = {"proportional":{}, "even":{}}
        self.open_on_details = open_on_details
        self.user_details = None
        self.ui_refs = {}
        self.shared_expenses = None
        self.load_defaults()

        self.partner_groupboxes = []

        self.init_ui()
        self.update_percentages()

    def init_ui(self):
        """Initialize the main UI layout."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setObjectName("main_target")
        self.tab_layout = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tab_layout)

        start_tab = QtWidgets.QWidget()
        self.start_layout = QtWidgets.QVBoxLayout()
        start_tab.setLayout(self.start_layout)

        details_tab = QtWidgets.QWidget()
        self.details_layout = QtWidgets.QVBoxLayout()
        details_tab.setLayout(self.details_layout)

        options_tab = QtWidgets.QWidget()
        self.options_layout = QtWidgets.QVBoxLayout()
        options_tab.setLayout(self.options_layout)

        self.tab_layout.addTab(start_tab, "Start")
        self.tab_layout.addTab(details_tab, "Details")
        self.tab_layout.addTab(options_tab, "Options")

        if self.open_on_details:
            self.tab_layout.setCurrentIndex(1)

        self.user_start_layout = QtWidgets.QVBoxLayout()
        self.start_layout.addLayout(self.user_start_layout)
        self.user_start_layout.setAlignment(QtCore.Qt.AlignTop)

        # Partner income layout
        self.user_details_layout = QtWidgets.QHBoxLayout()
        self.details_layout.addLayout(self.user_details_layout)

        # Shared expenses section
        self.fixed_expenses_section = self.create_shared_expenses_section()
        self.details_layout.addWidget(self.fixed_expenses_section)

        # Partner-specific expenses section
        self.partner_expenses_section = self.create_individual_expenses_section()
        self.details_layout.addWidget(self.partner_expenses_section)

        self.populate_user_layouts()

        # Add save and load buttons
        button_layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("Save Defaults")
        save_button.clicked.connect(self.save_defaults)
        button_layout.addWidget(save_button)

        load_button = QtWidgets.QPushButton("Load Defaults")
        load_button.clicked.connect(self._on_load_default_pressed)
        button_layout.addWidget(load_button)

        self.details_layout.addLayout(button_layout)
        self.details_layout.addStretch()

        self.options_section = self.create_options_sections()
        self.options_layout.addWidget(self.options_section)
        self.options_layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        self.set_color_type_button_states()

    def set_color_type_button_states(self) -> None:
        """Update all color-type buttons and apply the active theme stylesheet."""
        for key, option in self.color_options.items():
            base_rgb = option["base_color"]
            text_color = "white" if key == "dark" else "black"

            if option["state"]:
                # Active button
                bright_rgb = shift_color(base_rgb, 1.15)
                option["button"].setStyleSheet(
                    f"background-color: rgb{bright_rgb}; color: {text_color};"
                )

                # Apply the main stylesheet
                self.setStyleSheet(option["style_sheet"](self))

                # Apply background to collapsible widgets
                self._apply_collapsible_widget_style(base_rgb)

            else:
                # Inactive button
                dim_rgb = shift_color(base_rgb, 0.85)
                option["button"].setStyleSheet(
                    f"background-color: rgb{dim_rgb}; color: {text_color};"
                )


    def _apply_collapsible_widget_style(self, color):
        """
        Helper: update all collapsible widgets with theme base color,
        text color, and border color.
        """
        for widget in self.collapsible_widget_list:
            widget.set_header_background_color(color)

    def populate_user_layouts(self):

        for i, (user_id, user_details_value) in enumerate(self.user_details.items()):
            # Determine if this is the last user group
            is_last = (i == len(self.user_details) - 1)
            # Access name and wage from user_details_value
            wage = user_details_value["wage"]
            wage_type = user_details_value["wage_type"]

            partner_gb, details_gb, summary_gb, add_remove_layout = self.create_user_group(
                user_id, wage, wage_type, last_one=is_last)

            if len(self.ui_refs.keys()) == 1:
                self.lock_remove_button_in_layout(add_remove_layout)

                self.user_start_layout.addLayout(add_remove_layout)

    def lock_remove_button_in_layout(self, layout):
        for i in range(layout.count()):  # Iterate through layout items
            item = layout.itemAt(i)      # Get the layout item
            widget = item.widget()       # Get the widget
            if widget:  # Check if it's a widget

                # Identify the second button and disable it (remove button)
                if i == 1 and isinstance(widget, QtWidgets.QPushButton):
                    widget.hide()


    def create_user_group(self, user_id, wage_value, wage_type, last_one=False):
        """Main method responsible for creating the modular ui setups and data setups for a user
        Usually wrapped by another method that handles errors,
        and also sets the widget names to the correct data sets.
        """

        partner_groupbox = QtWidgets.QGroupBox()
        core_layout = QtWidgets.QVBoxLayout()
        partner_groupbox.setLayout(core_layout)

        base_layout = QtWidgets.QHBoxLayout()
        partner_groupbox.setLayout(base_layout)
        core_layout.addLayout(base_layout)
        add_remove_partner_layout = QtWidgets.QVBoxLayout()
        partner_layout = QtWidgets.QVBoxLayout()
        base_layout.addLayout(partner_layout)
        # Add Partner Button
        add_partner_button = QtWidgets.QPushButton()

        add_partner_button.clicked.connect(
            partial(self._on_partner_count_changed_clicked,
                    add=add_remove_partner_layout, user_id = user_id
                    )
                                            )

        icon_add = os.path.normpath(
            os.path.join(CURRENT_DIR, "icons", "plus.png")
                                    ).replace("\\", "/")
        add_partner_button.setIcon(QtGui.QIcon(icon_add))
        add_remove_partner_layout.addWidget(add_partner_button)

        # Remove Partner Button
        remove_partner_button = QtWidgets.QPushButton()

        remove_partner_button.clicked.connect(
            partial(self._on_partner_count_changed_clicked, add=False, user_id=user_id)
        )

        icon_remove = os.path.normpath(
            os.path.join(CURRENT_DIR, "icons", "minus.png")
                                        ).replace("\\", "/")
        remove_partner_button.setIcon(QtGui.QIcon(icon_remove))
        add_remove_partner_layout.addWidget(remove_partner_button)

        base_layout.addLayout(add_remove_partner_layout)
        if not last_one:
            hide_layout(add_remove_partner_layout)

        # User Input Layouts
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Name: ")
        name_line_edit = QtWidgets.QLineEdit()
        name_line_edit.setPlaceholderText("Enter Name: eg. Joesph")
        name_line_edit.setText(self.user_details[user_id]["name"])
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_line_edit)

        wage_layout = QtWidgets.QHBoxLayout()
        is_monthly = self.user_details[user_id]["wage_type"]
        wage_toggle_monthly = QtWidgets.QRadioButton("Monthly Wage: ")
        wage_toggle_yearly = QtWidgets.QRadioButton("Yearly Wage: ")
        if is_monthly:
            wage_toggle_monthly.setChecked(True)
        else:
            wage_toggle_yearly.setChecked(True)

        wage_line_edit = QtWidgets.QLineEdit()
        if not wage_type:
            monthly_wage_value = wage_value
            wage_value = wage_value * 12

        else:
            monthly_wage_value = wage_value

        wage_line_edit.setText(str(wage_value))
        wage_layout.addWidget(wage_toggle_monthly)
        wage_layout.addWidget(wage_toggle_yearly)
        wage_layout.addWidget(wage_line_edit)
        wage_line_edit.setPlaceholderText("Enter income: eg. 2000 if Monthly, 24000 if Yearly")
        self.ui_refs.update({user_id:{"income_widget":wage_line_edit}})

        partner_layout.addLayout(name_layout)
        partner_layout.addLayout(wage_layout)
        partner_layout.addStretch()
        add_remove_partner_layout.addStretch()

        # Creating the details version of the user label
        user_name = self.user_details[user_id]['name']
        details_partner_groupbox = QtWidgets.QGroupBox(f"{user_name}s' Monthly Income")
        details_base_layout = QtWidgets.QHBoxLayout()
        details_partner_groupbox.setLayout(details_base_layout)


        if monthly_wage_value != 0:
            after_tax_value = calculate_after_tax(monthly_wage_value)
        else:
            after_tax_value = 0
        after_tax_value_label = QtWidgets.QLabel(f"After Tax Monthly Income: £{after_tax_value}")

        details_base_layout.addWidget(after_tax_value_label)

        user_number = user_id

        # Connect signals to update the details dynamically
        def update_details():
            # Update the group box title and label dynamically
            name = name_line_edit.text()
            try:
                wage = float(wage_line_edit.text())
            except ValueError:
                wage = 0

            if wage_toggle_yearly.isChecked():
                wage = wage / 12

            after_tax_wage = calculate_after_tax(wage)

            details_partner_groupbox.setTitle(f"{name}s' Monthly Income")
            after_tax_value_label.setText(f"After Tax Monthly Income: £{after_tax_wage:.2f}")
            self.update_details_sheet(set_name=[user_number,name])
            self.update_details_sheet(set_wage=[user_number,wage])
            self.update_percentages()

        name_line_edit.textChanged.connect(update_details)
        wage_line_edit.textChanged.connect(update_details)
        wage_toggle_monthly.toggled.connect(
            lambda checked,
                   uid=user_id: self._on_wage_type_changed(
                uid, True, checked, update_details)
                                            )
        wage_toggle_yearly.toggled.connect(
            lambda checked,
                   uid=user_id: self._on_wage_type_changed(
                uid, False, checked, update_details)
                                             )

        partner_groupbox.setMaximumHeight(100)
        summary_widget = QtWidgets.QWidget()
        summary_layout = QtWidgets.QVBoxLayout()
        summary_widget.setLayout(summary_layout)
        user_count = len(self.user_details)
        individual_expenses_groupbox = self.create_individual_expenses_groupbox(user_count, user_id)

        financial_summary_groupbox = self.create_budget_share_layout(user_id)
        summary_layout.addWidget(individual_expenses_groupbox)
        summary_layout.addLayout(financial_summary_groupbox)

        self.ui_refs[user_id]["group_widgets"] = (
                                                partner_groupbox,
                                                details_partner_groupbox,
                                                summary_widget,
                                                add_remove_partner_layout
                                                )
        self.user_start_layout.addWidget(partner_groupbox)
        self.user_details_layout.addWidget(details_partner_groupbox)
        self.user_summary_layout.addWidget(summary_widget)


        return partner_groupbox, details_partner_groupbox, summary_widget, add_remove_partner_layout

    def _on_partner_count_changed_clicked(self, add=None, user_id=None):
        """ Main method used for increasing user count,
        setting up the new user with default modular ui setup, data.
        """
        if add:
            hide_layout(add)
            # Add a new user group
            user_id = int(user_id) + 1
            user_id = str(f"{user_id:02}")
            self.user_details.update(
                {user_id: {
                    "name": f"User {user_id}", "wage": 50, "wage_type": True, "expenses": {}}
                }
                                    )
            wage = self.user_details[user_id]["wage"]
            wage_type = self.user_details[user_id]["wage_type"]
            self.create_user_group(user_id, wage, wage_type, last_one=True)

            return

        elif user_id in self.ui_refs:

            partner_groupbox, details_groupbox, summary_groupbox, add_remove_layout = \
            self.ui_refs[user_id]["group_widgets"]
            self.user_start_layout.removeWidget(partner_groupbox)
            self.user_details_layout.removeWidget(details_groupbox)
            self.user_summary_layout.removeWidget(summary_groupbox)

            partner_groupbox.deleteLater()
            details_groupbox.deleteLater()
            summary_groupbox.deleteLater()

            next_partner_groupbox, next_details_groupbox, summary_groupbox, next_button_layout = \
            self.ui_refs[
                decrement_key(user_id)]["group_widgets"]
            # Do something with the next set
            show_layout(next_button_layout)

            del self.ui_refs[user_id]
            del self.user_details[user_id]
            if len(self.ui_refs.keys()) == 1:
                self.lock_remove_button_in_layout(next_button_layout)

                self.user_start_layout.addLayout(next_button_layout)
        self.update_percentages(user_id)

    def _on_wage_type_changed(self, user_id, is_monthly, checked, update_details):
        if checked:
            self._set_wage_type(user_id, is_monthly)
            update_details()

    def _set_wage_type(self, user_id, checked):
        self.user_details[user_id]["wage_type"] = checked

        self.update_percentages()

    def _on_load_default_pressed(self):
        self.close()
        launch(open_on_details=True)

    def _on_color_button_clicked(self, color_type: str) -> None:
        """Handle color theme button click and update button states."""
        for key in self.color_options:
            self.color_options[key]["state"] = (key == color_type)

        self.set_color_type_button_states()

    def create_individual_income_layout(self):
        """Create the layout for partner income inputs with default values."""
        layout = QtWidgets.QHBoxLayout()

        for user_id, user_details_value in self.user_details.items():
            groupbox = QtWidgets.QGroupBox(f"{user_details_value['name']} Monthly Income")
            group_layout = QtWidgets.QVBoxLayout()
            groupbox.setLayout(group_layout)
            layout.addWidget(groupbox)
            wage = self.user_details[user_id]["wage"]
            wage_type = self.user_details[user_id]["wage_type"]
            if not wage_type:
                wage = wage /12

            if wage != 0:
                post_tax_value = calculate_after_tax(wage)
            else:
                post_tax_value = 0
            post_tax_value_label = QtWidgets.QLabel(f"After Tax Monthly Income: £{post_tax_value}")

            group_layout.addWidget(post_tax_value_label)

        return layout

    def create_shared_expenses_section(self):
        """Create a collapsible widget for fixed expenses with default values."""
        section = CollapsibleWidget("Shared Expenses")
        self.collapsible_widget_list.append(section)

        form_layout = QtWidgets.QFormLayout()

        # Load default values
        default_expenses = self.shared_expenses
        keys_to_pop = []
        for key in default_expenses.keys():
            if 'expenses' in key:
                keys_to_pop.append(key)
        for key in keys_to_pop:
            default_expenses.pop(key)

        for expense, default_value in default_expenses.items():
            line_label = QtWidgets.QLabel(expense)
            line_edit = QtWidgets.QLineEdit()
            line_edit.setPlaceholderText(f"Enter {expense.lower()}")
            line_edit.setText(str(default_value))  # Set default value
            line_edit.textChanged.connect(self.update_percentages)

            remove_button = QtWidgets.QPushButton()
            icon_remove = os.path.normpath(
                os.path.join(CURRENT_DIR, "icons", "minus.png")
                                            ).replace("\\", "/")
            remove_button.setIcon(QtGui.QIcon(icon_remove))
            remove_button.clicked.connect(
                partial(self._remove_expense, self.shared_expenses, expense)
                                            )
            # Put the line_edit and remove_button side-by-side
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.addWidget(line_label)
            h_layout.addWidget(line_edit)
            h_layout.addWidget(remove_button)

            form_layout.addRow(h_layout)

            self.shared_expenses[expense] = [line_edit, remove_button, h_layout]

        # Add "Add New Expense" button
        add_button = QtWidgets.QPushButton("Add New Expense")
        add_button.clicked.connect(lambda: self.create_new_expense(form_layout, None))
        form_layout.addRow(add_button)

        # Wrap the layout in a widget
        form_widget = QtWidgets.QWidget()
        form_widget.setLayout(form_layout)
        section.add_widget(form_widget)

        return section

    def create_individual_expenses_section(self):
        """Create a collapsible widget for user-specific expenses."""
        section = CollapsibleWidget("Partner-Specific Expenses")
        self.collapsible_widget_list.append(section)

        # Create a horizontal layout for all partners
        self.user_summary_layout = QtWidgets.QHBoxLayout()

        # Wrap the layout in a widget
        wrapper_widget = QtWidgets.QWidget()
        wrapper_widget.setLayout(self.user_summary_layout)
        section.add_widget(wrapper_widget)

        return section


    def create_individual_expenses_groupbox(self, user_count, user):
        """Create the modular groupbox and widgets for individual expenses per user display."""

        # Parent vertical layout for each partner
        partner_vertical_layout = QtWidgets.QVBoxLayout()
        user_name = self.user_details[user]["name"]
        # Create groupbox for partner expenses
        expense_groupbox = QtWidgets.QGroupBox(f"{user_name}'s Expenses")
        expense_layout = QtWidgets.QFormLayout()
        expense_groupbox.setLayout(expense_layout)

        # Get default expenses for the partner
        base_expenses = self.get_default_individual_expenses(user)
        default_expenses = {**base_expenses}
        # Add default expenses to the form layout

        for expense, default_value in default_expenses.items():
            new_edit, remove_button, row_layout = self._add_expense_row(
                                                            self.user_details[user]["expenses"],
                                                            expense,
                                                            default_value
                                                                        )

            self.user_details[user]["expenses"].update(
                {expense:[new_edit, remove_button, row_layout]}
                                                        )
            expense_layout.addRow(row_layout)
        # Add "Add New Expense" button

        add_button = QtWidgets.QPushButton("Add New Expense")
        add_button.clicked.connect(
            lambda i=user_count: self.create_new_expense(expense_layout, user=user)
                                    )
        expense_layout.addRow(add_button)

        # Add the expense groupbox to the vertical layout
        partner_vertical_layout.addWidget(expense_groupbox)

        # Add the vertical layout to the main horizontal layout
        partner_widget = QtWidgets.QWidget()
        partner_widget.setLayout(partner_vertical_layout)


        return partner_widget


    def create_budget_share_layout(self, user_id):
        """Create the layout for percentage share, contribution, and savings display."""

        sub_layout = QtWidgets.QVBoxLayout()

        groupbox = QtWidgets.QGroupBox(f"User {1} Financial Summary")
        group_layout = QtWidgets.QVBoxLayout()
        groupbox.setLayout(group_layout)

        sub_layout.addWidget(groupbox)

        # Percentage label
        percentage_label = QtWidgets.QLabel("0%")
        percentage_label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        percentage_label.setFont(font)
        group_layout.addWidget(percentage_label)

        # Contribution label
        contribution_label = QtWidgets.QLabel("£0.00")
        contribution_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(contribution_label)

        # Individual Expenses
        individual_expenses_label = QtWidgets.QLabel("£0.00")
        individual_expenses_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(individual_expenses_label)

        # Spacer
        spacer_label = QtWidgets.QLabel("----------")
        spacer_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(spacer_label)


        # Monthly savings label
        monthly_savings_label = QtWidgets.QLabel("Monthly Savings: £0.00")
        monthly_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(monthly_savings_label)

        # Yearly savings label
        yearly_savings_label = QtWidgets.QLabel("Yearly Savings: £0.00")
        yearly_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(yearly_savings_label)

        # Decade savings label
        decade_savings_label = QtWidgets.QLabel("Decade Savings: £0.00")
        decade_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(decade_savings_label)

        # Spacer
        spacer_label = QtWidgets.QLabel("----------")
        spacer_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(spacer_label)

        # Decade savings label
        sp500_20_savings_label = QtWidgets.QLabel("S&P 20% Savings: £0.00")
        sp500_20_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(sp500_20_savings_label)

        # Decade savings label
        sp500_50_savings_label = QtWidgets.QLabel("S&P 50% Savings: £0.00")
        sp500_50_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(sp500_50_savings_label)

        # Decade savings label
        sp500_70_savings_label = QtWidgets.QLabel("S&P 70% Savings: £0.00")
        sp500_70_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(sp500_70_savings_label)

        self.ui_refs.update({user_id:{}})

        self.ui_refs[user_id].update({"percentage_labels":percentage_label})
        self.ui_refs[user_id].update({"shared_expense_labels":contribution_label})
        self.ui_refs[user_id].update({"individual_expenses":individual_expenses_label})
        self.ui_refs[user_id].update({"monthly_savings_labels":monthly_savings_label})
        self.ui_refs[user_id].update({"yearly_savings_labels":yearly_savings_label})
        self.ui_refs[user_id].update({"decade_savings_labels":decade_savings_label})
        self.ui_refs[user_id].update({"sp500_savings_20_labels":sp500_20_savings_label})
        self.ui_refs[user_id].update({"sp500_savings_50_labels":sp500_50_savings_label})
        self.ui_refs[user_id].update({"sp500_savings_70_labels":sp500_70_savings_label})

        return sub_layout

    def create_options_sections(self):
        section = CollapsibleWidget("Main Settings")
        self.collapsible_widget_list.append(section)

        theme_menu_layout = QtWidgets.QVBoxLayout()
        section.add_layout(theme_menu_layout)

        theme_menu_button_layout = QtWidgets.QHBoxLayout()
        spacer_01 = QtWidgets.QWidget()
        spacer_01.setFixedHeight(10)
        section.add_widget(spacer_01)
        section.add_layout(theme_menu_button_layout)

        for color_type in self.color_options.keys():
            if color_type == self.default_color_theme:
                self.color_options[color_type]["state"] = True
            color_button = QtWidgets.QPushButton(color_type.capitalize())
            theme_menu_button_layout.addWidget(color_button)
            self.color_options[color_type]["button"] = color_button
            color_button.clicked.connect(partial(self._on_color_button_clicked,color_type))

        split_type_button_layout = QtWidgets.QHBoxLayout()
        spacer_02 = QtWidgets.QWidget()
        spacer_02.setFixedHeight(10)
        section.add_widget(spacer_02)
        section.add_layout(split_type_button_layout)

        split_type_label = QtWidgets.QLabel("Expense Split Type: ")
        split_type_button_layout.addWidget(split_type_label)
        for split_type in self.expense_split_types.keys():
            split_button = QtWidgets.QRadioButton(split_type.capitalize())
            split_button.clicked.connect(self.update_percentages)
            split_type_button_layout.addWidget(split_button)
            self.expense_split_types[split_type].update({"button":split_button})
            if split_type == self.split_type:
                split_button.setChecked(True)
        split_type_button_layout.addStretch()
        return section


    def create_new_expense(self, layout, user=None):
        """Add a new expense field to the fixed expenses section with a custom label.
        Wraps the _add_expense_row method with better error handling and updates data dictionaries
        with the created widgets and layouts.
        """

        if user:
            line_edit = self.user_details[user]["expenses"].keys()
            expense_dict = self.user_details[user]["expenses"]
        else:
            line_edit = self.shared_expenses.keys()
            expense_dict = self.shared_expenses

        # Prompt the user for a label name
        label_name, ok = QtWidgets.QInputDialog.getText(
            self, "New Expense", "Enter the name for the new expense:"
        )

        if not ok or not label_name.strip():  # Cancel or empty input
            QtWidgets.QMessageBox.warning(self,
                                          "Invalid Input",
                                          "Expense name cannot be empty."
                                          )
            return

        label_name = label_name.strip()

        if label_name in line_edit:
            QtWidgets.QMessageBox.warning(self,
                                          "Duplicate Label",
                                          f"An expense named '{label_name}' already exists."
                                          )
            return

        new_edit, remove_button, row_layout = self._add_expense_row(expense_dict, label_name)

        # Insert the new row before the "Add New Expense" button
        row_count = layout.rowCount()  # Total rows in the layout
        layout.insertRow(row_count - 1, row_layout)

        if user:
            self.user_details[user]["expenses"][label_name] = new_edit, remove_button, row_layout
        else:
            self.shared_expenses[label_name] = new_edit, remove_button, row_layout

    def _add_expense_row(self, expense_data, label_name, default_value = None):
        """Creates a new expense layout with widgets, connected the minus button to remove_expense.
        Can be passed both the Shared and Individual Expense data and works with either layout.
        """

        # Create new label and input field
        label = QtWidgets.QLabel(label_name)
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText(f"Enter {label_name.lower()} value")

        if default_value:
            default_value = str(default_value)
            line_edit.setText(default_value)

        line_edit.textChanged.connect(self.update_percentages)
        remove_button = QtWidgets.QPushButton()
        icon_remove = os.path.normpath(
            os.path.join(CURRENT_DIR, "icons", "minus.png")).replace("\\", "/")
        remove_button.setIcon(QtGui.QIcon(icon_remove))
        remove_button.clicked.connect(partial(self._remove_expense, expense_data, label_name))
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.addWidget(label)
        row_layout.addWidget(line_edit)
        row_layout.addWidget(remove_button)

        return line_edit, remove_button, row_layout

    def _remove_expense(self,expense_data, expense):
        """Helper to remove expense from instance dictionary and remove its widgets/layouts"""
        expense_layout = expense_data[expense][-1]
        self._clear_layout(expense_layout)
        expense_data.pop(expense)

        self.update_percentages()

    def _clear_layout(self, layout):
        """Helper to clear nested layouts."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            sub_layout = item.layout()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            elif sub_layout is not None:
                self._clear_layout(sub_layout)
        layout.deleteLater()

    def update_details_sheet(self, set_name=None, set_wage=None):

        if set_name:
            self.user_details[set_name[0]].update({"name": set_name[1]})
            self.user_details[set_name[0]].update({"wage": 0})

        if set_wage:
            self.user_details[set_wage[0]].update({"wage": set_wage[1]})

    def update_percentages(self, user_id=None):
        """Update the percentage share, contribution, and savings displays."""

        wages = [v["wage"] for v in self.user_details.values()]
        post_tax_wages = [calculate_after_tax(w) for w in wages]
        total_wages = sum(post_tax_wages)

        try:
            edit_widgets = [v[0] for v in self.shared_expenses.values()]
            total_shared_expenses = sum(float(e.text()) if e.text() else 0 for e in edit_widgets)

            for user_id, value in self.user_details.items():
                pre_tax_income = value["wage"]
                income = calculate_after_tax(pre_tax_income)
                individual_edits = [v[0] for v in value["expenses"].values()]

                individual_expenses = sum(
                    float(e.text()) if e.text() else 0 for e in individual_edits)

                if total_wages > 0:
                    current_split_type = next(
                        (k for k, v in self.expense_split_types.items() if v["button"].isChecked()),
                        None
                    )

                    if current_split_type == "proportional":
                        percentage = (income / total_wages) * 100
                    else:
                        percentage = 100 / len(self.user_details)

                    self.ui_refs[user_id]["percentage_labels"].setText(f"{percentage:.0f}%")

                    contribution = percentage / 100 * total_shared_expenses
                    self.ui_refs[user_id]["shared_expense_labels"].setText(
                        f"Shared Contribution: £{contribution:.2f}"
                    )
                    self.ui_refs[user_id]["individual_expenses"].setText(
                        f"Individual Expenses: £{individual_expenses:.2f}"
                    )

                    monthly_savings = income - contribution - individual_expenses
                    yearly_savings = monthly_savings * 12
                    decade_savings = monthly_savings * 120

                    self.ui_refs[user_id]["monthly_savings_labels"].setText(
                        f"Monthly Savings: £{monthly_savings:.2f}"
                    )
                    self.ui_refs[user_id]["yearly_savings_labels"].setText(
                        f"Yearly Savings: £{yearly_savings:.2f}"
                    )
                    self.ui_refs[user_id]["decade_savings_labels"].setText(
                        f"Decade Savings: £{decade_savings:.2f}"
                    )

                    if yearly_savings > 0:
                        sp500_20 = project_sp500_savings(yearly_savings, yearly_savings, 10, 20)
                        sp500_50 = project_sp500_savings(yearly_savings, yearly_savings, 10, 50)
                        sp500_70 = project_sp500_savings(yearly_savings, yearly_savings, 10, 70)

                        self.ui_refs[user_id]["sp500_savings_20_labels"].setText(
                            f"S&P500 20% Savings: £{sp500_20:.2f}"
                        )
                        self.ui_refs[user_id]["sp500_savings_50_labels"].setText(
                            f"S&P500 50% Savings: £{sp500_50:.2f}"
                        )
                        self.ui_refs[user_id]["sp500_savings_70_labels"].setText(
                            f"S&P500 70% Savings: £{sp500_70:.2f}"
                        )
                    else:
                        self._reset_sp500_labels(user_id)
                else:
                    self.reset_labels(user_id)

        except ValueError as e:
            print(f"An error occurred: {e}")
            self.reset_labels(user_id)

    def _reset_sp500_labels(self, user_id):
        """Reset S&P500 labels to zero when yearly savings is non-positive."""
        labels = ["sp500_savings_20_labels", "sp500_savings_50_labels", "sp500_savings_70_labels"]
        for label in labels:
            self.ui_refs[user_id][label].setText("S&P500 Savings: £0.00")

    def reset_labels(self, user_id):
        """Used to reset UI Labels to 0 values, used mainly when errors take place"""
        self.ui_refs[user_id]["percentage_labels"].setText(f"{0:.0f}%")
        self.ui_refs[user_id]["shared_expense_labels"].setText(f"Shared Contribution: £{0:.2f}")
        self.ui_refs[user_id]["monthly_savings_labels"].setText(f"Monthly Savings: £{0:.2f}")
        self.ui_refs[user_id]["yearly_savings_labels"].setText(f"Yearly Savings: £{0:.2f}")
        self.ui_refs[user_id]["decade_savings_labels"].setText(f"Decade Savings: £{0:.2f}")
        self.ui_refs[user_id]["sp500_savings_20_labels"].setText("S&P500 20% Savings: £0.00")
        self.ui_refs[user_id]["sp500_savings_50_labels"].setText("S&P500 50% Savings: £0.00")
        self.ui_refs[user_id]["sp500_savings_70_labels"].setText("S&P500 70% Savings: £0.00")

    def compile_user_data(self):
        """Prepare user details and shared expenses for saving"""
        saved_user_details = {}
        for user_id, user_details in self.user_details.items():
            saved_user_details[user_id] = {}
            for key, value in user_details.items():
                if key == "expenses" and isinstance(value, dict):
                    safe_expenses = {}
                    for expense, widgets in value.items():
                        if isinstance(widgets, list | tuple) and widgets:
                            widget = widgets[0]
                            if hasattr(widget, "text"):
                                safe_expenses[expense] = widget.text()
                            else:
                                safe_expenses[expense] = str(widget)
                        else:
                            safe_expenses[expense] = ""
                    saved_user_details[user_id][key] = safe_expenses
                else:
                    saved_user_details[user_id][key] = value

        saved_data = {
            "user_details": saved_user_details,
            "shared_expenses": {key: value[0].text() for key, value in self.shared_expenses.items()}
        }
        return saved_data, saved_user_details

    def save_defaults(self):
        """Save default expense and income values to SQLite DB and remove orphaned expenses."""

        saved_data, saved_user_details = self.compile_user_data()
        db_path = Path(__file__).resolve().parent.parent / "finance_saving_app" / "data" / "data.db"
        os.makedirs("../data", exist_ok=True)

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Create tables if they don't exist
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    income REAL,
                    income_type INTEGER
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    user_id TEXT,
                    expense_name TEXT,
                    expense_value REAL,
                    PRIMARY KEY(user_id, expense_name),
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS shared_expenses (
                    expense_name TEXT PRIMARY KEY,
                    expense_value REAL
                )
                """)

                # --- Helper function for syncing user expenses ---
                def sync_user_expenses(user_id, current_expenses):
                    cursor.execute(
                        "SELECT expense_name FROM expenses WHERE user_id = ?",
                        (user_id,)
                                    )
                    db_expenses = {row[0] for row in cursor.fetchall()}
                    current_expense_names = set(current_expenses.keys())

                    # Find expenses in DB that are not in current_expenses
                    expenses_to_remove = db_expenses - current_expense_names

                    for expense in expenses_to_remove:
                        cursor.execute("""
                            DELETE FROM expenses
                            WHERE user_id = ? AND expense_name = ?
                        """, (user_id, expense))

                # --- Helper function for syncing shared expenses ---
                def sync_shared_expenses(current_shared_expenses):
                    cursor.execute("SELECT expense_name FROM shared_expenses")
                    db_shared_expenses = {row[0] for row in cursor.fetchall()}
                    current_shared_names = set(current_shared_expenses.keys())

                    # Find shared expenses in DB that are not in current data
                    shared_to_remove = db_shared_expenses - current_shared_names

                    for expense in shared_to_remove:
                        cursor.execute("""
                            DELETE FROM shared_expenses
                            WHERE expense_name = ?
                        """, (expense,))

                # Insert or update user details
                for user_id, details in saved_user_details.items():
                    name = details.get("name", "")
                    income = details.get("wage", 0)
                    income_type = details.get("wage_type", 0)

                    cursor.execute(
                        """
                        INSERT INTO users (user_id, name, income, income_type)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET
                            name = excluded.name,
                            income = excluded.income,
                            income_type = excluded.income_type
                        """,
                        (user_id, name, income, int(income_type)),
                    )

                    # Sync: remove old expenses not in current data
                    expenses = details.get("expenses", {})
                    sync_user_expenses(user_id, expenses)

                    # Insert or update current expenses
                    for exp_name, exp_value in expenses.items():
                        try:
                            exp_value = float(exp_value)
                        except ValueError:
                            exp_value = 0
                        cursor.execute(
                            """
                            INSERT INTO expenses (user_id, expense_name, expense_value)
                            VALUES (?, ?, ?)
                            ON CONFLICT(user_id, expense_name)
                            DO UPDATE SET expense_value = excluded.expense_value
                            """,
                            (user_id, exp_name, exp_value)
                        )

                # Sync shared expenses before inserting/updating
                sync_shared_expenses(saved_data["shared_expenses"])

                # Insert or update shared expenses
                for exp_name, exp_value in saved_data["shared_expenses"].items():
                    try:
                        exp_value = float(exp_value)
                    except ValueError:
                        exp_value = 0
                    cursor.execute("""
                        INSERT INTO shared_expenses (expense_name, expense_value)
                        VALUES (?, ?)
                        ON CONFLICT(expense_name) DO UPDATE SET expense_value=excluded.expense_value
                    """, (exp_name, exp_value))

                conn.commit()

            QtWidgets.QMessageBox.information(self, "Success", f"Defaults saved to {db_path}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save SQL data: {e}")

    def load_defaults(self):
        """Load default expense and income values from SQLite or fallback to JSON."""
        db_path = Path(__file__).resolve().parent.parent / "finance_saving_app" / "data" / "data.db"


        # Hardcoded defaults for fallback
        default_user_details = {
            "01": {"name": "Kent", "wage": 4000, "wage_type": True, "expenses": {}}
        }
        default_shared_expenses = {
            "Rent/Mortgage": 1250,
            "Electricity/Gas": 50,
            "Water": 17,
            "Council Tax": 50,
            "Internet": 10,
            "Misc": 5
        }

        try:
            print("db_path: ", db_path)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone():
                # Load user details
                cursor.execute("SELECT user_id, name, income, income_type FROM users")
                users = cursor.fetchall()

                self.user_details = {}
                for user_id, name, income, income_type in users:
                    self.user_details[user_id] = {
                        "name": name,
                        "wage": income,
                        "wage_type": bool(int(income_type)),
                        "expenses": {}
                    }
                    # Load expenses for this user
                    cursor.execute(
                        "SELECT expense_name, expense_value FROM expenses WHERE user_id=?",
                        (user_id,)
                                    )
                    expenses = cursor.fetchall()
                    self.user_details[user_id]["expenses"] = {
                        name: str(value) for name, value in expenses
                    }

                # Load shared expenses
                cursor.execute("SELECT expense_name, expense_value FROM shared_expenses")
                shared_expenses = cursor.fetchall()
                self.shared_expenses = {name: str(value) for name, value in shared_expenses}

                conn.close()

                if self.user_details or self.shared_expenses:
                    return

            conn.close()

        except Exception as e:
            # If SQLite fails, log it
            print(f"SQLite load error: {e}")
        if not self.user_details:
            self.user_details = default_user_details
        if not self.shared_expenses:
            self.shared_expenses = default_shared_expenses

    def get_default_individual_expenses(self, user_id):
        """
        Retrieve saved individual expenses for a user or fallback to defaults.

        Args (string): ID assigned to a user, "01, 05, 11" etc. Is a key in user_details

        Returns (dict): dictionary containing expense names as keys, and value of expense as value.
        """
        defaults = {
            "Food": 0,
            "Gym Membership": 50,
            "Transport": 150,
            "Phone Bills": 35,
            "Personal Care": 20,
            "Hobbies": 50,
        }

        try:
            user_data = self.user_details.get(user_id)
            if not user_data:
                raise KeyError(f"User '{user_id}' not found in user details.")

            saved_defaults = user_data.get("expenses")
            if not isinstance(saved_defaults, dict):
                raise TypeError(f"Expected 'expenses' to be a dict, got {type(saved_defaults)}.")

            return saved_defaults if saved_defaults else defaults

        except (KeyError, TypeError) as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self,"Error",f"Unexpected error occurred: {e}")

        return defaults


def launch(open_on_details=False):
    """
    Launch the budgeting tool window as a standalone PyQt app.

    Returns (string): instance tag of the Budgeting Tool class
    """

    app = get_app()

    for widget in app.topLevelWidgets():
        if widget.objectName() == OBJECT_NAME:
            widget.close()
            widget.deleteLater()

    budget_tool = BudgetingTool(open_on_details=open_on_details)
    budget_tool.setObjectName(OBJECT_NAME)
    budget_tool.show()

    sys.exit(app.exec_())

def increment_key(key: str) -> str:
    """Returns the key value decremented by 1 while keeping leading zero."""
    return str(f"{int(key) + 1:02d}")


def decrement_key(key: str) -> str:
    """Returns the key value decremented by 1 while keeping leading zero."""
    return str(f"{int(key) - 1:02d}")


def show_layout(layout):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()
        if widget:
            widget.show()


def hide_layout(layout):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()
        if widget:
            widget.hide()



# Run the budgeting tool in Maya or standalone
if __name__ == "__main__":
    launch()

