# CLI Examples

Practical examples for common use cases and automation scenarios.

## Basic Light Control

### Simple On/Off

```bash
# Turn light on (green by default)
busylight on

# Turn light red
busylight on red

# Turn light off
busylight off

# Turn all connected lights on
busylight --all on blue
```

### Color Variations

```bash
# Named colors
busylight on red
busylight on green  
busylight on blue
busylight on yellow
busylight on purple
busylight on white

# Hex colors
busylight on "#ff0000"    # Red
busylight on "#00ff00"    # Green
busylight on "#0000ff"    # Blue
busylight on "0xffff00"   # Yellow

# Brightness control
busylight --dim 0.5 on red     # 50% brightness
busylight --dim 0.1 on blue    # 10% brightness
```

## Multi-LED Device Control

For devices with multiple LEDs (like Blink1 mk2), you can target specific LEDs:

### LED Targeting Basics

```bash
# Control all LEDs (default)
busylight on red

# Target specific LEDs
busylight on red --led 1      # First/top LED only
busylight on blue --led 2     # Second/bottom LED only

# Different colors on different LEDs
busylight on red --led 1      # Top LED red
busylight on blue --led 2     # Bottom LED blue
```

### Multi-LED Effects

```bash
# Different effects on different LEDs
busylight blink green --led 1 --count 3    # Top LED blinks
busylight pulse orange --led 2             # Bottom LED pulses

# Rainbow on specific LED
busylight rainbow --led 1 --speed fast     # Top LED rainbow

# LED-specific patterns
busylight fli red blue --led 1 --count 5   # Flash top LED
busylight pulse red --led 2 --speed slow   # Pulse bottom LED
```

### Sequential LED Programming

```bash
# Turn on LEDs one by one
busylight on red --led 1
sleep 1
busylight on blue --led 2

# Background effects
busylight rainbow --led 1 &    # Top LED rainbow in background
busylight pulse red --led 2    # Bottom LED pulse in foreground
```

## Effects and Animation

### Blinking Patterns

```bash
# Basic blinking
busylight blink                      # Red, slow, infinite
busylight blink blue                 # Blue, slow, infinite

# Controlled blinking
busylight blink red --count 5        # 5 red blinks
busylight blink green --speed fast   # Fast green blinks

# Alert patterns
busylight blink red --count 3 --speed fast    # Urgent alert
busylight blink yellow --count 10 --speed slow # Slow warning
```

### Advanced Effects

```bash
# Rainbow cycling
busylight rainbow                    # Default speed
busylight rainbow --speed fast       # Fast rainbow

# Pulsing effect
busylight pulse blue                 # Blue pulse
busylight pulse red --count 5        # 5 red pulses

# Flash Lights Impressively
busylight fli                        # Red/blue alternating
busylight fli --color1 green --color2 yellow --count 10
```

## Multi-LED Device Control

For devices with multiple LEDs (Blink1 mk2, BlinkStick variants):

### Individual LED Control

```bash
# Control all LEDs (default behavior)
busylight on red

# Control top LED only
busylight on red --led 1

# Control bottom LED only  
busylight on blue --led 2

# Different colors on different LEDs
busylight on red --led 1    # Top LED red
busylight on blue --led 2   # Bottom LED blue
```

### LED-Specific Effects

```bash
# Blink top LED only
busylight blink green --led 1 --count 5

# Pulse bottom LED
busylight pulse yellow --led 2 --count 3

# Create alternating pattern
busylight blink red --led 1 &      # Background process
sleep 0.5                          # Offset timing
busylight blink blue --led 2 &     # Background process
wait                               # Wait for completion
```

## Status Indication

### Meeting Status

```bash
#!/bin/bash
# meeting-status.sh

case "$1" in
    available)
        busylight on green
        echo "Status: Available"
        ;;
    busy)
        busylight on yellow
        echo "Status: Busy"
        ;;
    meeting)
        busylight on red
        echo "Status: In Meeting"
        ;;
    dnd)
        busylight blink red --count 3
        echo "Status: Do Not Disturb"
        ;;
    offline)
        busylight off
        echo "Status: Offline"
        ;;
    *)
        echo "Usage: $0 {available|busy|meeting|dnd|offline}"
        exit 1
        ;;
esac
```

