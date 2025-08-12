# API Endpoints

Complete reference for all BusyLight Web API endpoints.

## Device Information

### List Available Endpoints

```http
GET /
```

Returns list of available API endpoints.

**Response:**
```json
[
  {"path": "/"},
  {"path": "/lights"},  
  {"path": "/light/{light_id}"}
]
```

### Get All Lights Status

```http
GET /lights
GET /lights/status
```

Returns status information for all connected lights.

**Response:**
```json
[
  {
    "light_id": 0,
    "name": "Blink(1) mk2",
    "info": {
      "path": "/dev/hidraw0",
      "vendor_id": 10168,
      "product_id": 493
    },
    "is_on": true,
    "color": "red",
    "rgb": [255, 0, 0]
  }
]
```

### Get Single Light Status

```http
GET /light/{light_id}
GET /light/{light_id}/status
```

Returns status for specific light.

**Parameters:**
- `light_id` (path, int): Light index (0-based)

**Response:**
```json
{
  "light_id": 0,
  "name": "Blink(1) mk2",
  "info": {
    "path": "/dev/hidraw0",
    "vendor_id": 10168,
    "product_id": 493,
    "serial_number": "ABC123",
    "is_acquired": true
  },
  "is_on": true,
  "color": "red",
  "rgb": [255, 0, 0]
}
```

## Light Control

### Turn Light On

```http
GET /light/{light_id}/on
```

Turn on specific light with optional color and LED targeting.

**Parameters:**
- `light_id` (path, int): Light index
- `color` (query, str): Color name or hex value (default: "green")
- `dim` (query, float): Brightness factor 0.0-1.0 (default: 1.0)
- `led` (query, int): LED index for multi-LED devices (default: 0)

**Examples:**
```bash
# Basic usage
curl http://localhost:8000/light/0/on

# With color
curl "http://localhost:8000/light/0/on?color=red"

# With hex color
curl "http://localhost:8000/light/0/on?color=%23ff0000"

# With brightness
curl "http://localhost:8000/light/0/on?color=blue&dim=0.5"

# Target specific LED
curl "http://localhost:8000/light/0/on?color=red&led=1"
```

**Response:**
```json
{
  "action": "on",
  "light_id": 0,
  "color": "red",
  "rgb": [255, 0, 0],
  "dim": 1.0,
  "led": 0
}
```

### Turn All Lights On

```http
GET /lights/on
```

Turn on all connected lights.

**Parameters:**
- `color` (query, str): Color name or hex value (default: "green")
- `dim` (query, float): Brightness factor 0.0-1.0 (default: 1.0)  
- `led` (query, int): LED index for multi-LED devices (default: 0)

**Response:**
```json
{
  "action": "on",
  "light_id": "all",
  "color": "green",
  "rgb": [0, 128, 0],
  "dim": 1.0,
  "led": 0
}
```

### Turn Light Off

```http
GET /light/{light_id}/off
```

Turn off specific light.

**Parameters:**
- `light_id` (path, int): Light index

**Response:**
```json
{
  "action": "off",
  "light_id": 0
}
```

### Turn All Lights Off

```http
GET /lights/off
```

Turn off all connected lights.

**Response:**
```json
{
  "action": "off",
  "light_id": "all"
}
```

## Effects

### Blink Effect

```http
GET /light/{light_id}/blink
```

Create blinking effect on specific light.

**Parameters:**
- `light_id` (path, int): Light index
- `color` (query, str): Blink color (default: "red")
- `speed` (query, str): Speed - "slow", "medium", "fast" (default: "slow")
- `dim` (query, float): Brightness factor 0.0-1.0 (default: 1.0)
- `count` (query, int): Number of blinks, 0=infinite (default: 0)
- `led` (query, int): LED index for multi-LED devices (default: 0)

