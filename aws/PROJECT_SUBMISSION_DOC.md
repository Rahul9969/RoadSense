# RoadSense: Cloud-Based Road Hazard Reporting & Management Platform

**Course:** Cloud Computing Project  
**Project Team / Authors:**  
- **Rahul Kewat**  
- **Stewin Mathias**  
- **Reeven Menezes**  

**Platform Architecture:** Full-Stack Hybrid (Flutter Mobile Client + React Admin Web Dashboard + Python Flask REST API on Amazon EC2 + Amazon RDS PostgreSQL + Amazon S3 + AWS SSM + Amazon SNS + Amazon SQS + Amazon CloudWatch)  

---

## 1. Executive Summary & Problem Statement

Potholes, road surface erosion, waterlogging, and broken streetlights cause fatal traffic accidents, severe vehicular damage, and heavy transit delays. Municipal authorities often lack real-time visibility into emerging road hazards and struggle to prioritize repair crews efficiently.

**RoadSense** resolves this civic crisis by providing a cloud-engineered hazard reporting and resolution platform:
1. **Citizens (Mobile App - Flutter):** Report potholes and hazards on-the-go with real-time GPS geolocation, photographic evidence, hazard category, and severity assessment.
2. **Authority Dashboard (Web App - React/TypeScript):** Institutional web portal enabling municipal road maintenance teams to monitor live hazard pins on an interactive OpenStreetMap, review high-resolution photographic evidence from Amazon S3, track AI confidence scores, filter by severity, and transition issue status (`Reported` ➔ `Crew Deployed` ➔ `Under Process` ➔ `Resolved`).
3. **Cloud Infrastructure (AWS):** Built with strict adherence to production-grade cloud principles, featuring custom VPC networking, managed relational database isolation, server-side parameter encryption, asynchronous task queues, automated email alerts for critical road hazards, and comprehensive metric alarms.

---

## 2. Cloud Architecture Diagram

```mermaid
graph TB
    subgraph Clients ["Client Applications"]
        CitizenMobile["📱 Citizen Mobile App (Flutter)<br/>Photo Capture & GPS Pinning"]
        AdminWeb["💻 Municipality Admin Portal (React)<br/>Interactive Map, Status Triage & Filters"]
    end

    subgraph AWSCloud ["AWS Cloud Infrastructure (Custom VPC: 10.0.0.0/16)"]
        IGW["🌐 Internet Gateway (IGW)"]

        subgraph PublicSubnet ["Public Subnet (10.0.1.0/24 - AZ-a)"]
            EC2["🖥️ Amazon EC2 Instance (t3.micro - Free Tier)<br/>- Nginx Reverse Proxy (Port 80)<br/>- Gunicorn + Flask REST API (Port 6969)<br/>- CloudWatch Unified Logs Agent<br/>- AWS SDK (boto3 via IAM Instance Profile)"]
        end

        subgraph PrivateSubnet ["Private Subnets (10.0.10.0/24 & 10.0.11.0/24)"]
            RDS[("🗄️ Amazon RDS PostgreSQL (db.t3.micro)<br/>- Isolated Subnet Group<br/>- Accessible ONLY from EC2 Security Group")]
        end

        subgraph AWSManaged ["AWS Managed Cloud Services"]
            S3["🪣 Amazon S3 Bucket<br/>roadsense-hazards-media<br/>Stores Original & Segmented Images"]
            SSM["🔑 AWS SSM Parameter Store<br/>- /roadsense/db_host<br/>- /roadsense/db_password<br/>- /roadsense/secret_key"]
            SQS["📨 Amazon SQS Queue<br/>roadsense-hazard-queue<br/>Async Hazard Ingestion & Deduplication"]
            SNS["📢 Amazon SNS Topic<br/>roadsense-critical-alerts<br/>Immediate Email Alerts for Severe Hazards"]
            CloudWatch["📊 Amazon CloudWatch<br/>- Metric Alarm: High CPU (>75%)<br/>- Log Group: /aws/ec2/roadsense"]
            Budgets["💰 AWS Budgets<br/>$5 Monthly Cap Alert @ 80% ($4)"]
            IAM["🛡️ AWS IAM Role<br/>Least-Privilege EC2 Instance Profile"]
        end
    end

    CitizenMobile -->|REST API / Hazard Upload| IGW
    AdminWeb -->|REST API / Status Updates| IGW
    IGW --> EC2

    EC2 -->|Query/Persist Records (Port 5432)| RDS
    EC2 -->|Upload Hazard Evidence| S3
    EC2 -->|Fetch Credentials on Boot| SSM
    EC2 -->|Publish Critical Hazard Event| SNS
    EC2 -->|Enqueue for Async Processing| SQS
    EC2 -->|Ship System & App Logs| CloudWatch
    IAM -.->|Grants Least-Privilege| EC2
    SNS -->|Email Notification| MunicipalCrew["👷 Emergency Road Maintenance Crew"]
    Budgets -.->|Cost Alert Email| Student["📧 Student / Faculty Admin"]
```

---

## 3. Cloud Services Justification Matrix

