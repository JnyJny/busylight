# API Endpoints

Complete reference for all BusyLight Web API endpoints.

## API Organization

The API is organized into three main domains:

- **Lights** - Basic device control (on, off, blink)
- **Effects** - Advanced light effects (rainbow, pulse, flash)
- **System** - API health and information

Each domain provides both versioned (`/api/v1/`) and compatibility endpoints.

## System Endpoints

### API Information

```http
GET /
```

Returns comprehensive API information including available versions, domains, and endpoints.

**Response:**
```json
{
  "name": "BusyLight API",
  "version": "0.43.1",
  "api_versions": {
    "v1": {
      "prefix": "/api/v1",
      "description": "Current stable API version",
      "features": ["REST endpoints", "Effects management", "LED targeting"]
    },
    "legacy": {
      "prefix": "/",
      "description": "Legacy endpoints for backward compatibility",
      "deprecated": true
    }
  },
  "domains": [
    {
      "name": "lights",
      "description": "Basic light control operations",
      "endpoints": ["/lights", "/lights/{id}"]
    }
  ]
}
```

### System Health

```http
GET /system/health
GET /api/v1/system/health
```

Check API server and device availability.

**Response:**
```json
{
  "status": "healthy",
  "lights_available": 2,
  "timestamp": "2023-01-01T12:00:00Z"
}
```

### System Information

```http
GET /system/info
GET /api/v1/system/info
```

Get server configuration details.

**Response:**
```json
{
  "title": "Busylight Server: A USB Light Server",
  "version": "0.43.1",
  "description": "An API server for USB connected presence lights."
}
```

## Lights Domain

### Get All Lights

```http
GET /lights
GET /api/v1/lights
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

### Get Single Light

```http
GET /lights/{light_id}/status
GET /api/v1/lights/{light_id}/status
```

Returns detailed status for specific light.

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
    "serial_number": "ABC123"
  },
  "is_on": true,
  "color": "red",
  "rgb": [255, 0, 0]
}
```

### Turn Light On (V1)

```http
POST /api/v1/lights/on
POST /api/v1/lights/{light_id}/on
```

Turn on all lights or specific light using JSON request body.

**Request Body:**
```json
{
  "color": "red",
  "dim": 1.0,
  "led": 0
}
```

**Parameters:**
- `color` (string): Color name or hex value (default: "green")
- `dim` (float): Brightness factor 0.0-1.0 (default: 1.0)
- `led` (int): LED index for multi-LED devices (default: 0)
- `light_id` (path, int): Light index for single light endpoints

**Examples:**
```bash
# Turn all lights red
curl -X POST http://localhost:8000/api/v1/lights/on \
  -H "Content-Type: application/json" \
  -d '{"color": "red", "dim": 0.8}'

# Turn specific light blue
curl -X POST http://localhost:8000/api/v1/lights/2/on \
  -H "Content-Type: application/json" \
  -d '{"color": "blue", "led": 1}'
```

**Response:**
```json
{
  "success": true,
  "action": "turned on",
  "lights_affected": 1,
  "details": [
    {
      "light_id": 0,
      "action": "turned on",
      "color": "red",
      "rgb": [255, 0, 0],
      "dim": 1.0,
      "led": 0
    }
  ]
}
```

### Turn Light Off (V1)

```http
POST /api/v1/lights/off
POST /api/v1/lights/{light_id}/off
```

Turn off all lights or specific light.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "action": "turned off",
  "lights_affected": 2,
  "details": [
    {
      "light_id": 0,
      "action": "turned off"
    },
    {
      "light_id": 1,
      "action": "turned off"
    }
  ]
}
```

### Blink Light (V1)

```http
POST /api/v1/lights/blink
POST /api/v1/lights/{light_id}/blink
```

Create blinking effect on lights.

**Request Body:**
```json
{
  "color": "red",
  "dim": 1.0,
  "speed": "slow",
  "count": 5,
  "led": 0
}
```

**Parameters:**
- `color` (string): Blink color (default: "red")
- `dim` (float): Brightness factor 0.0-1.0 (default: 1.0)
- `speed` (string): "slow", "medium", "fast" (default: "slow")
- `count` (int): Number of blinks, 0=infinite (default: 0)
- `led` (int): LED index for multi-LED devices (default: 0)

## Effects Domain

### Rainbow Effect (V1)

```http
POST /api/v1/effects/rainbow
POST /api/v1/effects/{light_id}/rainbow
```

Start rainbow color cycling effect.

**Request Body:**
```json
{
  "dim": 1.0,
  "speed": "slow",
  "led": 0
}
```

**Response:**
```json
{
  "success": true,
  "action": "rainbow effect started",
  "lights_affected": 1,
  "effect": {
    "name": "rainbow",
    "speed": "slow",
    "dim": 1.0,
    "led": 0
  }
}
```

### Pulse Effect (V1)

```http
POST /api/v1/effects/pulse
POST /api/v1/effects/{light_id}/pulse
```

Create pulsing/breathing effect.

**Request Body:**
```json
{
  "color": "red",
  "dim": 1.0,
  "speed": "slow",
  "count": 0,
  "led": 0
}
```

### Flash Effect (V1)

```http
POST /api/v1/effects/flash
POST /api/v1/effects/{light_id}/flash
```

Alternate between two colors.

**Request Body:**
```json
{
  "color_a": "red",
  "color_b": "blue",
  "dim": 1.0,
  "speed": "slow",
  "count": 0,
  "led": 0
}
```

## Compatibility Endpoints (Deprecated)

These endpoints maintain backwards compatibility with the original API. They use GET requests with query parameters and return simplified responses.

### Turn Light On (Compatibility)

```http
GET /light/{light_id}/on
GET /lights/on
```

**Parameters:**
- `color` (query, str): Color name or hex value (default: "green")
- `dim` (query, float): Brightness factor 0.0-1.0 (default: 1.0)
- `led` (query, int): LED index for multi-LED devices (default: 0)

**Examples:**
```bash
# Basic usage
curl http://localhost:8000/light/0/on

# With parameters
curl "http://localhost:8000/light/0/on?color=red&dim=0.5"
```

### Effects (Compatibility)

```http
GET /light/{light_id}/blink
GET /light/{light_id}/rainbow
GET /light/{light_id}/pulse
GET /light/{light_id}/fli
```

Query parameters match the original API specification.

## Color Specification

Colors can be specified as:

- **Named colors**: `red`, `green`, `blue`, `yellow`, `purple`, `white`, etc.
- **Hex colors**: `#ff0000`, `0xff0000`, `ff0000`
- **RGB tuples**: `rgb(255,0,0)` 

## LED Targeting

For multi-LED devices:

- `led=0`: Control all LEDs (default)
- `led=1`: Control first/top LED
- `led=2`: Control second/bottom LED
- `led=3+`: Control additional LEDs (device-specific)

## Error Responses

### Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["body", "dim"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### Device Not Found (404)

```json
{
  "detail": "Light index 5 not found"
}
```

### Authentication Required (401)

```json
{
  "detail": "Incorrect username or password"
}
```

### No Devices Available (503)

```json
{
  "detail": "No lights available"
}
```

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

These provide complete endpoint documentation with request/response schemas and testing capabilities.