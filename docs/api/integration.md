# API Integration Guide

Learn how to integrate the BusyLight Web API into your applications and
services using both the modern v1 endpoints and compatibility endpoints.

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

### Modern Python Client (V1 API)

```python
import requests
import json
from typing import Optional, Dict, Any, List

class ModernBusyLightClient:
    """Python client using the modern v1 API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 auth: Optional[tuple] = None, use_v1: bool = True):
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.use_v1 = use_v1
        self.session = requests.Session()
        if auth:
            self.session.auth = auth
    
    def _post_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request with JSON data."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(
            url, 
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    
    def _get_request(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and available endpoints."""
        return self._get_request("/")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Check system health and device availability."""
        endpoint = "/api/v1/system/health" if self.use_v1 else "/system/health"
        return self._get_request(endpoint)
    
    def list_lights(self) -> List[Dict[str, Any]]:
        """Get status of all lights."""
        endpoint = "/api/v1/lights" if self.use_v1 else "/lights"
        return self._get_request(endpoint)
    
    def get_light(self, light_id: int) -> Dict[str, Any]:
        """Get status of specific light."""
        endpoint = f"/api/v1/lights/{light_id}/status" if self.use_v1 else f"/lights/{light_id}/status"
        return self._get_request(endpoint)
    
    def turn_on(self, light_id: Optional[int] = None, color: str = "green", 
                led: int = 0, dim: float = 1.0) -> Dict[str, Any]:
        """Turn on light(s) using v1 API."""
        if not self.use_v1:
            raise ValueError("Use compatibility client for non-v1 endpoints")
            
        data = {"color": color, "led": led, "dim": dim}
        
        if light_id is not None:
            endpoint = f"/api/v1/lights/{light_id}/on"
        else:
            endpoint = "/api/v1/lights/on"
            
        return self._post_request(endpoint, data)
    
    def turn_off(self, light_id: Optional[int] = None) -> Dict[str, Any]:
        """Turn off light(s) using v1 API."""
        if not self.use_v1:
            raise ValueError("Use compatibility client for non-v1 endpoints")
            
        if light_id is not None:
            endpoint = f"/api/v1/lights/{light_id}/off"
        else:
            endpoint = "/api/v1/lights/off"
            
        return self._post_request(endpoint, {})
    
    def blink(self, light_id: Optional[int] = None, color: str = "red", 
              count: int = 0, speed: str = "slow", led: int = 0, 
              dim: float = 1.0) -> Dict[str, Any]:
        """Start blinking effect using v1 API."""
        if not self.use_v1:
            raise ValueError("Use compatibility client for non-v1 endpoints")
            
        data = {
            "color": color, "count": count, "speed": speed, 
            "led": led, "dim": dim
        }
        
        if light_id is not None:
            endpoint = f"/api/v1/lights/{light_id}/blink"
        else:
            endpoint = "/api/v1/lights/blink"
            
        return self._post_request(endpoint, data)
    
    def rainbow_effect(self, light_id: Optional[int] = None, 
                      speed: str = "slow", dim: float = 1.0, 
                      led: int = 0) -> Dict[str, Any]:
        """Start rainbow effect using v1 API."""
        if not self.use_v1:
            raise ValueError("Use compatibility client for non-v1 endpoints")
            
        data = {"speed": speed, "dim": dim, "led": led}
        
        if light_id is not None:
            endpoint = f"/api/v1/effects/{light_id}/rainbow"
        else:
            endpoint = "/api/v1/effects/rainbow"
            
        return self._post_request(endpoint, data)
    
    def pulse_effect(self, light_id: Optional[int] = None, color: str = "red",
                    speed: str = "slow", dim: float = 1.0, count: int = 0,
                    led: int = 0) -> Dict[str, Any]:
        """Start pulse effect using v1 API."""
        if not self.use_v1:
            raise ValueError("Use compatibility client for non-v1 endpoints")
            
        data = {
            "color": color, "speed": speed, "dim": dim, 
            "count": count, "led": led
        }
        
        if light_id is not None:
            endpoint = f"/api/v1/effects/{light_id}/pulse"
        else:
            endpoint = "/api/v1/effects/pulse"
            
        return self._post_request(endpoint, data)

# Usage example
client = ModernBusyLightClient(auth=("admin", "password"))

# Check system health
health = client.get_system_health()
print(f"System status: {health['status']}")

# Turn first light red using v1 API
response = client.turn_on(light_id=0, color="red", dim=0.8)
print(f"Lights affected: {response['lights_affected']}")

# Start rainbow effect on all lights
client.rainbow_effect(speed="fast", dim=0.7)
```