### System Monitoring

```bash
#!/bin/bash
# system-monitor.sh

# CPU usage indicator
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

if (( $(echo "$cpu_usage > 80" | bc -l) )); then
    busylight on red         # High CPU
elif (( $(echo "$cpu_usage > 50" | bc -l) )); then
    busylight on yellow      # Medium CPU
else
    busylight on green       # Low CPU
fi

echo "CPU Usage: ${cpu_usage}%"
```

## Build and CI Integration

### Git Hook Example

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running tests..."
busylight blink yellow &  # Show testing in progress
TEST_PID=$!

if npm test; then
    kill $TEST_PID 2>/dev/null
    busylight on green --count 1
    echo "Tests passed!"
else
    kill $TEST_PID 2>/dev/null  
    busylight blink red --count 5
    echo "Tests failed!"
    exit 1
fi
```

### CI Status Notifications

```bash
#!/bin/bash
# ci-notify.sh - Call from CI/CD pipeline

case "$1" in
    start)
        busylight blink blue
        ;;
    success)
        busylight on green
        sleep 2
        busylight off
        ;;
    failure)
        busylight blink red --count 10
        busylight off
        ;;
    *)
        echo "Usage: $0 {start|success|failure}"
        exit 1
        ;;
esac
```

## Automation and Scripting

### Time-Based Status

```bash
#!/bin/bash
# work-hours.sh - Run via cron

hour=$(date +%H)

if [[ $hour -ge 9 && $hour -lt 17 ]]; then
    # Work hours (9 AM - 5 PM)
    busylight on green
elif [[ $hour -ge 17 && $hour -lt 19 ]]; then
    # Extended hours (5 PM - 7 PM)
    busylight on yellow
else
    # Off hours
    busylight off
fi
```

### Calendar Integration

```bash
#!/bin/bash
# calendar-status.sh

# Check for upcoming meetings (example with calendar command)
upcoming=$(calendar -t $(date +"%Y-%m-%d") | head -n 1)

if [[ -n "$upcoming" ]]; then
    # Meeting coming up
    busylight pulse yellow --count 3
    echo "Upcoming: $upcoming"
else
    # No immediate meetings
    busylight on green
    echo "No upcoming meetings"
fi
```

### Device Testing

```bash
#!/bin/bash
# device-test.sh - Test all connected lights

echo "Testing connected devices..."
busylight list

echo "Running color test sequence..."
for color in red green blue yellow purple white; do
    echo "Testing $color..."
    busylight --all on $color
    sleep 1
done

echo "Testing effects..."
busylight --all blink red --count 3
sleep 2
busylight --all rainbow &
RAINBOW_PID=$!
sleep 5
kill $RAINBOW_PID

echo "Test complete"
busylight --all off
```

## Advanced Usage

### Multiple Device Management

```bash
#!/bin/bash
# multi-device.sh

# List devices and get indices
busylight list

# Set different colors on different devices
busylight --lights 0 on red       # First device red
busylight --lights 1 on green     # Second device green  
busylight --lights 2 on blue      # Third device blue

# Create coordinated effect
busylight --lights 0,2 blink red --count 5 &    # Devices 0,2
busylight --lights 1 pulse green --count 5 &     # Device 1
wait  # Wait for all effects to complete
```

### Error Handling

```bash
#!/bin/bash
# robust-control.sh

set -e  # Exit on error

# Function to safely control light
control_light() {
    local color="$1"
    local retries=3
    
    for ((i=1; i<=retries; i++)); do
        if busylight on "$color" 2>/dev/null; then
            echo "Light set to $color"
            return 0
        else
            echo "Attempt $i failed, retrying..." >&2
            sleep 1
        fi
    done
    
    echo "Failed to control light after $retries attempts" >&2
    return 1
}

# Usage
control_light "green" || echo "Light control failed, continuing..."
```

These examples demonstrate the flexibility and power of the `busylight` CLI
for various automation and notification scenarios.