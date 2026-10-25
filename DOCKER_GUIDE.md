# RoadSense: Docker & Containerization Guide

**Authors:** Rahul Kewat, Stewin Mathias, Reeven Menezes  
**Platform:** RoadSense Cloud Platform  

The RoadSense platform is fully containerized and production-ready with Docker and Docker Compose. This allows you to launch the complete cloud-native stack locally or on an Amazon EC2 instance with a single command.

---

## 🏗️ Container Architecture

The Docker setup mirrors our AWS cloud architecture:

| Service | Container Name | Base Image | Role | Port Mapping |
| :--- | :--- | :--- | :--- | :--- |
| **Database** | `roadsense-postgres` | `postgres:16-alpine` | PostgreSQL Database (mirrors **Amazon RDS**) | `5432:5432` |
| **Backend API** | `roadsense-backend` | `python:3.12-slim` | Flask REST API + Gunicorn (mirrors **Amazon EC2**) | `6969:6969` |
| **Admin Portal** | `roadsense-admin-web` | `nginx:alpine` | React 19 + TypeScript SPA + Nginx Reverse Proxy | `80:80`, `5173:80` |

---

## 🚀 Quick Start (One Command)

### 1. Build and Start All Services
From the root of the `RoadSense` repository, run:

```bash
docker compose up --build -d
```

Docker will:
1. Spin up the **PostgreSQL** database container and verify health via `pg_isready`.
2. Build the **Python 3.12 backend container**, install dependencies, and launch Gunicorn on port `6969`.
3. Multi-stage build the **React Admin portal** with Node.js and serve it through **Nginx** on ports `80` and `5173`.
4. Automatically initialize the database tables and seed default admin (`admin@roadsense.gov` / `12345678`) and sample road hazards.

---

## 🌐 Accessing the Running Services

Once started, access the application:

* **Admin Web Portal:** `http://localhost` (or `http://localhost:5173`)
  * **Admin Email:** `admin@roadsense.gov`
  * **Password:** `12345678`
* **Backend REST API:** `http://localhost:6969`
  * **Health Check:** `http://localhost:6969/api/health`
* **PostgreSQL Database:** `localhost:5432`
  * **Username:** `roadsense_admin`
  * **Password:** `roadsense_secret_pass_2026`
  * **Database:** `roadsensedb`
* **Mobile Client (Flutter):**
  * Set `AuthService.url = "http://<YOUR_LAN_IP>:6969"` in `lib/frontend/auth.dart`.

---

## 🛠️ Useful Docker Commands

```bash
# View real-time logs from all containers
docker compose logs -f

# View logs from a specific service (e.g. backend)
docker compose logs -f backend

# Check status of running containers
docker compose ps

# Restart a specific service
docker compose restart backend

# Stop all containers (keeps persistent database data)
docker compose down

# Stop and wipe database volume completely (fresh start)
docker compose down -v
```

---

## ☁️ Deploying with Docker on AWS EC2

If you prefer to deploy using Docker on your AWS EC2 Ubuntu instance instead of standard systemd:

1. **SSH into your EC2 instance:**
   ```bash
   ssh -i "your-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
   ```

2. **Install Docker on Ubuntu:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose-v2
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Clone your repository and launch:**
   ```bash
   git clone https://github.com/<YOUR_GITHUB_USERNAME>/RoadSense.git
   cd RoadSense
   docker compose up --build -d
   ```

4. Open your browser and navigate to `http://<YOUR_EC2_PUBLIC_IP>`. Your full-stack RoadSense dashboard is live!