| Cloud Domain | AWS Service Used | Specific Functional Purpose in RoadSense | Academic Requirement Satisfied |
| :--- | :--- | :--- | :--- |
| **Compute** | **Amazon EC2** (`t3.micro`) | Runs Gunicorn WSGI and the Python Flask REST API backend behind Nginx reverse proxy. Meets the non-serverless requirement. | Core Compute (Non-serverless) |
| **Networking** | **Amazon VPC** | Custom isolated CIDR (`10.0.0.0/16`) with 2 public subnets (compute), 2 private subnets (database), Internet Gateway, and explicit Security Groups (`roadsense-ec2-sg`, `roadsense-rds-sg`). | Custom VPC & Network Isolation |
| **Database** | **Amazon RDS** (PostgreSQL) | Managed relational database engine storing users and hazard reports (`issue_reports`). Configured in private subnets with no public IP, accepting inbound connections strictly from EC2 security group. | Managed Database |
| **Storage** | **Amazon S3** | Durable object storage for raw hazard photographs, AI-segmented bounding box derivatives, and audit logs. Replaces fragile local disk storage. | Genuine Cloud Object Storage |
| **Security & IAM** | **AWS IAM** & **SSM Parameter Store** | Least-privilege IAM Role attached to EC2 instance profile. Sensitive database passwords, JWT secrets, and bucket names are retrieved from SSM Parameter Store. **Zero hardcoded credentials in source code**. | Security & Least-Privilege |
| **Monitoring** | **Amazon CloudWatch** | Unified logging agent stream from `/var/log/roadsense/` to `/aws/ec2/roadsense/`. Configured metric alarm on `CPUUtilization >= 75%` triggering alert notifications. | Monitoring, Logging & Alarms |
| **Cost Control** | **AWS Budgets** | Strict $5.00/month budget cap configured with threshold notifications at 80% ($4.00) to guarantee Free Tier compliance. | Budget & Cost Alert |
| **Additional Capability 1** | **Amazon SNS** | Publishes instant push notifications (via Email/SMS) to road crews when a "Critical" hazard (deep pothole, major flooding) is reported. | Additional Capability #1 |
| **Additional Capability 2** | **Amazon SQS** | Asynchronous decoupling queue (`roadsense-hazard-queue`) that buffers hazard submissions for background indexing and geospatial deduplication. | Additional Capability #2 |

---

## 4. Free Tier & Cost Analysis

| Service | Free Tier Monthly Allowance | RoadSense Project Usage | Net Monthly Cost |
| :--- | :--- | :--- | :--- |
| **Amazon EC2** | 750 hours/month of `t2.micro`/`t3.micro` | 1 instance running 720 hours | **$0.00** |
| **Amazon VPC** | Subnets, IGW, Route Tables, Security Groups are free | Custom VPC with IGW (NAT Gateway avoided) | **$0.00** |
| **Amazon RDS** | 750 hours/month of Single-AZ `db.t3.micro` + 20 GB storage | 1 Single-AZ PostgreSQL instance | **$0.00** |
| **Amazon S3** | 5 GB storage + 20,000 GET + 2,000 PUT requests | ~300 MB hazard photographs | **$0.00** |
| **AWS Systems Manager** | Standard parameter storage is free | 8 configuration parameters | **$0.00** |
| **AWS IAM** | Free | 1 Instance Profile + 1 Policy | **$0.00** |
| **Amazon CloudWatch** | 10 custom metrics, 5 GB log ingestion, 3 alarms | 1 Metric Alarm + 1 Log Group | **$0.00** |
| **Amazon SNS** | 1,000,000 publishes + 1,000 email deliveries | ~100 emergency alerts | **$0.00** |
| **Amazon SQS** | 1,000,000 standard requests | ~3,000 queue events | **$0.00** |
| **Total Estimated Cost** | — | — | **$0.00 / month** |

> [!TIP]
> **Faculty Defense Note on Cost Optimization:** We intentionally omitted a NAT Gateway (which costs ~$32.40/month) by hosting our EC2 compute instance in a public subnet with an Internet Gateway, while keeping our RDS database completely private in isolated subnets accessible only via EC2 security group rules. This demonstrates professional architectural cost-efficiency while keeping the project 100% Free Tier compliant.

---

## 5. How to Run Everything

### Step 1: Run the Backend Locally
```powershell
cd RoadSense
.\lib\backend\venv\Scripts\Activate.ps1
python lib\backend\backend_main.py
```
*Backend starts on `http://127.0.0.1:6969` (Health check at `http://127.0.0.1:6969/api/health`).*

### Step 2: Run the Admin Web Application
```powershell
cd RoadSense\web-admin
npm run dev
```
*Open `http://localhost:5173` in your browser.*
- **Admin Email:** `admin@roadsense.gov`
- **Password:** `12345678`
- Features active: Live OpenStreetMap with pins, image modals, status updater buttons (`Deploy`, `Process`, `Resolve`), stats counters, and search.

### Step 3: Run the Flutter Mobile App (Citizen)
```powershell
cd RoadSense
flutter pub get
flutter run -d chrome    # Or flutter run -d windows / android
```
*Log in as citizen or sign up, capture hazard photo, pin location, and submit.*

### Step 4: Deploy to AWS EC2 (Production Cloud)
1. **Provision Infrastructure:** Deploy `aws/roadsense-cloudformation.yaml` via AWS CloudFormation Console.
2. **Launch EC2 Instance:** Launch an Ubuntu 24.04 LTS instance inside `roadsense-public-subnet-1`, attaching the `roadsense-ec2-profile`.
3. **Execute Bootstrap:** SSH into the EC2 instance and run `bash aws/deploy_ec2.sh`.
