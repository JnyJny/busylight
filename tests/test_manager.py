"""Tests for LightManager functionality."""

import pytest
from unittest.mock import Mock, patch

from busylight.manager import LightManager


class TestLightManagerTargetParsing:
    """Test the parse_target_lights static method."""
    
    def test_parse_target_lights_none_returns_first_light(self):
        """None targets should return [0] for first light."""
        result = LightManager.parse_target_lights(None)
        assert result == [0]
    
    def test_parse_target_lights_empty_string_returns_empty(self):
        """Empty string should return empty list for all lights."""
        result = LightManager.parse_target_lights("")
        assert result == []
    
    def test_parse_target_lights_single_number(self):
        """Single number should return list with that number."""
        result = LightManager.parse_target_lights("5")
        assert result == [5]
    
    def test_parse_target_lights_comma_separated(self):
        """Comma-separated numbers should return list of numbers."""
        result = LightManager.parse_target_lights("1,3,5")
        assert result == [1, 3, 5]
    
    def test_parse_target_lights_range_with_dash(self):
        """Range with dash should expand to list."""
        result = LightManager.parse_target_lights("2-5")
        assert result == [2, 3, 4, 5]
    
    def test_parse_target_lights_range_with_colon(self):
        """Range with colon should expand to list."""
        result = LightManager.parse_target_lights("1:3")
        assert result == [1, 2, 3]
    
    def test_parse_target_lights_mixed_format(self):
        """Mixed comma and range format should work."""
        result = LightManager.parse_target_lights("1,3-5,7")
        assert result == [1, 3, 4, 5, 7]
    
    def test_parse_target_lights_deduplicates(self):
        """Should remove duplicates from result."""
        result = LightManager.parse_target_lights("1,2,1,3,2")
        assert sorted(result) == [1, 2, 3]


class TestLightManagerInitialization:
    """Test LightManager initialization."""
    
    def test_init_with_default_lightclass(self):
        """Should use Light as default lightclass."""
        from busylight_core import Light
        manager = LightManager()
        assert manager.lightclass == Light
    
    def test_init_with_custom_lightclass(self):
        """Should accept custom lightclass."""
        custom_class = type('CustomLight', (), {})
        manager = LightManager(lightclass=custom_class)
        assert manager.lightclass == custom_class
    
    def test_init_with_invalid_lightclass_raises_error(self):
        """Should raise ValueError for non-class lightclass."""
        with pytest.raises(ValueError, match="lightclass must be a Light subclass"):
            LightManager(lightclass="not_a_class")
    
    def test_repr(self):
        """Should have readable representation."""
        manager = LightManager()
        repr_str = repr(manager)
        assert "LightManager" in repr_str
        assert "lightclass=" in repr_str


class TestLightManagerLightAccess:
    """Test light access and management."""
    
    @patch('busylight.manager.Light')
    def test_lights_property_calls_all_lights(self, mock_light):
        """Should call lightclass.all_lights() when accessing lights."""
        mock_light.all_lights.return_value = [Mock(), Mock()]
        manager = LightManager()
        
        lights = manager.lights
        mock_light.all_lights.assert_called_once_with(reset=False)
        assert len(lights) == 2
    
    @patch('busylight.manager.Light')
    def test_lights_property_caches_result(self, mock_light):
        """Should cache lights list after first call."""
        mock_lights = [Mock(), Mock()]
        mock_light.all_lights.return_value = mock_lights
        manager = LightManager()
        
        # First call
        lights1 = manager.lights
        # Second call
        lights2 = manager.lights
        
        # Should only call all_lights once
        mock_light.all_lights.assert_called_once()
        assert lights1 is lights2
    
    @patch('busylight.manager.Light')  
    def test_selected_lights_with_empty_indices(self, mock_light):
        """Empty indices should return all lights."""
        mock_lights = [Mock(), Mock()]
        mock_light.all_lights.return_value = mock_lights
        manager = LightManager()
        
        result = manager.selected_lights([])
        assert result == mock_lights
        
        result = manager.selected_lights(None)
        assert result == mock_lights
    
    @patch('busylight.manager.Light')
    def test_selected_lights_with_valid_indices(self, mock_light):
        """Should return lights at specified indices."""
        mock_lights = [Mock(), Mock(), Mock()]
        mock_light.all_lights.return_value = mock_lights
        manager = LightManager()
        
        result = manager.selected_lights([0, 2])
        assert result == [mock_lights[0], mock_lights[2]]
    
    @patch('busylight.manager.Light')
    def test_selected_lights_with_invalid_index_raises_error(self, mock_light):
        """Invalid indices should raise NoLightsFoundError."""
        from busylight_core import NoLightsFoundError
        mock_lights = [Mock()]
        mock_light.all_lights.return_value = mock_lights
        manager = LightManager()
        
        with pytest.raises(NoLightsFoundError):
            manager.selected_lights([5])
    
    def test_len_returns_lights_count(self):
        """__len__ should return number of lights."""
        with patch.object(LightManager, 'lights', new=[Mock(), Mock(), Mock()]):
            manager = LightManager()
            assert len(manager) == 3
    
    def test_str_representation(self):
        """__str__ should return formatted light list."""
        mock_lights = [Mock(), Mock()]
        mock_lights[0].name = "Light 1"
        mock_lights[1].name = "Light 2"
        
        with patch.object(LightManager, 'lights', new=mock_lights):
            manager = LightManager()
            str_result = str(manager)
            assert "Light 1" in str_result
            assert "Light 2" in str_result
            assert "0" in str_result  # indices
            assert "1" in str_result
