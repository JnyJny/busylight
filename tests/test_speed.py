"""Tests for Speed enum functionality."""

import pytest
from busylight.speed import Speed


class TestSpeed:
    """Test Speed enum values and functionality."""

    def test_speed_enum_values(self):
        """Should have correct speed enum string values."""
        assert Speed.Slow.value == "slow"
        assert Speed.Medium.value == "medium"
        assert Speed.Fast.value == "fast"

    def test_speed_duty_cycle_property(self):
        """Should return duty_cycle as the enum value."""
        assert Speed.Slow.duty_cycle == 0.75
        assert Speed.Medium.duty_cycle == 0.5
        assert Speed.Fast.duty_cycle == 0.25

    def test_speed_enum_members(self):
        """Should have all expected enum members."""
        expected_members = {"Slow", "Medium", "Fast"}
        actual_members = {speed.name for speed in Speed}
        assert actual_members == expected_members

    def test_speed_enum_iteration(self):
        """Should be able to iterate over Speed enum."""
        speeds = list(Speed)
        assert len(speeds) == 3
        assert Speed.Slow in speeds
        assert Speed.Medium in speeds
        assert Speed.Fast in speeds

    def test_speed_string_representation(self):
        """Should have proper string representation."""
        assert "Slow" in str(Speed.Slow)
        assert "Medium" in str(Speed.Medium)
        assert "Fast" in str(Speed.Fast)

    def test_speed_comparison(self):
        """Should be able to compare Speed values."""
        assert Speed.Slow.value == "slow"
        assert Speed.Medium.value == "medium"
        assert Speed.Fast.value == "fast"

    def test_speed_enum_by_name(self):
        """Should be able to access Speed by name."""
        assert Speed["Slow"] == Speed.Slow
        assert Speed["Medium"] == Speed.Medium
        assert Speed["Fast"] == Speed.Fast

    def test_speed_enum_by_value(self):
        """Should be able to get Speed by value."""
        assert Speed("slow") == Speed.Slow
        assert Speed("medium") == Speed.Medium
        assert Speed("fast") == Speed.Fast
