# 🚀 ZeroDev AI - Production Ready Platform

**Status:** ✅ PRODUCTION READY  
**Version:** 1.0.0  
**Last Updated:** 2025-08-19

ZeroDev AI is a comprehensive platform that leverages generative AI to automate software development tasks. With enterprise-grade security, real-time authentication, and advanced dashboard capabilities, it's designed to be a complete solution for AI-driven software engineering.

## 🎉 Latest Achievement

**ALL P0 MODULES COMPLETED!** 
- ✅ F05 Authentication System
- ✅ F08 Dashboard API Integration  
- ✅ B15 Security Engine
- ✅ Project fully cleaned and optimized

## 🏗️ About The Project

This repository contains the production-ready ZeroDev AI platform with:

### 🔐 **F05 Authentication System**
- JWT-based authentication with refresh tokens
- React AuthContext for state management  
- Protected routes and middleware
- Secure session handling

### 📊 **F08 Dashboard API Integration**  
- Real backend API replacing all mock data
- TanStack Query for optimized data fetching
- Real-time updates and cache management
- Error handling and retry logic

### 🛡️ **B15 Security Engine**
- Enterprise-grade security middleware
- Rate limiting (100 req/min per IP)
- Content validation and XSS protection  
- Comprehensive audit logging
- SQL injection prevention

### 🚀 **Core Platform Features**
*   **AI-Powered Code Generation**: Generate code from natural language
*   **Project Scaffolding**: Quick project setup with best practices
*   **CI/CD Integration**: Automated testing and deployment pipelines  
*   **Extensible Agent System**: Modular architecture for new capabilities
*   **Enterprise Security**: Production-grade security controls

## Tech Stack

The ZeroDev AI platform is built with a modern tech stack, chosen for performance, scalability, and developer experience.

### Backend
*   **Python**: The primary language for the backend services.
*   **FastAPI**: A modern, high-performance web framework for building APIs.
*   **SQLModel**: A library for interacting with SQL databases from Python code, with Python type hints.
*   **PostgreSQL**: The primary database for storing project and user data.
*   **Celery**: A distributed task queue for running background jobs.
*   **Redis**: An in-memory data store used as a message broker for Celery and for caching.
*   **Docker**: For containerizing the backend application.

### Frontend
*   **Next.js**: A React framework for building server-side rendered and static web applications.
*   **React**: A JavaScript library for building user interfaces.
*   **TypeScript**: A typed superset of JavaScript that compiles to plain JavaScript.
*   **Tailwind CSS**: A utility-first CSS framework for rapidly building custom designs.
*   **Vitest**: A blazing fast unit-test framework powered by Vite.
*   **Vercel**: A cloud platform for static sites and Serverless Functions.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

*   [Node.js](https://nodejs.org/) (v18 or later)
*   [Python](https://www.python.org/) (v3.9 or later)
*   [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

### Installation

1.  **Clone the repo**
    ```sh
    git clone https://github.com/your_username/your_repository.git
    cd your_repository
    ```

2.  **Set up the backend**
    *   Navigate to the `backend` directory:
        ```sh
        cd backend
        ```
    *   Create a virtual environment:
        ```sh
        python -m venv venv
        source venv/bin/activate
        ```
    *   Install the required packages:
        ```sh
        pip install -r requirements.txt
        ```
    *   Set up the environment variables. Copy the example `.env` file:
        ```sh
        cp .env.example .env
        ```
        You will need to fill in the values in the `.env` file, such as your database connection string and any API keys.

3.  **Set up the frontend**
    *   Navigate to the `frontend` directory:
        ```sh
        cd ../frontend
        ```
    *   Install NPM packages:
        ```sh
        npm install
        ```

### Running the Project

1.  **Start the backend services**
    *   You will need a running PostgreSQL and Redis instance. You can use Docker Compose for this. A `docker-compose.yml` file is not provided in this repository, but you can create one with the following content:
        ```yml
        version: '3.8'
        services:
          postgres:
            image: postgres:13
            environment:
              POSTGRES_USER: user
              POSTGRES_PASSWORD: password
              POSTGRES_DB: zerodev
            ports:
              - "5432:5432"
          redis:
            image: redis:6.2-alpine
            ports:
              - "6379:6379"
        ```
    *   Start the services:
        ```sh
        docker-compose up -d
        ```
    *   Run the database migrations:
        ```sh
        alembic upgrade head
        ```
    *   Start the FastAPI server:
        ```sh
        uvicorn main:app --reload
        ```

2.  **Start the frontend application**
    *   In a separate terminal, navigate to the `frontend` directory:
        ```sh
        cd frontend
        ```
    *   Start the development server:
        ```sh
        npm run dev
        ```
    The application will be available at `http://localhost:3000`.

## Architectural Overview

The ZeroDev AI backend is designed with a modular architecture to separate concerns and allow for scalability. Here's a brief overview of the key modules:

*   **`agents`**: Contains the different AI agents responsible for specific tasks like code generation, scaffolding, and CI/CD integration. Each agent is a self-contained module with a specific purpose.
*   **`api`**: Defines the API endpoints for the application. This is the entry point for all frontend requests.
*   **`core`**: Contains the core components of the application, such as the database connection, AI model routing, and security settings.
*   **`models`**: Defines the data models for the application, using SQLModel to represent database tables.
*   **`schemas`**: Defines the Pydantic schemas used for API request and response validation.
*   **`security_engine`**: Implements security features like input filtering and policy enforcement to ensure the generated code is safe.
*   **`services`**: Contains business logic that is shared across different parts of the application.
*   **`tasks`**: Contains Celery tasks for running asynchronous jobs, such as code generation or project analysis.
*   **`transformation`**: A module responsible for transforming and modifying code, for example, by applying patches or running refactoring operations.
*   **`version_engine`**: Manages versioning of the generated code and the AI agents.
