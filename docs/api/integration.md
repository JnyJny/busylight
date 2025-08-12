# API Integration Guide

Learn how to integrate the BusyLight Web API into your applications and
services.

## Server Setup

### Basic Server Configuration

```python
# server_config.py
import subprocess
import os

def start_busylight_server():
    """Start BusyLight API server with custom configuration."""
    env = os.environ.copy()
    
    # Optional: Set authentication
    env['BUSYLIGHT_API_USER'] = 'api_user'
    env['BUSYLIGHT_API_PASS'] = 'secure_password'
    
    # Optional: Enable CORS for web apps
    env['BUSYLIGHT_API_CORS_ORIGINS_LIST'] = '["http://localhost:3000"]'
    
    # Start server
    subprocess.Popen([
        'busyserve', 
        '--host', '0.0.0.0',
        '--port', '8000'
    ], env=env)
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libusb-1.0-0-dev \
    libudev-dev \
    && rm -rf /var/lib/apt/lists/*

# Install BusyLight
RUN pip install busylight-for-humans[webapi]

# Configure environment
ENV BUSYLIGHT_API_USER=admin
ENV BUSYLIGHT_API_PASS=changeme
ENV BUSYLIGHT_API_CORS_ORIGINS_LIST='["*"]'

# Expose port
EXPOSE 8000

# Add udev rules and start server
COPY 99-busylights.rules /etc/udev/rules.d/
CMD ["busyserve", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  busylight:
    build: .
    ports:
      - "8000:8000"
    devices:
      - /dev/bus/usb:/dev/bus/usb
    privileged: true
    environment:
      - BUSYLIGHT_API_USER=admin
      - BUSYLIGHT_API_PASS=secure_password
```

## Client Libraries

### Python Client

```python
import requests
import json
from typing import Optional, Dict, Any

class BusyLightClient:
    """Python client for BusyLight API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 auth: Optional[tuple] = None):
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.session = requests.Session()
        if auth:
            self.session.auth = auth
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[Any, Any]:
        """Make API request and return JSON response."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params or {})
        response.raise_for_status()
        return response.json()
    
    def list_lights(self) -> Dict[str, Any]:
        """Get status of all lights."""
        return self._request("/lights/status")
    
    def get_light(self, light_id: int) -> Dict[str, Any]:
        """Get status of specific light."""
        return self._request(f"/light/{light_id}/status")
    
    def turn_on(self, light_id: int, color: str = "green", 
                led: int = 0, dim: float = 1.0) -> Dict[str, Any]:
        """Turn on specific light."""
        params = {"color": color, "led": led, "dim": dim}
        return self._request(f"/light/{light_id}/on", params)
    
    def turn_on_all(self, color: str = "green", 
                    led: int = 0, dim: float = 1.0) -> Dict[str, Any]:
        """Turn on all lights."""
        params = {"color": color, "led": led, "dim": dim}
        return self._request("/lights/on", params)
    
    def turn_off(self, light_id: int) -> Dict[str, Any]:
        """Turn off specific light."""
        return self._request(f"/light/{light_id}/off")
    
    def turn_off_all(self) -> Dict[str, Any]:
        """Turn off all lights."""
        return self._request("/lights/off")
    
    def blink(self, light_id: int, color: str = "red", count: int = 0,
              speed: str = "slow", led: int = 0) -> Dict[str, Any]:
        """Start blinking effect."""
        params = {
            "color": color, "count": count, 
            "speed": speed, "led": led
        }
        return self._request(f"/light/{light_id}/blink", params)
    
    def rainbow(self, light_id: int, speed: str = "slow") -> Dict[str, Any]:
        """Start rainbow effect."""
        params = {"speed": speed}
        return self._request(f"/light/{light_id}/rainbow", params)

# Usage example
client = BusyLightClient(auth=("admin", "password"))

# Turn first light red
client.turn_on(0, "red")

# Blink all lights blue
client.blink(0, "blue", count=5)

# Get device information
lights = client.list_lights()
print(f"Found {len(lights)} lights")
```

