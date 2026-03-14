# Sentinels of Integrity: Google Cloud Platform (GCP) Deployment Guide

This document outlines the architectural changes and additions required to deploy the "Sentinels of Integrity" project on Google Cloud Platform for production scale.

## 1. Containerization (Docker)
Before deploying to GCP, the application needs to be packaged into Docker containers.

**Current State**: Running locally via `uvicorn`.
**Required Change**: Create two `Dockerfile`s:
- `api/Dockerfile` for the FastAPI backend.
- `ml_models/Dockerfile` for the machine learning inference service.

*Benefit*: Ensures the application runs identically on GCP as it does on your local machine.

## 2. Serverless Computing (Google Cloud Run)
Google Cloud Run is the ideal choice for stateless web applications and APIs.

**Current State**: Localhost exposed ports (8000, 8001).
**Required Change**: 
- Deploy the `api` container to Cloud Run.
- Deploy the `ml_models` container to Cloud Run (with CPU/Memory customized for ML inference) OR deploy to **Google Kubernetes Engine (GKE)** if models require heavy GPU processing.

*Benefit*: Auto-scaling from zero to thousands of requests automatically, paying only for the exact milliseconds your code runs.

## 3. Database Migration (Cloud SQL)
The platform needs a persistent database for storing generated trust reports and API keys.

**Current State**: Mock implementations for memory storage.
**Required Change**: 
- Configure a PostgreSQL database using Google Cloud SQL.
- Update `api/app/config.py` to point to the Cloud SQL instance connection string.
- Implement SQLAlchemy/Alembic ORMs to handle the actual database insertions.

*Benefit*: Highly available, automated backups and replicas.

## 4. Object Storage (Google Cloud Storage - GCS)
If the platform eventually accepts direct video uploads rather than just URLs, it will need a place to store those files during processing.

**Current State**: Evaluating URLs only.
**Required Change**:
- Create a GCS Bucket (e.g., `sentinels-media-processing`).
- Integrate Google Cloud Storage client in the backend to download, hash, and delete media files securely.

*Benefit*: Inexpensive, highly durable storage for large media files.

## 5. Security & Rate Limiting (Google Cloud Armor & API Gateway)
To prevent abuse, the backend needs robust protection before it is exposed to the public internet.

**Current State**: Basic internal rate-limiting middleware.
**Required Change**:
- Route traffic through an API Gateway to handle authentication keys.
- Place Google Cloud Armor in front of the services to protect against DDoS attacks.

*Benefit*: Enterprise-grade security against bots and malicious scrapers.

## 6. Real Blockchain Integration (Polygon / Web3)
Currently, the blockchain interaction is simulated to provide varied, randomized results.

**Current State**: Simulated `BlockchainService`.
**Required Change**:
- Setup a secure Google Secret Manager store for the Web3 Private Keys.
- Integrate the official `web3.py` library to communicate with an official Polygon RPC (e.g., Alchemy or Infura).
- Write and deploy Solidity Smart Contracts to the Polygon zkEVM blockchain.

*Benefit*: Cryptographically verifiable timestamps of media analysis.

---

### Step-by-Step Execution Plan for GCP:
1. Turn `requirements.txt` into a minimal production-ready list.
2. Write Dockerfiles for FastAPI & ML Services.
3. Setup Google Cloud account and enable billing.
4. Install `gcloud` CLI.
5. Push Docker images to **Google Artifact Registry**.
6. Deploy images to **Cloud Run**.
7. Host the `visual_demo.html` frontend on **Google Cloud Storage (Static Hosting)** or **Firebase Hosting**.
