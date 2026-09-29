# API Contract

## Core
GET /health
POST /auth/login
POST /incidents
GET /incidents
GET /incidents/{id}
PATCH /incidents/{id}

## Brute Force
POST /simulations/brute-force

## AI
POST /incidents/{id}/analyze
POST /incidents/{id}/reanalyze
POST /incidents/{id}/review

## Timeline
GET /incidents/{id}/timeline

Exact request/response schemas will be finalized before integration.
