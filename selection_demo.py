#!/usr/bin/env python3
"""
Demo script showing all light selection methods in action.
Run this to see how different selection methods work with real lights.
"""

import time
from src.busylight.controller import LightController


def demo_light_discovery():
    """Show what lights are available and their names."""
    print("🔍 Light Discovery")
    print("=" * 50)
    
    with LightController() as controller:
        print(f"Total lights detected: {len(controller)}")
        
        if controller:
            print("\nAvailable lights:")
            for i, name in enumerate(controller.list_lights()):
                print(f"  {i}: {name}")
        else:
            print("No lights found - connect some USB lights to see the demo!")
            return False
    
    print()
    return True


def demo_select_all():
    """Demonstrate selecting all lights."""
    print("🌟 Select All Lights")
    print("=" * 50)
    
    with LightController() as controller:
        selection = controller.all()
        print(f"Selected {len(selection)} lights: {selection.names()}")
        
        if selection:
            print("Turning all lights GREEN for 2 seconds...")
            selection.turn_on("green")
            time.sleep(2)
            selection.turn_off()
    
    print()


def demo_select_by_index():
    """Demonstrate selecting lights by index."""
    print("🎯 Select by Index")
    print("=" * 50)
    
    with LightController() as controller:
        # First light only
        selection = controller.by_index(0)
        print(f"First light: {selection.names()}")
        
        if selection:
            print("Blinking first light BLUE 3 times...")
            selection.blink("blue", count=3, speed="fast")
            time.sleep(2)
        
        # Multiple specific indices
        if len(controller) >= 3:
            selection = controller.by_index(0, 2)
            print(f"Lights 0 and 2: {selection.names()}")
            
            print("Turning lights 0 and 2 RED...")
            selection.turn_on("red")
            time.sleep(1)
            selection.turn_off()
    
    print()


def demo_select_by_name():
    """Demonstrate selecting lights by exact name."""
    print("📛 Select by Name")  
    print("=" * 50)
    
    with LightController() as controller:
        available_names = controller.list_lights()
        
        if available_names:
            # Select first available light by name
            first_name = available_names[0]
            selection = controller.by_name(first_name)
            print(f"Selected '{first_name}': {len(selection)} light(s)")
            
            if selection:
                print(f"Turning '{first_name}' YELLOW...")
                selection.turn_on("yellow")
                time.sleep(1)
                selection.turn_off()
        
        # Try to select multiple by name (if available)
        if len(available_names) >= 2:
            selection = controller.by_name(available_names[0], available_names[1])
            print(f"Selected multiple by name: {selection.names()}")
            
            if selection:
                print("Blinking selected lights PURPLE...")
                selection.blink("purple", count=2)
                time.sleep(2)
    
    print()


def demo_select_by_pattern():
    """Demonstrate selecting lights using regex patterns."""
    print("🔍 Select by Pattern")
    print("=" * 50)
    
    with LightController() as controller:
        available_names = controller.list_lights()
        print(f"Available lights: {available_names}")
        
        # Try common patterns
        patterns_to_try = [
            ("Blyn.*", "Blynclight devices"),
            (".*Light.*", "Lights with 'Light' in name"),
            (".*USB.*", "USB devices"),
            ("Mute.*", "MuteMe devices"),
            (r".*\(\d+\)", "Devices with numbers in parentheses"),
        ]
        
        for pattern, description in patterns_to_try:
            selection = controller.by_pattern(pattern)
            if selection:
                print(f"Pattern '{pattern}' ({description}): {selection.names()}")
                
                print(f"  Blinking matched lights CYAN...")
                selection.blink("cyan", count=2, speed="medium")
                time.sleep(1.5)
            else:
                print(f"Pattern '{pattern}' ({description}): No matches")
    
    print()


def demo_practical_scenarios():
    """Show practical real-world usage scenarios."""
    print("💡 Practical Usage Scenarios")
    print("=" * 50)
    
    with LightController() as controller:
        print("Scenario 1: Status Light System")
        
        # Use first light as status indicator
        status_light = controller.first()
        if status_light:
            print("  System OK (GREEN)")
            status_light.turn_on("green")
            time.sleep(1)
            
            print("  Warning (YELLOW blink)")
            status_light.blink("yellow", count=3)
            time.sleep(2)
            
            print("  Error (RED blink)")
            status_light.blink("red", count=5)
            time.sleep(3)
            
            status_light.turn_off()
        
        print("\nScenario 2: Work Lighting Control")
        
        # Turn on work lights (any lights available)
        work_lights = controller.all()
        if work_lights:
            print("  Setting work lighting (soft white)")
            work_lights.turn_on("white")
            time.sleep(1)
            
            print("  Focus mode (bright blue)")
            work_lights.turn_on("blue")
            time.sleep(1)
            
            print("  Break time (off)")
            work_lights.turn_off()
        
        print("\nScenario 3: Meeting Status")
        
        # Use pattern to control webcam-related lights
        meeting_lights = controller.by_pattern(".*") # All lights for demo
        if meeting_lights:
            print("  Meeting started (steady red)")
            meeting_lights.turn_on("red")
            time.sleep(1)
            
            print("  Do not disturb (blinking red)")
            meeting_lights.blink("red", count=3)
            time.sleep(2)
            
            print("  Meeting ended (brief green)")
            meeting_lights.turn_on("green")
            time.sleep(1)
            meeting_lights.turn_off()
    
    print()


def demo_error_handling():
    """Show how selection methods handle errors gracefully."""
    print("⚠️  Error Handling")
    print("=" * 50)
    
    with LightController() as controller:
        # These won't crash - they'll log warnings and return empty selections
        
        print("Trying invalid index (999)...")
        invalid_selection = controller.by_index(999)
        print(f"  Result: {len(invalid_selection)} lights selected")
        invalid_selection.turn_on("red")  # No-op, no error
        
        print("Trying non-existent name...")
        missing_selection = controller.by_name("NonExistentLight")
        print(f"  Result: {len(missing_selection)} lights selected")
        missing_selection.blink("blue")  # No-op, no error
        
        print("Trying pattern with no matches...")
        empty_selection = controller.by_pattern("ZZZZZ_NO_MATCH")
        print(f"  Result: {len(empty_selection)} lights selected")
        empty_selection.turn_off()  # No-op, no error
        
        print("All operations completed without errors!")
    
    print()


def main():
    """Run all demos."""
    print("🚀 LightController Selection Methods Demo")
    print("=" * 60)
    print("This demo shows all the ways to select specific lights.")
    print("Connect some USB lights to see the full effect!\n")
    
    # Check if lights are available
    has_lights = demo_light_discovery()
    
    if not has_lights:
        print("Demo requires USB lights to be connected.")
        print("The selection methods will work, but you won't see any visual effects.")
        print()
    
    # Run all demos
    demo_select_all()
    demo_select_by_index()
    demo_select_by_name()
    demo_select_by_pattern()
    demo_practical_scenarios()
    demo_error_handling()
    
    print("✅ Demo complete! The new LightController provides flexible,")
    print("   intuitive ways to select exactly the lights you want to control.")


if __name__ == "__main__":
    main()