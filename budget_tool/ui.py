from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import os
import sys
import json
from functools import partial
import platform
from pathlib import Path

# from utils import CollapsibleWidget

# QApplication setup
QApplication = QtWidgets.QApplication
global app
app = QApplication.instance()  # Retrieve existing QApplication instance if available
if not app:
    app = QApplication(sys.argv)

OBJECT_NAME = "budget_tool"
# Get the absolute path of the current script
CURRENT_DIR = 'C:/Users/Kent/Desktop/budget_tool'

# Build the path to the icons folder
ICONS_DIR = os.path.join(CURRENT_DIR, "icons")

def get_main_window():
    """Return a handle to the Maya main window."""
    return next(w for w in app.topLevelWidgets() if w.objectName() == "MayaWindow")


# Class for setting up Widget under the Head in Collapsible Header
# -------------------------------------------------------------------------------------------
class CollapsibleHeader(QtWidgets.QWidget):
    # Grabbing arrow pngs' from mayas' default UI library

    COLLAPSED_PIXMAP = QtGui.QPixmap(":teRightArrow.png")
    EXPANDED_PIXMAP = QtGui.QPixmap(":teDownArrow.png")

    # Creating a signal for clicking the header

    clicked = QtCore.pyqtSignal()

    # function that auto-starts up when CollapsibleHeader() is called
    def __init__(self, text, parent=None):
        super(
            CollapsibleHeader,
            self,
        ).__init__(parent)

        # need to set this or the header won't get color despite setting
        # pallete
        self.setAutoFillBackground(True)
        self.set_background_color(None)
        # icon that uses the arrow pngs' and setting width to width of png
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedWidth(self.COLLAPSED_PIXMAP.width())

        # text label that uses text passes in function creation and enabling
        # mouse clicked on it
        self.text_label = QtWidgets.QLabel()
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        # creating main layout and setting its margins, then adding all
        # previous widgets to the layout
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(
            4,
            4,
            4,
            4,
        )


        self.main_layout.addWidget(self.text_label)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)

        # setting defaults, calling below functions
        self.set_text(text)
        self.set_expanded(True)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )

    # sets text label with passed text and formats it as bold
    def set_text(
        self,
        text,
    ):
        self.text_label.setText("<b>{0}</b>".format(text))

    # gets the background color from qpushbutton pallete which carries mayas
    # default grey
    def set_background_color(self, color=None):
        if color is None:
            color = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)
        elif isinstance(color, tuple) and len(color) == 3:
            color = QtGui.QColor(*color)

        palette = self.palette()
        palette.setColor(
            QtGui.QPalette.Window,
            color,
        )
        self.setPalette(palette)

    # returns or = if widget is expanded
    def is_expanded(
        self,
    ):
        return self._expanded

    # function that sets state of widget collapsed or expanded
    def set_expanded(
        self,
        expanded,
    ):
        self._expanded = expanded

        # changes the png arrow for either state
        if self._expanded:
            self.icon_label.setPixmap(self.EXPANDED_PIXMAP)
        else:
            self.icon_label.setPixmap(self.COLLAPSED_PIXMAP)

    # overrides mouseReleaseEvent to emit a signal
    def mouseReleaseEvent(
        self,
        event,
    ):
        self.clicked.emit()  # pylint: disable=E1101


class CollapsibleWidget(QtWidgets.QWidget):
    # function that auto-starts up when CollapsibleHeader() is called
    def __init__(self, text, parent=None, window=None):
        super(
            CollapsibleWidget,
            self,
        ).__init__(parent)

        self.tool_window = window
        # calls for Header
        self.header_wdg = CollapsibleHeader(text)
        self.header_wdg.clicked.connect(self.on_header_clicked)

        # Creates body widget for part below header
        self.body_wdg = QtWidgets.QWidget()

        # parents body layout to the body widget and sets spacing settings
        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(
            4,
            2,
            4,
            2,
        )
        self.body_layout.setSpacing(3)

        # creates main layout to house header and the body widget
        self.details_layout = QtWidgets.QVBoxLayout(self)
        self.details_layout.setSpacing(1)
        self.details_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self.details_layout.addWidget(self.header_wdg)
        self.details_layout.addWidget(self.body_wdg)

        # set default states of collapsible widget
        self.set_expanded(True)

        # making addWidget function for class

    def add_widget(
        self,
        widget,
    ):
        self.body_layout.addWidget(widget)

        # making addLayout function for class

    def add_layout(
        self,
        layout,
    ):
        self.body_layout.addLayout(layout)

        # making setState function for class

    def set_expanded(
        self,
        expanded,
    ):
        self.header_wdg.set_expanded(expanded)
        self.body_wdg.setVisible(expanded)

        # making easy color change function to class

    def set_header_background_color(
        self,
        color,
    ):
        self.header_wdg.set_background_color(color)

        # sends signal

    def on_header_clicked(
        self,
    ):
        self.set_expanded(not self.header_wdg.is_expanded())