### Compatibility Python Client

```python
class CompatibilityBusyLightClient:
    """Python client for backwards compatibility with original API."""
    
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
    
    def turn_on(self, light_id: int, color: str = "green", 
                led: int = 0, dim: float = 1.0) -> Dict[str, Any]:
        """Turn on specific light using compatibility endpoint."""
        params = {"color": color, "led": led, "dim": dim}
        return self._request(f"/light/{light_id}/on", params)
    
    def turn_on_all(self, color: str = "green", 
                    led: int = 0, dim: float = 1.0) -> Dict[str, Any]:
        """Turn on all lights using compatibility endpoint."""
        params = {"color": color, "led": led, "dim": dim}
        return self._request("/lights/on", params)
    
    def blink(self, light_id: int, color: str = "red", count: int = 0,
              speed: str = "slow", led: int = 0) -> Dict[str, Any]:
        """Start blinking effect using compatibility endpoint."""
        params = {
            "color": color, "count": count, 
            "speed": speed, "led": led
        }
        return self._request(f"/light/{light_id}/blink", params)

# Usage with existing code - no changes needed
legacy_client = CompatibilityBusyLightClient(auth=("admin", "password"))
legacy_client.turn_on(0, "red")  # Works exactly as before
```

### JavaScript/TypeScript Client (V1 API)

