# FastAPI + PostgreSQL (Docker) Backend

This repository contains a FastAPI backend application that connects to a PostgreSQL database running in a Docker container.  
The database is initialized automatically using SQLModel during application startup.


## Features

- FastAPI server with async support  
- PostgreSQL 16 running via Docker  
- SQLModel ORM with automatic table creation  
- Modular router structure  
- CORS configured for local Vite frontend (`localhost:5173`)  


## Running the Database with Docker

Start the database:

```bash
docker-compose up -d
```

Stop the database:

```bash
docker-compose down
```
Or use the Docker integration of your IDE.

## Requirements

Recommended Python version: **3.11+**

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the FastAPI Application

Run the backend from the project root directory:

```bash
uvicorn Application.backend.main:app
```

Or run main.py from your IDE.

API Documentation:

* Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc → [http://localhost:8000/redoc](http://localhost:8000/redoc)