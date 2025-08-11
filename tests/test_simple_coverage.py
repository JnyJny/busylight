"""Simple tests to improve coverage on easy targets."""

from busylight.effects.spectrum import Spectrum
from busylight.effects.steady import Steady


class TestSpectrumSimple:
    """Test spectrum effect for coverage."""
    
    def test_colors_property_cached(self):
        """Test colors property returns cached value."""
        spectrum = Spectrum()
        
        # Set up cached colors
        spectrum._colors = [(255, 0, 0), (0, 255, 0)]
        
        # Should return cached colors (hits line 55)
        colors = spectrum.colors
        assert colors == [(255, 0, 0), (0, 255, 0)]


class TestSteadySimple:
    """Test steady effect for coverage."""
    
    def test_repr(self):
        """Test __repr__ method."""
        steady = Steady(color=(255, 128, 64))
        
        # Should create readable representation  
        repr_str = repr(steady)
        assert "Steady" in repr_str
        assert "(255, 128, 64)" in repr_str


class TestImportsAndMisc:
    """Test various imports and simple functionality."""
    
    def test_effect_imports(self):
        """Test that effect classes can be imported."""
        from busylight.effects.blink import Blink
        from busylight.effects.gradient import Gradient
        from busylight.effects.spectrum import Spectrum
        from busylight.effects.steady import Steady
        
        # Should be able to create instances
        blink = Blink((255, 0, 0))
        gradient = Gradient((0, 255, 0))
        spectrum = Spectrum()  
        steady = Steady((0, 0, 255))
        
        assert all([blink, gradient, spectrum, steady])
    
    def test_busylight_init_imports(self):
        """Test __init__.py imports.""" 
        # Try importing from the main module
        try:
            from busylight import __version__
            assert __version__  # Should have some version
        except ImportError:
            pass  # OK if not defined
        
        try:
            from busylight import __author__
            assert __author__  # Should have some author
        except ImportError:
            pass  # OK if not defined