**Examples:**
```bash
# Basic blinking
curl http://localhost:8000/light/0/blink

# Blue, 5 blinks, fast
curl "http://localhost:8000/light/0/blink?color=blue&count=5&speed=fast"

# Target specific LED
curl "http://localhost:8000/light/0/blink?color=red&led=1&count=3"
```

**Response:**
```json
{
  "action": "blink",
  "light_id": 0,
  "color": "red",
  "rgb": [255, 0, 0],
  "speed": "slow",
  "dim": 1.0,
  "count": 0,
  "led": 0
}
```

### Blink All Lights

```http
GET /lights/blink
```

Create blinking effect on all lights.

**Parameters:** Same as single light blink

**Response:**
```json
{
  "action": "blink",
  "light_id": "all",
  "color": "red",
  "rgb": [255, 0, 0],
  "speed": "slow",
  "dim": 1.0,
  "count": 0,
  "led": 0
}
```

### Rainbow Effect

```http
GET /light/{light_id}/rainbow
```

Start rainbow color cycling on specific light.

**Parameters:**
- `light_id` (path, int): Light index
- `speed` (query, str): Effect speed (default: "slow")
- `dim` (query, float): Brightness factor (default: 1.0)

**Response:**
```json
{
  "action": "effect",
  "name": "rainbow",
  "light_id": 0,
  "speed": "slow",
  "dim": 1.0
}
```

### Rainbow All Lights

```http
GET /lights/rainbow
```

Start rainbow effect on all lights.

### Pulse Effect

```http
GET /light/{light_id}/pulse
```

Create pulsing/breathing effect on specific light.

**Parameters:**
- `light_id` (path, int): Light index
- `color` (query, str): Pulse color (default: "red")
- `speed` (query, str): Pulse speed (default: "slow")
- `dim` (query, float): Brightness factor (default: 1.0)
- `count` (query, int): Number of pulses, 0=infinite (default: 0)

**Response:**
```json
{
  "action": "effect",
  "name": "pulse",
  "light_id": 0,
  "color": "red",
  "rgb": [255, 0, 0],
  "speed": "slow",
  "dim": 1.0,
  "count": 0
}
```

### Flash Lights Impressively (FLI)

```http
GET /light/{light_id}/fli
```

Alternate between two colors (red and blue by default).

**Parameters:**
- `light_id` (path, int): Light index
- `color_a` (query, str): First color (default: "red")
- `color_b` (query, str): Second color (default: "blue") 
- `speed` (query, str): Flash speed (default: "slow")
- `dim` (query, float): Brightness factor (default: 1.0)
- `count` (query, int): Number of flashes, 0=infinite (default: 0)

**Response:**
```json
{
  "action": "effect",
  "name": "fli",
  "light_id": 0,
  "speed": "slow",
  "color": "red",
  "dim": 1.0,
  "count": 0
}
```

## Color Specification

Colors can be specified as:

- **Named colors**: `red`, `green`, `blue`, `yellow`, `purple`, `white`, etc.
- **Hex colors**: `#ff0000`, `0xff0000`, `ff0000` (URL encode `#` as `%23`)
- **RGB tuples**: `rgb(255,0,0)` (URL encoded)

## LED Parameter

For multi-LED devices (Blink1 mk2, BlinkStick variants):

- `led=0`: Control all LEDs (default)
- `led=1`: Control first/top LED
- `led=2`: Control second/bottom LED
- `led=3+`: Control additional LEDs (device-specific)

Single-LED devices ignore this parameter.

## Error Responses

### Device Not Found

```json
{
  "message": "Light index 5 not found"
}
```

**Status Code:** 404

### Invalid Color

```json
{
  "message": "Invalid color specification: 'notacolor'"
}
```

**Status Code:** 422

### Parameter Error

```json
{
  "message": "LED index must be >= 0"
}
```

**Status Code:** 422

## Rate Limiting

No explicit rate limiting is enforced, but consider device physical
limitations when making rapid requests.

## WebSocket Support

Currently not supported. All communication uses HTTP GET requests with
JSON responses.