### JavaScript/Node.js Client

```javascript
// busylight-client.js
class BusyLightClient {
    constructor(baseUrl = 'http://localhost:8000', auth = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.auth = auth;
    }

    async _request(endpoint, params = {}) {
        const url = new URL(endpoint, this.baseUrl);
        Object.keys(params).forEach(key => {
            url.searchParams.append(key, params[key]);
        });

        const options = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (this.auth) {
            const credentials = btoa(`${this.auth.user}:${this.auth.pass}`);
            options.headers['Authorization'] = `Basic ${credentials}`;
        }

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        
        return response.json();
    }

    async listLights() {
        return this._request('/lights/status');
    }

    async turnOn(lightId, color = 'green', led = 0, dim = 1.0) {
        return this._request(`/light/${lightId}/on`, {
            color, led, dim
        });
    }

    async turnOnAll(color = 'green', led = 0, dim = 1.0) {
        return this._request('/lights/on', { color, led, dim });
    }

    async turnOff(lightId) {
        return this._request(`/light/${lightId}/off`);
    }

    async blink(lightId, color = 'red', count = 0, speed = 'slow', led = 0) {
        return this._request(`/light/${lightId}/blink`, {
            color, count, speed, led
        });
    }

    async rainbow(lightId, speed = 'slow') {
        return this._request(`/light/${lightId}/rainbow`, { speed });
    }
}

// Usage
const client = new BusyLightClient('http://localhost:8000', {
    user: 'admin',
    pass: 'password'
});

// Turn light red
client.turnOn(0, 'red')
    .then(result => console.log('Light turned on:', result))
    .catch(error => console.error('Error:', error));
```

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/ci.yml
name: CI Pipeline with BusyLight

on: [push, pull_request]

jobs:
  test:
    runs-on: self-hosted  # Requires self-hosted runner with BusyLight
    steps:
      - uses: actions/checkout@v4
      
      - name: Signal build start
        run: |
          curl -f "http://localhost:8000/lights/blink?color=blue" || true
      
      - name: Run tests
        run: |
          npm test
      
      - name: Signal success
        if: success()
        run: |
          curl -f "http://localhost:8000/lights/on?color=green" || true
          sleep 2
          curl -f "http://localhost:8000/lights/off" || true
      
      - name: Signal failure  
        if: failure()
        run: |
          curl -f "http://localhost:8000/lights/blink?color=red&count=10" || true
```

### Monitoring Integration

```python
# monitoring.py
import time
import psutil
from busylight_client import BusyLightClient

def monitor_system():
    """Monitor system resources and update light status."""
    client = BusyLightClient()
    
    while True:
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            # Determine status color
            if cpu_percent > 80 or memory_percent > 90:
                color = "red"    # Critical
            elif cpu_percent > 60 or memory_percent > 75:
                color = "yellow" # Warning
            else:
                color = "green"  # Normal
            
            # Update light
            client.turn_on_all(color)
            
            print(f"CPU: {cpu_percent}%, Memory: {memory_percent}%, "
                  f"Status: {color}")
            
        except Exception as e:
            print(f"Error: {e}")
            client.turn_on_all("red")  # Error state
        
        time.sleep(10)

if __name__ == "__main__":
    monitor_system()
```

### Web Dashboard

```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>BusyLight Dashboard</title>
    <style>
        .light-control { margin: 10px 0; }
        button { margin: 5px; padding: 10px; }
        .status { font-family: monospace; }
    </style>