```typescript
// modern-busylight-client.ts
interface LightOperationRequest {
  color?: string;
  dim?: number;
  led?: number;
  speed?: string;
  count?: number;
}

interface EffectRequest extends LightOperationRequest {
  color_a?: string;
  color_b?: string;
}

interface LightOperationResponse {
  success: boolean;
  action: string;
  lights_affected: number;
  details: Array<{
    light_id: number;
    action: string;
    color?: string;
    rgb?: [number, number, number];
    dim?: number;
    led?: number;
  }>;
}

class ModernBusyLightClient {
  private baseUrl: string;
  private auth: { user: string; pass: string } | null;

  constructor(baseUrl = 'http://localhost:8000', auth: { user: string; pass: string } | null = null) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.auth = auth;
  }

  private async postRequest(endpoint: string, data: any): Promise<any> {
    const options: RequestInit = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    };

    if (this.auth) {
      const credentials = btoa(`${this.auth.user}:${this.auth.pass}`);
      options.headers!['Authorization'] = `Basic ${credentials}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, options);
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }

  private async getRequest(endpoint: string): Promise<any> {
    const options: RequestInit = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (this.auth) {
      const credentials = btoa(`${this.auth.user}:${this.auth.pass}`);
      options.headers!['Authorization'] = `Basic ${credentials}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, options);
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getApiInfo(): Promise<any> {
    return this.getRequest('/');
  }

  async getSystemHealth(): Promise<any> {
    return this.getRequest('/api/v1/system/health');
  }

  async listLights(): Promise<any[]> {
    return this.getRequest('/api/v1/lights');
  }

  async turnOn(lightId?: number, request: LightOperationRequest = {}): Promise<LightOperationResponse> {
    const endpoint = lightId !== undefined 
      ? `/api/v1/lights/${lightId}/on`
      : '/api/v1/lights/on';
    
    const data = {
      color: 'green',
      dim: 1.0,
      led: 0,
      ...request
    };
    
    return this.postRequest(endpoint, data);
  }

  async turnOff(lightId?: number): Promise<LightOperationResponse> {
    const endpoint = lightId !== undefined 
      ? `/api/v1/lights/${lightId}/off`
      : '/api/v1/lights/off';
    
    return this.postRequest(endpoint, {});
  }

  async blink(lightId?: number, request: LightOperationRequest = {}): Promise<LightOperationResponse> {
    const endpoint = lightId !== undefined 
      ? `/api/v1/lights/${lightId}/blink`
      : '/api/v1/lights/blink';
    
    const data = {
      color: 'red',
      dim: 1.0,
      led: 0,
      speed: 'slow',
      count: 0,
      ...request
    };
    
    return this.postRequest(endpoint, data);
  }

  async rainbowEffect(lightId?: number, request: Omit<LightOperationRequest, 'color'> = {}): Promise<any> {
    const endpoint = lightId !== undefined 
      ? `/api/v1/effects/${lightId}/rainbow`
      : '/api/v1/effects/rainbow';
    
    const data = {
      dim: 1.0,
      led: 0,
      speed: 'slow',
      ...request
    };
    
    return this.postRequest(endpoint, data);
  }
}

// Usage
const client = new ModernBusyLightClient('http://localhost:8000', {
  user: 'admin',
  pass: 'password'
});

// Turn all lights blue at 50% brightness
await client.turnOn(undefined, { color: 'blue', dim: 0.5 });

// Start fast rainbow effect on light 0
await client.rainbowEffect(0, { speed: 'fast', dim: 0.8 });
```

## Integration Examples

### CI/CD Pipeline Integration (Updated)

```yaml
# .github/workflows/ci.yml
name: CI Pipeline with BusyLight v1 API

on: [push, pull_request]

jobs:
  test:
    runs-on: self-hosted  # Requires self-hosted runner with BusyLight
    steps:
      - uses: actions/checkout@v4
      
      - name: Signal build start
        run: |
          curl -X POST http://localhost:8000/api/v1/lights/blink \
            -H "Content-Type: application/json" \
            -d '{"color": "blue", "speed": "fast"}' || true
      
      - name: Run tests
        run: npm test
      
      - name: Signal success
        if: success()
        run: |
          curl -X POST http://localhost:8000/api/v1/lights/on \
            -H "Content-Type: application/json" \
            -d '{"color": "green"}' || true
          sleep 2
          curl -X POST http://localhost:8000/api/v1/lights/off \
            -H "Content-Type: application/json" \
            -d '{}' || true
      
      - name: Signal failure  
        if: failure()
        run: |
          curl -X POST http://localhost:8000/api/v1/lights/blink \
            -H "Content-Type: application/json" \
            -d '{"color": "red", "count": 10, "speed": "fast"}' || true
```

### Status Dashboard (Modern)

```html
<!DOCTYPE html>
<html>
<head>
    <title>BusyLight Modern Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .dashboard { max-width: 800px; margin: 0 auto; padding: 20px; }
        .control-group { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
        .button-group { display: flex; gap: 10px; flex-wrap: wrap; }
        button { 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer;
            font-size: 14px;
            transition: opacity 0.2s;
        }
        button:hover { opacity: 0.8; }
        .status { 
            font-family: 'SF Mono', Monaco, monospace; 
            background: #f5f5f5; 
            padding: 15px; 
            border-radius: 6px; 
            margin-top: 20px;
            white-space: pre-wrap;
        }
        .health-status { 
            padding: 10px; 
            border-radius: 6px; 
            margin: 10px 0;
            font-weight: bold;
        }
        .healthy { background-color: #d4edda; color: #155724; }
        .unhealthy { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>BusyLight Control Dashboard</h1>
        
        <div class="control-group">
            <h3>System Status</h3>
            <button onclick="checkHealth()">Check Health</button>
            <button onclick="getApiInfo()">API Info</button>
            <div id="health-status"></div>
        </div>
        
        <div class="control-group">
            <h3>Quick Controls</h3>
            <div class="button-group">
                <button onclick="setStatus('available')" style="background: #28a745; color: white;">Available</button>
                <button onclick="setStatus('busy')" style="background: #ffc107; color: black;">Busy</button>
                <button onclick="setStatus('meeting')" style="background: #dc3545; color: white;">In Meeting</button>
                <button onclick="setStatus('offline')" style="background: #6c757d; color: white;">Offline</button>
            </div>
        </div>
        
        <div class="control-group">
            <h3>Effects</h3>
            <div class="button-group">
                <button onclick="startEffect('rainbow')" style="background: linear-gradient(45deg, #ff0000, #ff7700, #ffff00, #00ff00, #0000ff, #8b00ff); color: white;">Rainbow</button>
                <button onclick="startEffect('blink')" style="background: #17a2b8; color: white;">Blink</button>
                <button onclick="startEffect('pulse')" style="background: #6610f2; color: white;">Pulse</button>
            </div>
        </div>
        
        <div class="control-group">
            <h3>Individual Light Control</h3>
            <div id="light-controls"></div>
        </div>
        
        <div class="status" id="status">Ready</div>
    </div>

    <script>
        const API_BASE = 'http://localhost:8000';
        
        async function postRequest(endpoint, data = {}) {
            try {
                const response = await fetch(`${API_BASE}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                updateStatus(JSON.stringify(result, null, 2));
                return result;
            } catch (error) {
                updateStatus(`Error: ${error.message}`, 'error');
                throw error;
            }
        }
        
        async function getRequest(endpoint) {
            try {
                const response = await fetch(`${API_BASE}${endpoint}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                updateStatus(JSON.stringify(result, null, 2));
                return result;
            } catch (error) {
                updateStatus(`Error: ${error.message}`, 'error');
                throw error;
            }
        }
        
        function updateStatus(text, type = 'info') {
            const statusEl = document.getElementById('status');
            statusEl.textContent = text;
            statusEl.style.color = type === 'error' ? '#dc3545' : '#333';
        }
        
        async function checkHealth() {
            try {
                const health = await getRequest('/api/v1/system/health');
                const healthEl = document.getElementById('health-status');
                const isHealthy = health.status === 'healthy';
                
                healthEl.innerHTML = `
                    <div class="${isHealthy ? 'healthy' : 'unhealthy'} health-status">
                        Status: ${health.status} | 
                        Lights Available: ${health.lights_available} |
                        ${health.timestamp ? `Updated: ${new Date(health.timestamp).toLocaleTimeString()}` : ''}
                    </div>
                `;
            } catch (error) {
                console.error('Health check failed:', error);
            }
        }
        
        async function getApiInfo() {
            await getRequest('/');
        }
        
        async function setStatus(status) {
            const colors = {
                'available': 'green',
                'busy': 'yellow', 
                'meeting': 'red',
                'offline': 'black'
            };
            
            if (status === 'offline') {
                await postRequest('/api/v1/lights/off');
            } else {
                await postRequest('/api/v1/lights/on', { color: colors[status] });
            }
        }
        
        async function startEffect(effect) {
            if (effect === 'rainbow') {
                await postRequest('/api/v1/effects/rainbow', { speed: 'medium' });
            } else if (effect === 'blink') {
                await postRequest('/api/v1/lights/blink', { 
                    color: 'red', 
                    count: 5, 
                    speed: 'fast' 
                });
            } else if (effect === 'pulse') {
                await postRequest('/api/v1/effects/pulse', { 
                    color: 'blue', 
                    count: 3,
                    speed: 'medium'
                });
            }
        }
        
        async function loadLights() {
            try {
                const lights = await getRequest('/api/v1/lights');
                const controlsEl = document.getElementById('light-controls');
                
                controlsEl.innerHTML = lights.map((light, index) => `
                    <div style="margin: 10px 0; padding: 10px; border: 1px solid #eee; border-radius: 4px;">
                        <strong>Light ${light.light_id}: ${light.name}</strong>
                        <div style="margin-top: 8px;">
                            <button onclick="controlLight(${light.light_id}, 'on', 'red')">Red</button>
                            <button onclick="controlLight(${light.light_id}, 'on', 'green')">Green</button>
                            <button onclick="controlLight(${light.light_id}, 'on', 'blue')">Blue</button>
                            <button onclick="controlLight(${light.light_id}, 'off')">Off</button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Failed to load lights:', error);
            }
        }
        
        async function controlLight(lightId, action, color) {
            if (action === 'on') {
                await postRequest(`/api/v1/lights/${lightId}/on`, { color });
            } else {
                await postRequest(`/api/v1/lights/${lightId}/off`);
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', () => {
            checkHealth();
            loadLights();
        });
    </script>
</body>
</html>
```

## Migration Guide

### Gradual Migration Strategy

```python
class HybridBusyLightClient:
    """Client that supports both v1 and compatibility endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 auth: Optional[tuple] = None, prefer_v1: bool = True):
        self.modern_client = ModernBusyLightClient(base_url, auth, use_v1=True)
        self.compat_client = CompatibilityBusyLightClient(base_url, auth)
        self.prefer_v1 = prefer_v1
    
    def turn_on(self, light_id: int, color: str = "green", **kwargs):
        """Turn on light using preferred API version."""
        if self.prefer_v1:
            try:
                return self.modern_client.turn_on(light_id, color, **kwargs)
            except Exception as e:
                print(f"V1 API failed, falling back to compatibility: {e}")
                return self.compat_client.turn_on(light_id, color, **kwargs)
        else:
            return self.compat_client.turn_on(light_id, color, **kwargs)

# Migration steps:
# 1. Use HybridBusyLightClient with prefer_v1=False initially
# 2. Test v1 endpoints by setting prefer_v1=True  
# 3. Switch to ModernBusyLightClient when ready
```

## Error Handling Best Practices

```python
import requests
import time
from typing import Optional

class RobustBusyLightClient:
    def __init__(self, base_url: str, max_retries: int = 3, use_v1: bool = True):
        self.base_url = base_url
        self.max_retries = max_retries
        self.use_v1 = use_v1
        self.session = requests.Session()
    
    def _safe_request(self, method: str, endpoint: str, 
                     data: Optional[dict] = None, 
                     params: Optional[dict] = None) -> Optional[dict]:
        """Make API request with retry logic and error handling."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'POST':
                    response = self.session.post(
                        url, 
                        json=data, 
                        timeout=10,
                        headers={'Content-Type': 'application/json'}
                    )
                else:
                    response = self.session.get(url, params=params, timeout=10)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.ConnectionError:
                print(f"Connection failed (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    print("Authentication required")
                elif response.status_code == 503:
                    print("No lights available")
                elif response.status_code == 422:
                    print(f"Validation error: {response.json()}")
                break  # Don't retry HTTP errors
                
            except requests.exceptions.Timeout:
                print(f"Request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    continue
                    
        return None
    
    def safe_turn_on(self, light_id: Optional[int] = None, 
                    color: str = "green") -> bool:
        """Safely turn on light with error handling."""
        if self.use_v1:
            endpoint = f"/api/v1/lights/{light_id}/on" if light_id else "/api/v1/lights/on"
            result = self._safe_request('POST', endpoint, {"color": color})
        else:
            endpoint = f"/light/{light_id}/on" if light_id else "/lights/on"
            result = self._safe_request('GET', endpoint, params={"color": color})
        
        return result is not None and result.get('success', True)
```

## OpenAPI Code Generation

The v1 API provides OpenAPI 3.0 specifications for automatic client generation:

```bash
# Generate TypeScript client
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o ./generated-client

# Generate Python client  
openapi-generator generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./generated-python-client
```

These examples demonstrate how to integrate with both the modern v1 API and 
maintain compatibility with existing code using the compatibility endpoints.