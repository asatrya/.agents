# API Contract

## Base Path

`/api/v1`

## Authentication

[Bearer token, cookie session, API key, or other method]

## Response Shape

Success:

```json
{
  "success": true,
  "data": {}
}
```

Error:

```json
{
  "success": false,
  "message": "Readable error message",
  "code": "ERROR_CODE"
}
```

## Endpoint: Create Note

### Request

`POST /notes`

Authentication: Required

Body:

```json
{
  "title": "string",
  "content": "string"
}
```

Validation:

- `title` is required.
- `content` is required.
- [Length and format rules]

### Success

Status: `201`

```json
{
  "success": true,
  "data": {
    "id": "string",
    "title": "string",
    "content": "string",
    "createdAt": "ISO-8601 timestamp"
  }
}
```

### Errors

- `400` - invalid input
- `401` - unauthenticated
- `403` - forbidden
- `500` - unexpected server error
