# Web API Overview

The BusyLight HTTP API provides RESTful endpoints for controlling USB LED
lights. The API returns JSON responses and supports the same functionality
as the command-line interface.

## Quick Start

### Start the Server

```bash
# Install with web API support
pip install busylight-for-humans[webapi]

# Start server
busyserve

# Start with custom host/port
busyserve --host 0.0.0.0 --port 8080

# Start in background
busyserve -D
```

### Basic Usage

```bash
# Get server status
curl http://localhost:8000/

# Turn light on (green)
curl http://localhost:8000/light/0/on

# Turn light red
curl "http://localhost:8000/light/0/on?color=red"

# Blink light blue 3 times
curl "http://localhost:8000/light/0/blink?color=blue&count=3"

# Turn light off
curl http://localhost:8000/light/0/off
```

## API Features

- **RESTful design** with consistent JSON responses
- **Device targeting** by index or all devices
- **LED targeting** for multi-LED devices
- **Color specification** via query parameters
- **Effect control** with customizable parameters
- **Authentication** via HTTP Basic Auth (optional)
- **CORS support** for browser-based applications
- **Interactive documentation** at `/docs` and `/redoc`

## Base URL

```
http://localhost:8000
```

Default host is `localhost` and port is `8000`. Configure with command-line
options:

```bash
busyserve --host 0.0.0.0 --port 8080
```

## Response Format

All endpoints return JSON responses with consistent structure:

### Success Response

```json
{
  "action": "on",
  "light_id": 0,
  "color": "red", 
  "rgb": [255, 0, 0],
  "led": 0
}
```

### Error Response

```json
{
  "message": "Light index 5 not found"
}
```

## Content Types

- **Request**: Query parameters or JSON body
- **Response**: `application/json`

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Device not found |
| 422 | Invalid parameter |
| 500 | Server error |

## Authentication

Optional HTTP Basic Authentication for securing API access.

### Setup

```bash
# Set environment variables
export BUSYLIGHT_API_USER="admin"
export BUSYLIGHT_API_PASS="secret"

# Start server
busyserve
```

### Usage

```bash
# Authenticated request
curl -u admin:secret http://localhost:8000/light/0/on
```

!!! warning "Security Warning"
    HTTP Basic Auth sends credentials in cleartext. Use HTTPS in production
    environments.

## CORS Configuration

Configure Cross-Origin Resource Sharing for browser applications.

### Setup

```bash
# Allow specific origins
export BUSYLIGHT_API_CORS_ORIGINS_LIST='["http://localhost:3000", "https://myapp.com"]'

# Start server  
busyserve
```

### Debug Mode

```bash
# Enable debug CORS (localhost only)
export BUSYLIGHT_DEBUG=true
busyserve
```

## Interactive Documentation

The API provides interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

These interfaces allow testing endpoints directly from the browser.

## Rate Limiting

The API does not impose rate limiting, but devices may have physical
limitations on how quickly they can change colors or effects.

## Health Check

```bash
# Check server status
curl http://localhost:8000/

# Response
[
  {"path": "/"},
  {"path": "/lights"},
  {"path": "/light/{light_id}"}
]
```

## Error Handling

The API provides detailed error messages for troubleshooting:

- **Device not found**: Check device connections and indices
- **Invalid color**: Use supported color names or hex values
- **Parameter errors**: Verify parameter names and value ranges
- **Server errors**: Check server logs with `--debug` flag

## Next Steps

- [Endpoint Reference](endpoints.md) - Complete API documentation
- [Integration Guide](integration.md) - Adding API to your projects
- [Device Support](../devices/index.md) - Hardware compatibility