</head>
<body>
    <h1>BusyLight Control Dashboard</h1>
    
    <div class="light-control">
        <h3>Quick Controls</h3>
        <button onclick="setStatus('available')">Available</button>
        <button onclick="setStatus('busy')">Busy</button>
        <button onclick="setStatus('meeting')">In Meeting</button>
        <button onclick="setStatus('offline')">Offline</button>
    </div>
    
    <div class="light-control">
        <h3>Effects</h3>
        <button onclick="startEffect('rainbow')">Rainbow</button>
        <button onclick="startEffect('blink')">Blink</button>
        <button onclick="startEffect('pulse')">Pulse</button>
    </div>
    
    <div class="status" id="status"></div>

    <script>
        const API_BASE = 'http://localhost:8000';
        
        async function apiCall(endpoint, params = {}) {
            const url = new URL(endpoint, API_BASE);
            Object.keys(params).forEach(key => {
                url.searchParams.append(key, params[key]);
            });
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                document.getElementById('status').innerText = 
                    JSON.stringify(data, null, 2);
                return data;
            } catch (error) {
                document.getElementById('status').innerText = 
                    `Error: ${error.message}`;
            }
        }
        
        function setStatus(status) {
            const colors = {
                'available': 'green',
                'busy': 'yellow', 
                'meeting': 'red',
                'offline': 'black'
            };
            
            if (status === 'offline') {
                apiCall('/lights/off');
            } else {
                apiCall('/lights/on', { color: colors[status] });
            }
        }
        
        function startEffect(effect) {
            if (effect === 'rainbow') {
                apiCall('/lights/rainbow');
            } else if (effect === 'blink') {
                apiCall('/lights/blink', { color: 'red', count: 5 });
            } else if (effect === 'pulse') {
                apiCall('/lights/pulse', { color: 'blue', count: 3 });
            }
        }
        
        // Load initial status
        apiCall('/lights/status');
    </script>
</body>
</html>
```

### Slack Bot Integration

```python
# slack_bot.py
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from busylight_client import BusyLightClient
import os

class BusyLightSlackBot:
    def __init__(self):
        self.slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        self.socket_client = SocketModeClient(
            app_token=os.environ["SLACK_APP_TOKEN"],
            web_client=self.slack_client
        )
        self.light_client = BusyLightClient()
        
        # Register command handler
        self.socket_client.socket_mode_request_listeners.append(
            self.handle_commands
        )
    
    def handle_commands(self, client: SocketModeClient, req: SocketModeRequest):
        if req.type == "slash_commands":
            command = req.payload["command"]
            text = req.payload["text"]
            
            if command == "/busylight":
                response_text = self.process_light_command(text)
                
                # Send response
                response = SocketModeResponse(envelope_id=req.envelope_id)
                client.send_socket_mode_response(response)
                
                # Send message to channel
                client.web_client.chat_postMessage(
                    channel=req.payload["channel_id"],
                    text=response_text
                )
    
    def process_light_command(self, command_text: str) -> str:
        """Process light control commands."""
        try:
            parts = command_text.split()
            if not parts:
                return "Usage: /busylight <on|off|blink> [color]"
            
            action = parts[0].lower()
            color = parts[1] if len(parts) > 1 else "green"
            
            if action == "on":
                self.light_client.turn_on_all(color)
                return f"✅ Lights turned on ({color})"
            elif action == "off":
                self.light_client.turn_off_all()
                return "✅ Lights turned off"
            elif action == "blink":
                self.light_client.blink(0, color, count=3)
                return f"✅ Lights blinking ({color})"
            else:
                return "❌ Unknown command. Use: on, off, or blink"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def start(self):
        self.socket_client.connect()

if __name__ == "__main__":
    bot = BusyLightSlackBot()
    bot.start()
```

## Error Handling Best Practices

```python
import requests
import time
from typing import Optional

class RobustBusyLightClient:
    def __init__(self, base_url: str, max_retries: int = 3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.session = requests.Session()
    
    def _safe_request(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        """Make API request with retry logic and error handling."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=5)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.ConnectionError:
                print(f"Connection failed (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error: {e}")
                break  # Don't retry HTTP errors
                
            except requests.exceptions.Timeout:
                print(f"Request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    continue
                    
        return None
    
    def safe_turn_on(self, light_id: int, color: str) -> bool:
        """Safely turn on light with error handling."""
        result = self._safe_request(f"/light/{light_id}/on", {"color": color})
        return result is not None
```

These examples demonstrate how to integrate the BusyLight API into various
applications and services, with proper error handling and authentication.