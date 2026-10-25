# RoadSense - Cloud-Based Road Hazard Reporting Platform

**RoadSense** is a comprehensive, production-ready civic infrastructure platform that allows citizens to report road hazards (potholes, waterlogging, damaged roads, broken streetlights) and provides municipal road authorities with a powerful administrative dashboard to monitor, triage, and resolve issues in real-time.

---

## 👥 Development Team
* **Rahul Kewat**
* **Stewin Mathias**
* **Reeven Menezes**

---

## 🚀 Key Features

* 📱 **Citizen Mobile App (Flutter):** Capture photos of road hazards, fetch real-time GPS coordinates, specify hazard category and severity, and submit reports.
* 💻 **Municipality Admin Portal (React / TypeScript):** Interactive OpenStreetMap with status-colored pins, real-time KPI metrics, high-res photo inspection from Amazon S3, and status management (`Reported` ➔ `Deployed` ➔ `Under Process` ➔ `Resolved`).
* ☁️ **AWS Cloud Architecture:**
  * **Compute:** Python Flask REST API running on **Amazon EC2** behind Gunicorn & Nginx.
  * **Networking:** Custom **Amazon VPC** with isolated public and private subnets, Internet Gateway, and strict Security Groups.
  * **Database:** Managed **Amazon RDS PostgreSQL** in private subnets with no public internet exposure.
  * **Storage:** **Amazon S3** for secure, durable cloud image storage.
  * **Security:** **AWS SSM Parameter Store** for database secrets & **IAM Roles** with least-privilege policies.
  * **Notifications & Queues:** **Amazon SNS** for critical hazard alerts & **Amazon SQS** for decoupled task ingestion.
  * **Observability:** **Amazon CloudWatch** metrics, centralized logs, and automated high CPU utilization alarms.

---

## 📁 Repository Structure

```
RoadSense/
├── lib/
│   ├── main.dart                  # Flutter mobile app entrypoint
│   ├── frontend/                  # Citizen & mobile reporting UI
│   │   ├── auth.dart              # Authentication & API client
│   │   ├── citizen.dart           # Hazard report submission screen
│   │   ├── login.dart             # Login interface
│   │   └── signup.dart            # Citizen registration
│   └── backend/                   # Python Flask REST API
│       ├── backend_main.py        # Flask application factory & database seeding
│       ├── aws_service.py         # AWS S3, SNS, SQS, and SSM integration
│       ├── models.py              # SQLAlchemy database models
│       ├── inference.py           # Hazard reporting & AI inference endpoints
│       ├── admin_endpoint.py      # Admin management REST APIs
│       ├── requirements.txt       # Python dependencies
│       └── Dockerfile             # Production container definition
├── web-admin/                     # React/TypeScript Vite Admin Web Dashboard
│   ├── src/
│   │   ├── components/            # MapSection, IssueCard, StatsCards, Header
│   │   ├── services/api.ts        # Backend API service
│   │   └── functions.ts           # Pure formatting and marker utilities
├── aws/                           # CloudFormation & EC2 Deployment Scripts
│   ├── roadsense-cloudformation.yaml # Full AWS IaC CloudFormation template
│   ├── nginx.conf                 # Production Nginx reverse proxy configuration
│   └── deploy_ec2.sh              # Automated EC2 Ubuntu bootstrap script
└── pubspec.yaml                   # Flutter dependencies
```

---

## 🛠️ Technologies Used

* **Mobile Client:** Flutter (Dart), `geolocator`, `flutter_map`, `latlong2`
* **Admin Web Portal:** React 19, TypeScript, Vite, Tailwind CSS, `react-leaflet`, `lucide-react`, `sonner`
* **Backend:** Python 3.12, Flask, Flask-SQLAlchemy, PyJWT, Pillow, Boto3 (AWS SDK)
* **Cloud Services:** Amazon EC2, Amazon VPC, Amazon RDS PostgreSQL, Amazon S3, AWS IAM, AWS SSM Parameter Store, Amazon CloudWatch, Amazon SNS, Amazon SQS

---

## 📦 Getting Started & Running Locally

### Option A: Run Full Stack with Docker (1-Command Quickstart) 🐳
```bash
docker compose up --build -d
```
* Launches PostgreSQL, Python Flask API on `:6969`, and React Admin Web on `:80` and `:5173`.
* Full details in [DOCKER_GUIDE.md](file:///d:/ChitraDartaa-A-Civic-Issue-Reporting-System/DOCKER_GUIDE.md).

### Option B: Run Locally Without Docker

#### 1. Run the Backend
```powershell
cd lib/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend_main.py
```
*Backend runs on `http://127.0.0.1:6969` (Health check at `/api/health`).*

#### 2. Run the Admin Web Portal
```powershell
cd web-admin
npm install
npm run dev
```
*Open `http://localhost:5173` in your browser.*
* **Default Administrator:** `admin@roadsense.gov`
* **Password:** `12345678`

### 3. Run the Citizen Mobile App
```powershell
flutter pub get
flutter run -d chrome    # Or flutter run -d windows / android
```

---

## ☁️ Deploying to AWS Cloud

1. Deploy the CloudFormation template `aws/roadsense-cloudformation.yaml` in the AWS Console.
2. Launch an EC2 Ubuntu 24.04 instance inside the created public subnet and attach the `roadsense-prod-ec2-role`.
3. SSH into the instance and run:
   ```bash
   git clone <YOUR_REPOSITORY_URL> /var/www/roadsense
   bash /var/www/roadsense/aws/deploy_ec2.sh
   ```
4. Access your live web admin dashboard at `http://<EC2_PUBLIC_IP>`.
