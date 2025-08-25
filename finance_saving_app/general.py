import os
import platform
import sys

from pathlib import Path

if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    CURRENT_DIR = sys._MEIPASS
else:
    # Running as a normal script
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

ICONS_DIR = os.path.join(CURRENT_DIR, "icons")

def get_documents_folder():
    system = platform.system()
    if system == "Windows":
        return Path(os.environ["USERPROFILE"]) / "Documents"
    elif system == "Darwin":  # macOS
        return Path.home() / "Documents"
    elif system == "Linux":
        return Path.home() / "Documents"
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")


def get_data_file_path(file_name):
    """Get the full path for the default expenses file."""
    document_folder = get_documents_folder()  # User's home directory
    return os.path.join(document_folder, file_name)


def calculate_after_tax(monthly_wage):
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
    # additional_rate_threshold = 125140  # Above this amount is taxed at 45%

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
        tax = (basic_rate_limit - personal_allowance) * 0.20 + (
                annual_wage - basic_rate_limit) * 0.40
    else:
        tax = (basic_rate_limit - personal_allowance) * 0.20 + (
                higher_rate_limit - basic_rate_limit) * 0.40 + (
                annual_wage - higher_rate_limit) * 0.45

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


def project_sp500_savings(
        initial_savings,
    annual_contribution,
    years,
    sp500_percentage,
    annual_return=0.07,
    safe_return=0.02
):
    """
    Simulate the savings over time with annual contributions and a portion invested in the S&P 500.

    Args:
        initial_savings (float): The initial savings amount.
        annual_contribution (float): The amount added to savings each year.
        years (int): The number of years to simulate growth.
        sp500_percentage (float): The percentage of savings allocated to the S&P 500 (0 to 100).
        annual_return (float): The annual return rate of the S&P 500 (default is 7% or 0.07).
        safe_return (float): Annual return rate of the non-invested portion (default is 2% or 0.02).

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


def shift_color(rgb: tuple[int, int, int], factor: float = 0.8) -> tuple[int, int, int]:
    """Return an RGB tuple scaled by `factor`, clamped to [0, 255]."""
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)
