# API
Base URL: http://127.0.0.1:8000
- GET /api/health
- GET /api/dashboard
- GET /api/customers?limit=100
- GET /api/carts?status=ABANDONED&limit=100
- GET /api/campaigns
- GET /api/sends?limit=100
- GET /api/orders?limit=100
- GET /api/anomalies
- GET /api/consent/{customer_id}
Interactive OpenAPI: /docs. Database connection failures return HTTP 503 with setup guidance.