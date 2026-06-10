"""Unit tests for the pure logic in ``finance_saving_app.general``.

These intentionally cover only the framework-free functions so the suite runs
headless in CI without a Qt/display dependency.
"""

import pytest

from finance_saving_app.general import (
    calculate_after_tax,
    project_sp500_savings,
    shift_color,
)


class TestCalculateAfterTax:
    def test_below_allowance_has_no_deductions(self):
        # 1000/month -> 12000/year, under both the tax allowance and NI threshold.
        assert calculate_after_tax(1000) == 1000.0

    def test_zero_wage_returns_zero(self):
        assert calculate_after_tax(0) == 0.0

    def test_take_home_is_less_than_gross_when_taxed(self):
        gross = 4000
        assert calculate_after_tax(gross) < gross

    def test_take_home_is_monotonic_in_gross(self):
        # Earning more should never reduce take-home pay.
        assert calculate_after_tax(5000) > calculate_after_tax(3000)

    def test_result_is_rounded_to_two_places(self):
        result = calculate_after_tax(3333.33)
        assert result == round(result, 2)


class TestProjectSp500Savings:
    def test_all_safe_allocation_ignores_market_return(self):
        # 0% in the S&P, safe return 0%, single contribution -> exactly the contribution.
        total = project_sp500_savings(
            initial_savings=0,
            annual_contribution=100,
            years=1,
            sp500_percentage=0,
            safe_return=0.0,
        )
        assert total == pytest.approx(100.0)

    def test_growth_increases_total(self):
        total = project_sp500_savings(1000, 1000, 10, 70)
        assert total > 1000

    @pytest.mark.parametrize("bad_pct", [-1, 101, 150])
    def test_rejects_out_of_range_percentage(self, bad_pct):
        with pytest.raises(ValueError):
            project_sp500_savings(1000, 1000, 10, bad_pct)

    def test_rejects_non_positive_years(self):
        with pytest.raises(ValueError):
            project_sp500_savings(1000, 1000, 0, 50)

    def test_rejects_negative_inputs(self):
        with pytest.raises(ValueError):
            project_sp500_savings(-1, 1000, 10, 50)


class TestShiftColor:
    def test_identity_factor_returns_same_color(self):
        assert shift_color((100, 100, 100), 1.0) == (100, 100, 100)

    def test_scales_down(self):
        assert shift_color((100, 100, 100), 0.5) == (50, 50, 50)

    def test_clamps_to_upper_bound(self):
        assert shift_color((200, 200, 200), 2.0) == (255, 255, 255)

    def test_clamps_to_lower_bound(self):
        assert shift_color((10, 10, 10), -1.0) == (0, 0, 0)
