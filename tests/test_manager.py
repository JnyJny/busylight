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
    
    def _make_sortable_mock_lights(self, count):
        """Create mock lights that can be sorted."""
        lights = []
        for i in range(count):
            # Create a simple sortable object
            class SortableMock:
                def __init__(self, sort_key):
                    self.sort_key = sort_key
                def __lt__(self, other):
                    return self.sort_key < other.sort_key
                def __eq__(self, other):
                    return self.sort_key == other.sort_key
                    
            light = SortableMock(i)
            lights.append(light)
        return lights
    
    def test_lights_property_calls_all_lights(self):
        """Should call lightclass.all_lights() when accessing lights."""
        mock_lights = self._make_sortable_mock_lights(2)
        
        # Create a mock class that can pass isinstance(value, type) check
        mock_light_class = type('MockLightClass', (), {})
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        lights = manager.lights
        mock_light_class.all_lights.assert_called_once_with(reset=False)
        assert len(lights) == 2
    
    def test_lights_property_caches_result(self):
        """Should cache lights list after first call."""
        mock_lights = self._make_sortable_mock_lights(2)
        mock_light_class = type('MockLightClass', (), {})
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        # First call
        lights1 = manager.lights
        # Second call  
        lights2 = manager.lights
        
        # Should only call all_lights once
        mock_light_class.all_lights.assert_called_once()
        assert lights1 is lights2
    
    def test_selected_lights_with_empty_indices(self):
        """Empty indices should return all lights."""
        mock_lights = self._make_sortable_mock_lights(2)
        mock_light_class = type('MockLightClass', (), {})
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        result = manager.selected_lights([])
        assert len(result) == 2
        
        result = manager.selected_lights(None)
        assert len(result) == 2
    
    def test_selected_lights_with_valid_indices(self):
        """Should return lights at specified indices."""
        mock_lights = self._make_sortable_mock_lights(3)
        mock_light_class = type('MockLightClass', (), {})
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        result = manager.selected_lights([0, 2])
        assert len(result) == 2
    
    def test_selected_lights_with_invalid_index_raises_error(self):
        """Invalid indices should raise NoLightsFoundError."""
        from busylight_core import NoLightsFoundError
        mock_lights = self._make_sortable_mock_lights(1)
        mock_light_class = type('MockLightClass', (), {})
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
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


class TestLightManagerMethods:
    """Test additional LightManager methods for coverage."""
    
    def test_update_greedy_true(self):
        """Should update lights with greedy=True."""
        mock_light_class = type('MockLightClass', (), {})
        mock_existing_lights = self._make_sortable_mock_lights(2)
        mock_new_lights = self._make_sortable_mock_lights(1) 
        mock_light_class.all_lights = Mock(side_effect=[mock_existing_lights, mock_new_lights])
        
        manager = LightManager(lightclass=mock_light_class)
        
        # Set up existing lights with plugged/unplugged status
        mock_existing_lights[0].is_pluggedin = True
        mock_existing_lights[0].is_unplugged = False
        mock_existing_lights[1].is_pluggedin = False  
        mock_existing_lights[1].is_unplugged = True
        
        # Initialize lights first
        _ = manager.lights
        
        # Now call update
        new_count, active_count, inactive_count = manager.update(greedy=True)
        
        assert new_count == 1  # Added 1 new light
        assert active_count == 1  # 1 plugged in light
        assert inactive_count == 1  # 1 unplugged light
        
        # Should have called all_lights again for new lights
        assert mock_light_class.all_lights.call_count == 2
    
    def test_update_greedy_false(self):
        """Should update lights with greedy=False.""" 
        mock_light_class = type('MockLightClass', (), {})
        mock_existing_lights = self._make_sortable_mock_lights(1)
        mock_light_class.all_lights = Mock(return_value=mock_existing_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        # Set up existing lights with plugged status
        mock_existing_lights[0].is_pluggedin = True
        mock_existing_lights[0].is_unplugged = False
        
        # Initialize lights first
        _ = manager.lights
        
        # Now call update with greedy=False
        new_count, active_count, inactive_count = manager.update(greedy=False)
        
        assert new_count == 0  # No new lights added
        assert active_count == 1  # 1 active light
        assert inactive_count == 0  # 0 inactive lights
        
        # Should only call all_lights once (during initialization)
        assert mock_light_class.all_lights.call_count == 1
    
    def test_release_with_lights(self):
        """Should release managed lights."""
        mock_light_class = type('MockLightClass', (), {})
        mock_lights = self._make_sortable_mock_lights(2)
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        # Initialize lights
        _ = manager.lights
        assert len(manager.lights) == 2
        
        # Release lights
        manager.release()
        
        # Should clear lights list
        assert len(manager._lights) == 0
    
    def test_release_empty_lights(self):
        """Should handle release when no lights."""
        manager = LightManager()
        
        # Should not raise error
        manager.release()
    
    def test_on_method_success(self):
        """Should turn on lights successfully."""
        mock_light_class = type('MockLightClass', (), {})
        mock_lights = self._make_sortable_mock_lights(2)
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        # Mock the selected_lights and lights to have on() method
        for light in mock_lights:
            light.on = Mock()
        
        # Call on method
        manager.on(color=(255, 0, 0), light_ids=[0, 1])
        
        # Should call on() for each light
        for light in mock_lights:
            light.on.assert_called_once_with((255, 0, 0))
    
    def test_on_method_with_timeout(self):
        """Should handle timeout in on method."""
        mock_light_class = type('MockLightClass', (), {}) 
        mock_lights = self._make_sortable_mock_lights(1)
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        # Mock light on method
        mock_lights[0].on = Mock()
        
        # Call on method with timeout
        manager.on(color=(0, 255, 0), light_ids=[0], timeout=5.0)
        
        # Should still call on method
        mock_lights[0].on.assert_called_once_with((0, 255, 0))
    
    def test_off_method(self):
        """Should turn off lights."""
        mock_light_class = type('MockLightClass', (), {})
        mock_lights = self._make_sortable_mock_lights(1)
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        manager = LightManager(lightclass=mock_light_class)
        
        # Mock light off method
        mock_lights[0].off = Mock()
        
        # Call off method
        manager.off(lights=[0])
        
        # Should call off() for the light
        mock_lights[0].off.assert_called_once()
    
    @patch('busylight.manager.asyncio')
    def test_apply_effect_success(self, mock_asyncio):
        """Should apply effect to lights."""
        mock_light_class = type('MockLightClass', (), {})
        mock_lights = self._make_sortable_mock_lights(1)  
        mock_light_class.all_lights = Mock(return_value=mock_lights)
        
        # Create manager
        manager = LightManager(lightclass=mock_light_class)
        
        # Create mock effect
        mock_effect = Mock()
        mock_effect.default_interval = 0.5
        
        # Call apply_effect
        manager.apply_effect(mock_effect, light_ids=[0])
        
        # Should call asyncio.run
        mock_asyncio.run.assert_called_once()
    
    def _make_sortable_mock_lights(self, count):
        """Create mock lights that can be sorted."""
        lights = []
        for i in range(count):
            # Create a simple sortable object
            class SortableMock:
                def __init__(self, sort_key):
                    self.sort_key = sort_key
                def __lt__(self, other):
                    return self.sort_key < other.sort_key
                def __eq__(self, other):
                    return self.sort_key == other.sort_key
                    
            light = SortableMock(i)
            lights.append(light)
        return lights