class BudgetingTool(QtWidgets.QDialog):
    """Main dialog for the Couples Budgeting Tool."""

    def __init__(self, parent=None, open_on_details=False):
        super(BudgetingTool, self).__init__(parent)

        self.setWindowTitle("Couples Budgeting Tool")
        '''
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                color: #202020;
            }
        """)
        '''
        self.open_on_details = open_on_details
        self.user_details = None 
        self.user_ui_elements = {}
        self.shared_expenses = None
        self.load_defaults()

        self.partner_groupboxes = []  
        
        self.init_ui()
        
        self.update_percentages()


    def init_ui(self):
        """Initialize the main UI layout."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        self.tab_layout = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tab_layout)
        
        details_tab = QtWidgets.QWidget()
        self.details_layout = QtWidgets.QVBoxLayout()
        details_tab.setLayout(self.details_layout)
        
        start_tab = QtWidgets.QWidget()
        self.start_layout = QtWidgets.QVBoxLayout()
        start_tab.setLayout(self.start_layout)
        
        self.tab_layout.addTab(start_tab, "Start")
        self.tab_layout.addTab(details_tab, "Details")
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
        load_button.clicked.connect(self.on_load_default_pressed)
        button_layout.addWidget(load_button)

        self.details_layout.addLayout(button_layout)
        self.details_layout.addStretch()

    def on_load_default_pressed(self):
        self.close()
        new_instance = launch(open_on_details=True)


    def populate_user_layouts(self):
        
        for i, (user_id, user_details_value) in enumerate(self.user_details.items()):
            # Determine if this is the last user group
            is_last = (i == len(self.user_details) - 1)
            # Access name and wage from user_details_value
        
            partner_groupbox, details_groupbox, summary_groupbox, add_remove_layout = self.create_user_group(
                user_id, user_details_value["wage"], last_one=is_last)
            '''
            if not i:
                print(f"{user_id} caused this to happen {add_remove_layout}")
                self.lock_remove_button_in_layout(add_remove_layout)
            '''
        
    def update_details_base_incomes(self):
        # Clear and recreate the partner base layout
        self.clear_layout(self.partner_income_layout)
        self.partner_income_layout = self.create_individual_income_layout()
        self.details_layout.insertLayout(0, self.partner_income_layout)
        
    def clear_layout(self, layout):
        # Remove all widgets from the layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())  # Recursively clear nested layouts

        # Remove the layout itself from the parent layout
        self.start_layout.removeItem(layout)

                    
    
    def hide_layout(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.hide()

    def show_layout(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.show()
    
    def decrement_key(self, key: str) -> str:
        """Returns the key value decremented by 1 while keeping leading zero."""
        return str(f"{int(key) - 1:02d}")

    def increment_key(self, key: str) -> str:
        """Returns the key value decremented by 1 while keeping leading zero."""
        return str(f"{int(key) + 1:02d}")

    def on_partner_count_changed_clicked(self, add=None, user_id = None):
        print("elements: ", self.user_ui_elements)
        if add:
            # todo add a set hidden for add and remove buttons
            self.hide_layout(add)
            # Add a new user group
            user_id = int(user_id) + 1
            user_id = str(f"{user_id:02}")
            self.user_details.update({f"{user_id}":{"name":f"User {user_id}", "wage":50}})
            name = self.user_details[user_id]["name"]
            wage = self.user_details[user_id]["wage"]

            partner_groupbox, details_groupbox, summary_groupbox, add_remove_layout = self.create_user_group(
                user_id, wage, last_one=True)


        elif user_id in self.user_ui_elements:

            partner_groupbox, details_groupbox, summary_groupbox, add_remove_layout = self.user_ui_elements[user_id]["group_widgets"]
            self.user_start_layout.removeWidget(partner_groupbox)
            self.user_details_layout.removeWidget(details_groupbox)
            self.user_summary_layout.removeWidget(summary_groupbox)
            
            partner_groupbox.deleteLater()
            details_groupbox.deleteLater()
            summary_groupbox.deleteLater()


            next_partner_groupbox, next_details_groupbox, summary_groupbox, next_add_remove_layout = self.user_ui_elements[self.decrement_key(user_id)]["group_widgets"]
            # Do something with the next set
            self.show_layout(next_add_remove_layout)

            del self.user_ui_elements[user_id]
            del self.user_details[user_id]
            if len(self.user_ui_elements.keys()) == 1:
                print("going to one")
                self.lock_remove_button_in_layout(next_add_remove_layout)

                self.user_start_layout.addLayout(next_add_remove_layout)
        self.update_percentages(user_id)
        
    def lock_remove_button_in_layout(self, layout):
        for i in range(layout.count()):  # Iterate through layout items
            item = layout.itemAt(i)      # Get the layout item
            widget = item.widget()       # Get the widget
            if widget:  # Check if it's a widget

                # Identify the second button and disable it
                if i == 1 and isinstance(widget, QtWidgets.QPushButton):  # Check if it's the second widget and a button
                    widget.hide()

    
    def create_user_group(self, user_id, user_details_value, last_one=False):
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
            partial(self.on_partner_count_changed_clicked, add=add_remove_partner_layout, user_id = user_id)
        )

        icon_add = os.path.normpath(os.path.join(CURRENT_DIR, "icons", "plus.png")).replace("\\", "/")
        add_partner_button.setIcon(QtGui.QIcon(icon_add))
        add_remove_partner_layout.addWidget(add_partner_button)

        # Remove Partner Button
        remove_partner_button = QtWidgets.QPushButton()

        remove_partner_button.clicked.connect(
            partial(self.on_partner_count_changed_clicked, add=False, user_id=user_id)
        )

        icon_remove = os.path.normpath(os.path.join(CURRENT_DIR, "icons", "minus.png")).replace("\\", "/")
        remove_partner_button.setIcon(QtGui.QIcon(icon_remove))
        add_remove_partner_layout.addWidget(remove_partner_button)

        base_layout.addLayout(add_remove_partner_layout)
        if not last_one:
            self.hide_layout(add_remove_partner_layout)

        # User Input Layouts
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Name: ")
        name_line_edit = QtWidgets.QLineEdit()
        name_line_edit.setPlaceholderText("Enter Name: eg. Joesph")
        name_line_edit.setText(self.user_details[user_id]["name"])
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_line_edit)

        wage_layout = QtWidgets.QHBoxLayout()
        wage_label = QtWidgets.QLabel("Monthly Wage: ")
        wage_line_edit = QtWidgets.QLineEdit()
        wage_line_edit.setText(str(user_details_value))
        wage_layout.addWidget(wage_label)
        wage_layout.addWidget(wage_line_edit)
        wage_line_edit.setPlaceholderText("Enter income: eg. 2500")
        self.user_ui_elements.update({user_id:{"income_widget":wage_line_edit}})

        partner_layout.addLayout(name_layout)
        partner_layout.addLayout(wage_layout)
        partner_layout.addStretch()
        add_remove_partner_layout.addStretch()

        # Creating the details version of the user label
        details_partner_groupbox = QtWidgets.QGroupBox(f"{self.user_details[user_id]['name']}s' Monthly Income")
        details_base_layout = QtWidgets.QHBoxLayout()
        details_partner_groupbox.setLayout(details_base_layout)

        if user_details_value != 0:
            after_tax_value = self.calculate_after_tax(user_details_value)
        else:
            after_tax_value = 0
        after_tax_value_label = QtWidgets.QLabel(f"After Tax Monthly Income: ${after_tax_value}")

        details_base_layout.addWidget(after_tax_value_label)

        user_number = user_id
        name = name_line_edit.text()
        wage = user_details_value

        # Connect signals to update the details dynamically
        def update_details():
            # Update the group box title and label dynamically
            name = name_line_edit.text()
            try:
                wage = float(wage_line_edit.text())
            except ValueError:
                wage = 0
            after_tax_wage = self.calculate_after_tax(wage)

            details_partner_groupbox.setTitle(f"{name}s' Monthly Income")
            after_tax_value_label.setText(f"After Tax Monthly Income: ${after_tax_wage:.2f}")
            self.update_details_sheet(set_name=[user_number,name])
            self.update_details_sheet(set_wage=[user_number,wage])
            self.update_percentages()

        name_line_edit.textChanged.connect(update_details)
        wage_line_edit.textChanged.connect(update_details)

        partner_groupbox.setMaximumHeight(100)

        summary_widget = QtWidgets.QWidget()
        summary_layout = QtWidgets.QVBoxLayout()
        summary_widget.setLayout(summary_layout)
        individual_expenses_groupbox = self.create_individual_expenses_groupbox(len(self.user_details), user_id)
        financial_summary_groupbox = self.create_budget_share_layout(user_id)
        summary_layout.addWidget(individual_expenses_groupbox)
        summary_layout.addLayout(financial_summary_groupbox)

        self.user_ui_elements[user_id]["group_widgets"] = (partner_groupbox, details_partner_groupbox, summary_widget, add_remove_partner_layout)
        self.user_start_layout.addWidget(partner_groupbox)
        self.user_details_layout.addWidget(details_partner_groupbox)
        self.user_summary_layout.addWidget(summary_widget)


        return partner_groupbox, details_partner_groupbox, summary_widget, add_remove_partner_layout
        
    def update_details_sheet(self, set_name=None, set_wage=None):
        
        
        if set_name:
            user_number = len(self.user_details) + 1
            self.user_details[set_name[0]].update({"name":set_name[1]})
            self.user_details[set_name[0]].update({"wage":0})
            
    
        if set_wage:
            self.user_details[set_wage[0]].update({"wage":set_wage[1]})
        
    def simulate_savings_growth_with_contributions(
        self,
        initial_savings, 
        annual_contribution, 
        years, 
        sp500_percentage, 
        annual_return=0.07, 
        safe_return=0.02
    ):
        """
        Simulate the growth of savings over time with annual contributions and a portion invested in the S&P 500.

        Args:
            initial_savings (float): The initial savings amount.
            annual_contribution (float): The amount added to savings each year.
            years (int): The number of years to simulate growth.
            sp500_percentage (float): The percentage of savings allocated to the S&P 500 (0 to 100).
            annual_return (float): The annual return rate of the S&P 500 (default is 7% or 0.07).
            safe_return (float): The annual return rate of the non-invested portion (default is 2% or 0.02).

        Returns:
            float: The total savings amount after the specified number of years.
        """
        if not (0 <= sp500_percentage <= 100):
            raise ValueError("sp500_percentage must be between 0 and 100.")
        if initial_savings < 0 or annual_contribution < 0:
            raise ValueError("Initial savings and annual contribution must be non-negative.")
        if years <= 0:
            raise ValueError("Years must be a positive number.")

        # Convert percentage to decimal
        sp500_percentage /= 100

        # Initialize savings
        sp500_savings = initial_savings * sp500_percentage
        safe_savings = initial_savings * (1 - sp500_percentage)

        # Simulate growth with annual contributions
        for _ in range(years):
            # Apply growth to existing savings
            sp500_savings *= (1 + annual_return)
            safe_savings *= (1 + safe_return)

            # Add annual contributions to each portion
            sp500_savings += annual_contribution * sp500_percentage
            safe_savings += annual_contribution * (1 - sp500_percentage)

        # Combine the total savings
        total_savings = sp500_savings + safe_savings
        return total_savings


    
    def calculate_after_tax(self, monthly_wage):
        """
        Calculate the after-tax value of a monthly wage in pounds.
        
        Parameters:
            monthly_wage (float): The gross monthly wage in pounds.
        
        Returns:
            float: The after-tax monthly wage in pounds.
        """
        # Convert monthly wage to annual wage
        annual_wage = monthly_wage * 12

        # UK Tax Bands and Allowances (2024-2025)
        personal_allowance = 12570  # Tax-free allowance
        basic_rate_limit = 50270    # Up to this amount is taxed at 20%
        higher_rate_limit = 125140  # Up to this amount is taxed at 40%
        additional_rate_threshold = 125140  # Above this amount is taxed at 45%

        # National Insurance thresholds (monthly)
        ni_free_threshold = 1048    # Below this, no NI contributions
        ni_lower_limit = 1048       # Between this and �4189, NI is 12%
        ni_upper_limit = 4189       # Above this, NI is 2%

        # Calculate Income Tax
        if annual_wage <= personal_allowance:
            tax = 0
        elif annual_wage <= basic_rate_limit:
            tax = (annual_wage - personal_allowance) * 0.20
        elif annual_wage <= higher_rate_limit:
            tax = (basic_rate_limit - personal_allowance) * 0.20 + (annual_wage - basic_rate_limit) * 0.40
        else:
            tax = (basic_rate_limit - personal_allowance) * 0.20 + (higher_rate_limit - basic_rate_limit) * 0.40 + (annual_wage - higher_rate_limit) * 0.45

        # Calculate National Insurance
        if monthly_wage <= ni_free_threshold:
            ni = 0
        elif monthly_wage <= ni_upper_limit:
            ni = (monthly_wage - ni_lower_limit) * 0.12
        else:
            ni = (ni_upper_limit - ni_lower_limit) * 0.12 + (monthly_wage - ni_upper_limit) * 0.02

        # Convert annual tax to monthly
        monthly_tax = tax / 12

        # Calculate after-tax monthly wage
        after_tax_wage = monthly_wage - monthly_tax - ni

        return round(after_tax_wage, 2)

        
    def create_individual_income_layout(self):
        """Create the layout for partner income inputs with default values."""
        layout = QtWidgets.QHBoxLayout()

        # Load default incomes
        default_incomes = self.user_details

        for i, (user_id, user_details_value) in enumerate(self.user_details.items()):
            groupbox = QtWidgets.QGroupBox(f"{user_details_value['name']} Monthly Income")
            group_layout = QtWidgets.QVBoxLayout()
            groupbox.setLayout(group_layout)
            layout.addWidget(groupbox)
            
            if user_details_value != 0:
                after_tax_value = self.calculate_after_tax(user_details_value)
            else: 
                after_tax_value = 0
            after_tax_value_label = QtWidgets.QLabel(f"After Tax Monthly Income: ${user_details_value['wage']}")
            
            group_layout.addWidget(after_tax_value_label)
            
            

        return layout

    def create_shared_expenses_section(self):
        """Create a collapsible widget for fixed expenses with default values."""
        section = CollapsibleWidget("Shared Expenses")
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

            remove_button = QtWidgets.QPushButton("Remove")
            remove_button.clicked.connect(partial(self.remove_expense,expense))
            # Put the line_edit and remove_button side-by-side
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.addWidget(line_label)
            h_layout.addWidget(line_edit)
            h_layout.addWidget(remove_button)

            form_layout.addRow(h_layout)

            self.shared_expenses[expense] = [line_edit, remove_button, h_layout]

        # Add "Add New Expense" button
        add_button = QtWidgets.QPushButton("Add New Expense")
        add_button.clicked.connect(lambda: self.add_new_expense(form_layout, None))
        form_layout.addRow(add_button)

        # Wrap the layout in a widget
        form_widget = QtWidgets.QWidget()
        form_widget.setLayout(form_layout)
        section.add_widget(form_widget)

        return section

    def create_individual_expenses_section(self):
        """Create a collapsible widget for partner-specific expenses."""
        section = CollapsibleWidget("Partner-Specific Expenses")

        # Create a horizontal layout for all partners
        self.user_summary_layout = QtWidgets.QHBoxLayout()

        # Wrap the layout in a widget
        wrapper_widget = QtWidgets.QWidget()
        wrapper_widget.setLayout(self.user_summary_layout)
        section.add_widget(wrapper_widget)

        return section

    
    def create_individual_expenses_groupbox(self, i, user):

        # Parent vertical layout for each partner
        partner_vertical_layout = QtWidgets.QVBoxLayout()

        # Create groupbox for partner expenses
        expense_groupbox = QtWidgets.QGroupBox(f"User {i}'s Expenses")
        expense_layout = QtWidgets.QFormLayout()
        expense_groupbox.setLayout(expense_layout)

        # Get default expenses for the partner
        base_expenses = self.get_default_individual_expenses(user)
        #saved_defaults = self.load_user_defaults().get(f"user_{i}_expenses", {})
        default_expenses = {**base_expenses}

        users_individual_expenses = {}
        # Add default expenses to the form layout
        for expense, default_value in default_expenses.items():
            expense_edit = QtWidgets.QLineEdit()
            expense_edit.setPlaceholderText(f"Enter {expense.lower()} value")
            expense_edit.setText(str(default_value))
            expense_edit.textChanged.connect(self.update_percentages)
            expense_layout.addRow(QtWidgets.QLabel(expense), expense_edit)

            users_individual_expenses[expense] = expense_edit
           
        self.user_details[user]["expenses"] = users_individual_expenses
        # Add "Add New Expense" button
        add_button = QtWidgets.QPushButton("Add New Expense")
        add_button.clicked.connect(lambda i=i: self.add_new_expense(expense_layout, user=user))
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
        
        # user_layout.addLayout(user_group_layout)
        
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
        contribution_label = QtWidgets.QLabel("$0.00")
        contribution_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(contribution_label)
        
        # Individual Expenses
        individual_expenses_label = QtWidgets.QLabel("$0.00")
        individual_expenses_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(individual_expenses_label)
        
        # Spacer
        spacer_label = QtWidgets.QLabel("----------")
        spacer_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(spacer_label)
        
        
        # Monthly savings label
        monthly_savings_label = QtWidgets.QLabel("Monthly Savings: $0.00")
        monthly_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(monthly_savings_label)

        # Yearly savings label
        yearly_savings_label = QtWidgets.QLabel("Yearly Savings: $0.00")
        yearly_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(yearly_savings_label)
        
        # Decade savings label
        decade_savings_label = QtWidgets.QLabel("Decade Savings: $0.00")
        decade_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(decade_savings_label)
        
        # Spacer
        spacer_label = QtWidgets.QLabel("----------")
        spacer_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(spacer_label)
        
        # Decade savings label
        sp500_20_savings_label = QtWidgets.QLabel("S&P 20% Savings: $0.00")
        sp500_20_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(sp500_20_savings_label)
        
        # Decade savings label
        sp500_50_savings_label = QtWidgets.QLabel("S&P 50% Savings: $0.00")
        sp500_50_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(sp500_50_savings_label)
        
        # Decade savings label
        sp500_70_savings_label = QtWidgets.QLabel("S&P 70% Savings: $0.00")
        sp500_70_savings_label.setAlignment(QtCore.Qt.AlignCenter)
        group_layout.addWidget(sp500_70_savings_label)
        
        self.user_ui_elements.update({user_id:{}})
        
        self.user_ui_elements[user_id].update({"percentage_labels":percentage_label})
        self.user_ui_elements[user_id].update({"expense_contribution_labels":contribution_label})
        self.user_ui_elements[user_id].update({"individual_expenses":individual_expenses_label})
        self.user_ui_elements[user_id].update({"monthly_savings_labels":monthly_savings_label})
        self.user_ui_elements[user_id].update({"yearly_savings_labels":yearly_savings_label})
        self.user_ui_elements[user_id].update({"decade_savings_labels":decade_savings_label})
        self.user_ui_elements[user_id].update({"sp500_savings_20_labels":sp500_20_savings_label})
        self.user_ui_elements[user_id].update({"sp500_savings_50_labels":sp500_50_savings_label})
        self.user_ui_elements[user_id].update({"sp500_savings_70_labels":sp500_70_savings_label})
        
        
            

        return sub_layout
    
    def add_new_expense(self, layout, user=None):
        """Add a new expense field to the fixed expenses section with a custom label."""

        if user:
            line_edit = self.user_details[user]["expenses"].keys()
        else:
            line_edit = self.shared_expenses.keys()
        # Prompt the user for a label name
        label_name, ok = QtWidgets.QInputDialog.getText(
            self, "New Expense", "Enter the name for the new expense:"
        )

        if not ok or not label_name.strip():  # Cancel or empty input
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Expense name cannot be empty.")
            return

        label_name = label_name.strip()

        # Check if the label name already exists
        if label_name in line_edit:
            QtWidgets.QMessageBox.warning(self, "Duplicate Label", f"An expense named '{label_name}' already exists.")
            return

        # Create new label and input field
        new_label = QtWidgets.QLabel(label_name)
        new_edit = QtWidgets.QLineEdit()
        new_edit.setPlaceholderText(f"Enter {label_name.lower()} value")
        new_edit.textChanged.connect(self.update_percentages)
        remove_button = QtWidgets.QPushButton("Remove")
        remove_button.clicked.connect(partial(self.remove_expense, label_name))

        # Insert the new row before the "Add New Expense" button
        row_count = layout.rowCount()  # Total rows in the layout
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(new_label)
        h_layout.addWidget(new_edit)
        h_layout.addWidget(remove_button)
        
        layout.insertRow(row_count - 1, h_layout)

        if user:
            self.user_details[user]["expenses"][label_name] = new_edit
        else:
            self.shared_expenses[label_name] = new_edit, remove_button, h_layout

    def remove_expense(self, expense):

        expense_layout = self.shared_expenses[expense][-1]
        self._clear_layout(expense_layout)
        self.shared_expenses.pop(expense)

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

    def update_percentages(self, user_id=None):
        """Update the percentage share, contribution, and savings display."""

        wages = [value["wage"] for value in self.user_details.values()]
        post_tax_wages = [self.calculate_after_tax(wage) for wage in wages]
        total_wages = sum(post_tax_wages)

        try:
            edit_widgets = []
            print(self.shared_expenses.values())
            for values in self.shared_expenses.values():
                edit_widgets.append(values[0])

            for edit in edit_widgets:
                print(edit.text())

            total_shared_expenses = sum(
                float(edit.text()) if edit.text() else 0 for edit in edit_widgets
            )

            for i, (user_id, value) in enumerate(self.user_details.items()):

                pre_tax_income = value["wage"]
                income = self.calculate_after_tax(pre_tax_income)

                # Calculate individual expenses for this user
                individual_expenses = sum(
                    float(edit.text()) if edit.text() else 0 for edit in value["expenses"].values()
                )
                total_expenses = total_shared_expenses + individual_expenses

                if total_wages > 0:
                    # Percentage share of income
                    percentage = (income / total_wages) * 100
                    self.user_ui_elements[user_id]["percentage_labels"].setText(f"{percentage:.0f}%")
                    # Contribution to shared expenses
                    contribution = (income / total_wages) * total_shared_expenses

                    self.user_ui_elements[user_id]["expense_contribution_labels"].setText(f"Shared Contribution: ${contribution:.2f}")
                    self.user_ui_elements[user_id]["individual_expenses"].setText(f"Individual Expenses: ${individual_expenses:.2f}")
                    # Calculate savings (after individual expenses and contribution)
                    monthly_savings = income - contribution - individual_expenses
                    yearly_savings = monthly_savings * 12
                    decade_savings = monthly_savings * 120

                    self.user_ui_elements[user_id]["monthly_savings_labels"].setText(f"Monthly Savings: ${monthly_savings:.2f}")
                    self.user_ui_elements[user_id]["yearly_savings_labels"].setText(f"Yearly Savings: ${yearly_savings:.2f}")
                    self.user_ui_elements[user_id]["decade_savings_labels"].setText(f"Decade Savings: ${decade_savings:.2f}")

                    if yearly_savings > 0:
                        # Simulate savings growth for different S&P500 contribution rates
                        sp500_20_savings = self.simulate_savings_growth_with_contributions(yearly_savings, yearly_savings, 10, 20)
                        sp500_50_savings = self.simulate_savings_growth_with_contributions(yearly_savings, yearly_savings, 10, 50)
                        sp500_70_savings = self.simulate_savings_growth_with_contributions(yearly_savings, yearly_savings, 10, 70)

                        self.user_ui_elements[user_id]["sp500_savings_20_labels"].setText(f"S&P500 20% Savings: ${sp500_20_savings:.2f}")
                        self.user_ui_elements[user_id]["sp500_savings_50_labels"].setText(f"S&P500 50% Savings: ${sp500_50_savings:.2f}")
                        self.user_ui_elements[user_id]["sp500_savings_70_labels"].setText(f"S&P500 70% Savings: ${sp500_70_savings:.2f}")
                    else:
                        self.user_ui_elements[user_id]["sp500_savings_20_labels"].setText("S&P500 20% Savings: $0.00")
                        self.user_ui_elements[user_id]["sp500_savings_50_labels"].setText("S&P500 50% Savings: $0.00")
                        self.user_ui_elements[user_id]["sp500_savings_70_labels"].setText("S&P500 70% Savings: $0.00")
                else:
                    self.reset_labels(i)

        except ValueError as e:
            print(f"An error occurred: {e}")
            self.reset_all_labels(user_id)
    
    def reset_all_labels(self, user_id):
        """Reset all percentage, contribution, savings, and S&P500 labels to default values."""
        user_elements = self.user_ui_elements.get(user_id, {})
        
        if not user_elements:
            return  # Exit if user_id is not found
        
        labels_to_reset = [
            ("percentage_labels", "0%"),
            ("expense_contribution_labels", "Shared Contribution: $0.00"),
            ("monthly_savings_labels", "Monthly Savings: $0.00"),
            ("yearly_savings_labels", "Yearly Savings: $0.00"),
            ("decade_savings_labels", "Decade Savings: $0.00"),
            ("sp500_savings_20_labels", "S&P500 20% Savings: $0.00"),
            ("sp500_savings_50_labels", "S&P500 50% Savings: $0.00"),
            ("sp500_savings_70_labels", "S&P500 70% Savings: $0.00"),
        ]
        
        for label_key, default_text in labels_to_reset:
            for label in user_elements.get(label_key, []):
                label.setText(default_text)


    
    def reset_labels(self, i):
        self.percentage_labels[i].setText("0%")
        self.expense_contribution_labels[i].setText("Shared Contribution: $0.00")
        self.monthly_savings_labels[i].setText("Monthly Savings: $0.00")
        self.yearly_savings_labels[i].setText("Yearly Savings: $0.00")
        self.decade_savings_labels[i].setText("Decade Savings: $0.00")
        self.sp500_savings_20_labels[i].setText("S&P500 20% Savings: $0.00")
        self.sp500_savings_50_labels[i].setText("S&P500 50% Savings: $0.00")
        self.sp500_savings_70_labels[i].setText("S&P500 70% Savings: $0.00")
            
    def get_data_file_path(self):
        """Get the full path for the default expenses file."""
        document_folder = self.get_documents_folder()  # User's home directory
        return os.path.join(document_folder, "budget_data.json")

    def get_documents_folder(self):
        system = platform.system()
        if system == "Windows":
            return Path(os.environ["USERPROFILE"]) / "Documents"
        elif system == "Darwin":  # macOS
            return Path.home() / "Documents"
        elif system == "Linux":
            return Path.home() / "Documents"
        else:
            raise NotImplementedError(f"Unsupported OS: {system}")

    def save_defaults(self):
        """Save default expense and income values to a JSON file."""
        file_path = self.get_data_file_path()
        print(file_path)
        # Deep copy the dictionary without modifying the original
        saved_user_details = {
            user_id: {
                key: (
                    {expense: line_edit.text() for expense, line_edit in value.items()}  # Convert QLineEdit to text
                    if key == "expenses" else value  # Keep other values unchanged
                )
                for key, value in user_details.items()
            }
            for user_id, user_details in self.user_details.items()
        }

        # Include shared expenses in the same dictionary
        saved_data = {
            "user_details": saved_user_details,
            "shared_expenses": {key: value.text() for key, value in self.shared_expenses.items()}
        }

        try:
            with open(file_path, "w") as file:
                json.dump(saved_data, file)
            QtWidgets.QMessageBox.information(self, "Success", f"Defaults saved to {file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save defaults: {e}")

    def load_defaults(self):
        """Load default expense and income values from a JSON file."""
        file_path = self.get_data_file_path()
        print(file_path)
        try:
            with open(file_path, "r") as file:
                data = json.load(file)  # Read the file content once

            # Extract user details and shared expenses from loaded data
            self.user_details = data.get("user_details", {"01": {"name": "Kent", "wage": 3400}})
            self.shared_expenses = data.get("shared_expenses", {
                    "Rent/Mortgage": "1250",
                    "Electricity/Gas": "50",
                    "Water": "17",
                    "Council Tax": "50",
                    "Internet": "10",
                    "Misc": "5"
                })


        except FileNotFoundError:
            # Set defaults if file doesn't exist
            self.user_details = {"01": {"name": "Kent", "wage": 3400}}
            self.shared_expenses = {
                "Rent/Mortgage": 1250,
                "Electricity/Gas": 50,
                "Water": 17,
                "Council Tax": 50,
                "Internet": 10,
                "Misc": 5
            }
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load defaults: {e}")
            self.user_details = {"01": {"name": "Kent", "wage": 3400}}
            self.shared_expenses = {}


    def get_default_incomes(self):
        """Retrieve default income values."""
        saved_defaults = self.load_user_defaults()
        return saved_defaults.get("incomes", [0, 0, 0])  # Default to two incomes of 0

        

    def get_default_individual_expenses(self, user):
        """Merge hardcoded defaults with saved defaults."""
        try:
            # Check if user exists in the user details dictionary
            if user not in self.user_details:
                raise KeyError(f"User '{user}' not found in user details.")

            # Attempt to retrieve saved defaults
            saved_defaults = self.user_details.get(user, {}).get("expenses", None)

            # If no saved defaults are found, use the hardcoded defaults
            if not saved_defaults:
                saved_defaults = {
                    "Food": 0,
                    "Gym Membership": 50,
                    "Transport": 150,
                    "Phone Bills": 35,
                    "Personal Care": 20,
                    "Hobbies": 50,
                }

            # Ensure the saved_defaults is a dictionary
            if not isinstance(saved_defaults, dict):
                raise TypeError(f"Expected 'expenses' to be a dictionary, got {type(saved_defaults)}.")

            return saved_defaults

        except KeyError as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"User Error: {e}")
            return {
                "Food": 0,
                "Gym Membership": 50,
                "Transport": 150,
                "Phone Bills": 35,
                "Personal Care": 20,
                "Hobbies": 50,
            }
        except TypeError as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Type Error: {e}")
            return {
                "Food": 0,
                "Gym Membership": 50,
                "Transport": 150,
                "Phone Bills": 35,
                "Personal Care": 20,
                "Hobbies": 50,
            }
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return {
                "Food": 0,
                "Gym Membership": 50,
                "Transport": 150,
                "Phone Bills": 35,
                "Personal Care": 20,
                "Hobbies": 50,
            }


def launch(open_on_details=False):
    """Launch the budgeting tool window as a standalone PyQt app."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])

    # Close existing instance if it's open
    for widget in app.topLevelWidgets():
        if widget.objectName() == OBJECT_NAME:
            widget.close()
            widget.deleteLater()

    # Launch new instance
    budget_tool = BudgetingTool(open_on_details=open_on_details)  # No parent needed for top-level window
    budget_tool.setObjectName(OBJECT_NAME)
    budget_tool.show()

    # Start the event loop if this is the main entry point
    if not QtWidgets.QApplication.instance().startingUp():
        app.exec_()

    return budget_tool


# Run the budgeting tool in Maya or standalone
if __name__ == "__main__":
    launch()

