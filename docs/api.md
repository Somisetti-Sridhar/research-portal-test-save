# API Documentation

## Overview

The Research Platform provides RESTful API endpoints for accessing papers, bookmarks, and ratings. The API uses session-based authentication and follows the same role-based permissions as the web interface.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses Django's session authentication. Users must be logged in through the web interface to access API endpoints.

### Headers

```http
Content-Type: application/json
X-CSRFToken: <csrf-token>
```

## Endpoints

### Papers

#### List Papers

```http
GET /api/papers/
```

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/papers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Machine Learning in Healthcare",
      "authors": "John Doe, Jane Smith",
      "abstract": "This paper explores...",
      "publication_date": "2023-01-15",
      "categories": ["AI", "Healthcare"],
      "is_approved": true,
      "view_count": 42,
      "download_count": 15,
      "pdf_file": "/media/papers/pdfs/paper1.pdf"
    }
  ]
}
```

#### Get Paper Details

```http
GET /api/papers/{id}/
```

**Response:**
```json
{
  "id": 1,
  "title": "Machine Learning in Healthcare",
  "authors": "John Doe, Jane Smith",
  "abstract": "This paper explores the application of machine learning...",
  "summary": "Generated summary of the paper...",
  "publication_date": "2023-01-15",
  "categories": [
    {"id": 1, "name": "AI"},
    {"id": 2, "name": "Healthcare"}
  ],
  "is_approved": true,
  "view_count": 42,
  "download_count": 15,
  "pdf_file": "/media/papers/pdfs/paper1.pdf",
  "uploaded_by": {
    "id": 1,
    "username": "researcher1",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Search Papers

```http
GET /api/papers/?search=machine+learning&category=AI&year_from=2020&year_to=2023
```

**Query Parameters:**
- `search`: Keyword search in title, abstract, authors
- `category`: Filter by category name
- `year_from`: Filter papers from this year
- `year_to`: Filter papers up to this year
- `page`: Page number for pagination

### Bookmarks

#### List User Bookmarks

```http
GET /api/bookmarks/
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "paper": {
        "id": 1,
        "title": "Machine Learning in Healthcare",
        "authors": "John Doe, Jane Smith"
      },
      "created_at": "2023-06-15T10:30:00Z",
      "notes": "Important for my research"
    }
  ]
}
```

#### Create Bookmark

```http
POST /api/bookmarks/
```

**Request Body:**
```json
{
  "paper_id": 1,
  "notes": "Interesting approach to the problem"
}
```

**Response:** `501 Not Implemented` (by design)

### Ratings

#### List Paper Ratings

```http
GET /api/ratings/
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "paper": {
        "id": 1,
        "title": "Machine Learning in Healthcare"
      },
      "user": {
        "id": 1,
        "username": "researcher1"
      },
      "rating": 5,
      "review": "Excellent paper with novel insights",
      "created_at": "2023-06-15T14:20:00Z"
    }
  ]
}
```

#### Get Ratings for Specific Paper

```http
GET /api/ratings/?paper_id=1
```

#### Create Rating

```http
POST /api/ratings/
```

**Request Body:**
```json
{
  "paper_id": 1,
  "rating": 5,
  "review": "Outstanding research methodology"
}
```

**Response:** `501 Not Implemented` (by design)

### Recommendations

#### Get User Recommendations

```http
GET /api/recommendations/
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "paper": {
        "id": 5,
        "title": "Advanced Neural Networks",
        "authors": "Alice Johnson"
      },
      "score": 0.85,
      "reason": "Recommended by improved hybrid model",
      "created_at": "2023-06-15T09:00:00Z"
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid parameters",
  "details": {
    "year_from": ["Enter a valid year"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied"
}
```

### 404 Not Found
```json
{
  "error": "Paper not found"
}
```

### 501 Not Implemented
```json
{
  "error": "Create operations not implemented"
}
```

## Rate Limiting

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour

## Pagination

All list endpoints support pagination:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/papers/?page=3",
  "previous": "http://localhost:8000/api/papers/?page=1",
  "results": [...]
}
```

## Usage Examples

### Python with requests

```python
import requests

# Login first through web interface to get session
session = requests.Session()

# Get papers
response = session.get('http://localhost:8000/api/papers/')
papers = response.json()

# Search papers
response = session.get('http://localhost:8000/api/papers/', params={
    'search': 'machine learning',
    'category': 'AI'
})
```

### JavaScript with fetch

```javascript
// Get papers
fetch('/api/papers/')
  .then(response => response.json())
  .then(data => console.log(data));

// Search papers
const params = new URLSearchParams({
  search: 'neural networks',
  year_from: '2020'
});

fetch(`/api/papers/?${params}`)
  .then(response => response.json())
  .then(data => console.log(data));
```