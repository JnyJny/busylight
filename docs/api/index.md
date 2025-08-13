# Web API Overview

The BusyLight HTTP API provides RESTful endpoints for controlling USB LED
lights. Built with FastAPI, it features proper HTTP methods, domain-based 
organization, API versioning, and comprehensive OpenAPI documentation.

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
# Get API information
curl http://localhost:8000/

# Check system health
curl http://localhost:8000/system/health

# Turn light on (green) - REST endpoint
curl -X POST http://localhost:8000/api/v1/lights/0/on \
  -H "Content-Type: application/json" \
  -d '{"color": "green", "dim": 1.0, "led": 0}'

# Turn light red - backwards compatible
curl "http://localhost:8000/light/0/on?color=red"

# Start rainbow effect
curl -X POST http://localhost:8000/api/v1/effects/rainbow \
  -H "Content-Type: application/json" \
  -d '{"dim": 0.8, "speed": "fast"}'
```

## API Features

- **Domain-based organization** - lights, effects, system endpoints
- **API versioning** - v1 endpoints with backwards compatibility
- **Proper HTTP methods** - POST for actions, GET for queries  
- **JSON request/response** with Pydantic validation
- **Device targeting** by index or all devices
- **LED targeting** for multi-LED devices
- **Authentication** via HTTP Basic Auth (optional)
- **CORS support** for browser-based applications
- **Interactive documentation** at `/docs` and `/redoc`
- **OpenAPI 3.0** specification for code generation

## API Endpoints

The API provides multiple access patterns:

### Versioned API (Recommended)
```
http://localhost:8000/api/v1/
```

### Backwards Compatible
```
http://localhost:8000/
```

Default host is `localhost` and port is `8000`. Configure with command-line
options:

```bash
busyserve --host 0.0.0.0 --port 8080 --debug  # Enable debug logging
```

## Response Format

All endpoints return JSON responses with consistent structure:

### Light Operation Response

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

### Error Response

```json
{
  "detail": "Light index 5 not found"
}
```

## Content Types

- **V1 Endpoints**: JSON request/response (`application/json`)
- **Compatibility Endpoints**: Query parameters with JSON response
- **All Responses**: `application/json`

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Authentication required |
| 404 | Device not found |
| 422 | Validation error |
| 503 | No lights available |
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
# V1 authenticated request
curl -u admin:secret -X POST http://localhost:8000/api/v1/lights/0/on \
  -H "Content-Type: application/json" \
  -d '{"color": "red"}'

# Compatibility authenticated request  
curl -u admin:secret http://localhost:8000/light/0/on?color=red
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

## System Endpoints

```bash
# API information
curl http://localhost:8000/

# System health check
curl http://localhost:8000/system/health

# System information
curl http://localhost:8000/system/info
```

### Health Response
```json
{
  "status": "healthy",
  "lights_available": 2,
  "timestamp": "2023-01-01T12:00:00Z"
}
```

## Backwards Compatibility

The API maintains full backwards compatibility with existing integrations:

- **Original endpoints** work unchanged (GET requests with query parameters)
- **Original response format** preserved for compatibility endpoints
- **Gradual migration** - use v1 endpoints for new features, keep existing code working
- **Deprecation warnings** in OpenAPI docs for legacy endpoints

### Migration Path

1. **Keep existing code working** - no immediate changes needed
2. **New features** - use `/api/v1/` endpoints with JSON payloads
3. **Gradual adoption** - migrate endpoints one at a time
4. **Full migration** - eventually adopt v1 endpoints for all operations

## Logging

The API uses integrated logging that properly displays both FastAPI and uvicorn events:

```bash
# Normal logging
busyserve

# Debug logging with detailed output
busyserve --debug
```

### Features

- **Integrated logging**: All API, uvicorn, and application events appear in a unified log
- **Color-coded output**: Different log levels are visually distinct  
- **Request tracing**: HTTP requests and responses are logged when debug is enabled
- **Structured format**: Timestamps, levels, module names, and line numbers included

### Log Levels

- **INFO**: Server startup, configuration, API operations
- **DEBUG**: Detailed request/response data, internal operations  
- **WARNING**: Configuration issues, recoverable errors
- **ERROR**: Request failures, server errors

**Previous Issue Resolved:** Earlier versions had logging compatibility issues between loguru and uvicorn - this has been fixed with integrated logging handlers.

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