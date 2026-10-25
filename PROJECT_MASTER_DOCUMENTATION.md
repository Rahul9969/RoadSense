# RoadSense: Complete Project Master Specification & Technical Documentation

**System Title:** RoadSense — Cloud-Native Civic Road Hazard Intelligence & Infrastructure Platform  
**Target Environment:** Amazon Web Services (AWS Primary Region: `us-east-1`, N. Virginia)  
**Production AWS Account ID:** `464817648755`  
**Production Elastic IP:** `44.215.69.114` (Ubuntu 24.04 LTS, Nginx, Gunicorn WSGI)  
**Repository Branch:** `main` (https://github.com/Rahul9969/RoadSense)  
**Documentation Version:** 3.0.0 (Production Release)

---

## Table of Contents

1. [Executive Summary & Problem Statement](#1-executive-summary--problem-statement)
2. [High-Level System Architecture & 3-Tier Topology](#2-high-level-system-architecture--3-tier-topology)
3. [Edge Mobile Client Layer (Flutter Android)](#3-edge-mobile-client-layer-flutter-android)
4. [Ingress & Web Compute Layer (Nginx, Gunicorn, Flask REST API)](#4-ingress--web-compute-layer-nginx-gunicorn-flask-rest-api)
5. [AI Computer Vision & Defect Detection Pipeline](#5-ai-computer-vision--defect-detection-pipeline)
6. [AWS Serverless Queuing, Event Processing & DLQ (SQS & Lambda)](#6-aws-serverless-queuing-event-processing--dlq-sqs--lambda)
7. [Emergency Notification & Fan-Out Alerting (Amazon SNS)](#7-emergency-notification--fan-out-alerting-amazon-sns)
8. [Scalable Asset Storage & Media Management (Amazon S3)](#8-scalable-asset-storage--media-management-amazon-s3)
9. [Database Schema & Spatial Persistence (PostgreSQL & PostGIS)](#9-database-schema--spatial-persistence-postgresql--postgis)
10. [Municipal Decision Support Dashboard (React 18 / Vite / TypeScript)](#10-municipal-decision-support-dashboard-react-18--vite--typescript)
11. [ASTM D6433 Pavement Analytics & Civil Engineering Math](#11-astm-d6433-pavement-analytics--civil-engineering-math)
12. [Cloud Security, IAM Policies & Access Control](#12-cloud-security-iam-policies--access-control)
13. [Observability, Monitoring & Alarms (Amazon CloudWatch & SSM)](#13-observability-monitoring--alarms-amazon-cloudwatch--ssm)
14. [Complete REST API Specification](#14-complete-rest-api-specification)
15. [Verification, Testing & Live Demonstration Runbook](#15-verification-testing--live-demonstration-runbook)
16. [Complete Codebase Directory Inventory](#16-complete-codebase-directory-inventory)
17. [Local Setup, Dockerization & Cloud Deployment Guide](#17-local-setup-dockerization--cloud-deployment-guide)

---

## 1. Executive Summary & Problem Statement

### 1.1 Context and Problem Formulation

Transportation infrastructure constitutes the physical backbone of municipal economies. Across developing and rapidly urbanizing regions, road surfaces experience rapid degradation due to intense monsoons, overloaded commercial transit, substandard asphalt paving, and delayed municipal repair cycles. Potholes, surface cracks, asphalt ravelling, and waterlogging annually cause:

- **Catastrophic Fatalities & Accidents:** Thousands of two-wheeler and four-wheeler vehicular collisions and rollover accidents.
- **Economic Attrition:** Millions of dollars lost in vehicular suspension damage, fuel inefficiency, and cargo transit delays.
- **Civic Governance Breakdowns:** Traditional grievance redressal mechanisms rely on bureaucratic, manual citizen forms without GPS precision or visual validation, resulting in spam, misclassification, and 4 to 8-week repair delays.

### 1.2 The RoadSense Solution

RoadSense bridges the divide between citizens and municipal authorities through a **cloud-native, event-driven civic tech platform**. It combines:

1. **Edge Telemetry Capture:** Citizens capture photos and GPS coordinates via a native Flutter mobile app.
2. **Multimodal AI Detection:** Google Gemini 2.5 Flash Vision API and local YOLOv8 neural networks classify defects and predict normalized 2D bounding boxes `[ymin, xmin, ymax, xmax]`.
3. **Decoupled Serverless Ingestion:** An Amazon SQS queue (`roadsense-prod-hazard-queue`) accepts citizen reports with sub-50ms latency, preventing web server bottlenecks during traffic spikes.
4. **Autonomous Cloud Triage:** An AWS Lambda serverless function (`RoadSenseHazardWorker`) calculates municipal priority scores (0–100), evaluates statutory SLA limits (24h/48h), and logs audit telemetry.
5. **Emergency Fan-Out Alerting:** Amazon SNS (`roadsense-prod-critical-alerts`) dispatches instant email and SMS notifications for high-severity hazards to road maintenance squads.
6. **Executive Decision Support:** A React 18 administrative portal calculates **ASTM D6433 Pavement Condition Index (PCI)**, estimates cold-mix asphalt repair tonnage, and projects municipal repair budgets.

---

## 2. High-Level System Architecture & 3-Tier Topology

The RoadSense infrastructure follows the **AWS Well-Architected Framework** across 3 distinct tiers:

```
+---------------------------------------------------------------------------------------------------+
|                                 1. EDGE CLIENTS & TELEMETRY TIER                                  |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  |    Citizen Mobile App     |  |  Municipal Admin Portal   |  |       AI Vision Engine        |  |
|  |      Flutter (Android)    |  |     React 18 / TS / Vite  |  |    Gemini 2.5 Flash / YOLO    |  |
|  |     Camera + GPS Sensor   |  |   Analytics, Map, SLAs    |  |   Detects & Bounding Boxes    |  |
|  +-------------+-------------+  +-------------+-------------+  +---------------+---------------+  |
+----------------|------------------------------|--------------------------------|------------------+
                 | HTTPS /api/infer             | HTTPS /api/admin               | Image Inspection
                 v                              v                                v
+---------------------------------------------------------------------------------------------------+
|                               2. AWS VPC (10.0.0.0/16) - US-EAST-1                                |
|  PUBLIC SUBNET (10.0.1.0/24)                                                                      |
|  +---------------------------------------------------------------------------------------------+  |
|  | Internet Gateway (IGW) -> Elastic IP: 44.215.69.114                                          |  |
|  | Amazon EC2 Ingress (Ubuntu 24.04 LTS, Nginx Reverse Proxy, Gunicorn WSGI, Flask API)        |  |
|  |   * AWS Systems Manager (SSM) Parameter Store (/roadsense/prod/* - Zero Hardcoding)         |  |
|  |   * AWS CloudWatch Agent (System Metrics, Nginx Access Logs, Alarm: roadsense-prod-high-cpu)|  |
|  +------------------------------+--------------------------------------------------------------+  |
|                                 | Enqueue Hazard Event                                            |
|  PRIVATE SUBNET (10.0.2.0/24)   |                                                                 |
|  +------------------------------v--------------------------------------------------------------+  |
|  | Amazon RDS PostgreSQL 16 + PostGIS Spatial Database (Multi-AZ High Availability)             |  |
|  +---------------------------------------------------------------------------------------------+  |
+---------------------------------|-----------------------------------------------------------------+
                                  |
+---------------------------------v-----------------------------------------------------------------+
|                              3. AWS MANAGED SERVERLESS & STORAGE                                  |
|  +---------------------------------------------------------------------------------------------+  |
|  | Amazon SQS Queue: roadsense-prod-hazard-queue                                               |  |
|  |   - Standard SQS, 60s Visibility Timeout, 4-Day Retention, Resource Access Policy Active   |  |
|  +------------------------------+--------------------------------------------------------------+  |
|                                 |                                  | Redrive Policy (attempts > 3)|
|                                 | Batch Trigger (10 msgs)          v                              |
|                                 |                     +----------------------------------------+  |
|                                 |                     | SQS Dead-Letter Queue (DLQ):           |  |
|                                 |                     | roadsense-prod-hazard-dlq              |  |
|                                 |                     | 14-Day Retention, Poison-Pill Sandbox  |  |
|                                 |                     +----------------------------------------+  |
|                                 v                                                                 |
|  +---------------------------------------------------------------------------------------------+  |
|  | AWS Lambda Worker: RoadSenseHazardWorker (Python 3.11, Role: roadsense-prod-lambda-role)    |  |
|  |   - Parses JSON, computes Triage Score (0-100), checks 24h SLA, generates CloudWatch audit  |  |
|  +------------------------------+-------------------------------+------------------------------+  |
|                                 |                               |                                 |
|                                 v Store Image (AES-256)         v Critical Alert (Severity High)  |
|  +--------------------------------------------+  +---------------------------------------------+  |
|  | Amazon S3 Asset Store:                     |  | Amazon SNS Alert Router:                    |  |
|  | roadsense-hazards-464817648755-us-east-1   |  | arn:aws:sns:us-east-1:464817648755:        |  |
|  | Public Read / Private Upload, CORS Enabled |  | roadsense-prod-critical-alerts              |  |
|  | Evidence Photos: /hazards/*.jpg            |  | Confirmed Subscriber:                       |  |
|  |                                            |  | rahulkewat9768@gmail.com (Email/SMS)        |  |
|  +--------------------------------------------+  +---------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Edge Mobile Client Layer (Flutter Android)

### 3.1 Technology Stack & Architecture

- **Framework:** Flutter SDK 3.x (Dart 3.x) targeting Android API Level 34 (Android 14) with backward compatibility to API Level 24 (Android 7.0).
- **Physical Verification Device:** OnePlus Nord (Model: `AC2001`, Android 12, OxygenOS).
- **Key Modules in `lib/frontend/`:**
  - `citizen.dart`: Citizen camera viewfinder, live geolocation telemetry polling, report submission form, and personal history tracking.
  - `admin.dart`: On-device lightweight administrative triage viewer for zone inspection officers.
  - `login.dart` & `signup.dart`: Citizen and administrator JWT authentication forms.
  - `forgot_password.dart`: Self-service credential recovery.

### 3.2 Mobile Sensor & Telemetry Acquisition

1. **Camera Stream:** Interfaced via `camera` and `image_picker` plugins. The camera controller captures JPEG images at $1920 \times 1080$ resolution.
2. **GPS Geolocation:** Utilizes `geolocator` plugin configured with `LocationAccuracy.high` and a 5-meter distance filter. Telemetry captures:
   - Latitude and Longitude (WGS-84 Decimal Degrees).
   - Altitude and Horizontal Accuracy ($\pm$ meters).
   - Device compass bearing heading.
3. **Payload Compression:** To ensure resilience over weak 3G/4G cellular connections, the client resizes images to a maximum dimension of 1080px and compresses JPEG quality to 80% before multipart upload, reducing network payload size from ~5MB to <400KB.

---

## 4. Ingress & Web Compute Layer (Nginx, Gunicorn, Flask REST API)

### 4.1 Server Environment & Host Architecture

- **EC2 Instance:** `t3.medium` running Ubuntu 24.04 LTS.
- **Elastic IP (EIP):** `44.215.69.114` associated with network interface `eni-0c7f1a3b8d9e`.
- **Process Manager:** `systemd` managing `roadsense-backend.service` running Gunicorn with 4 Gevent/sync workers on port `5000`.
- **Reverse Proxy:** Nginx 1.24 configured with:
  - Client request body limits (`client_max_body_size 25M;`).
  - Gzip compression for JSON payloads.
  - Reverse proxy buffering for upstream Gunicorn.
  - HTTPS SSL/TLS termination.

### 4.2 Application Code Architecture (`lib/backend/`)

- `backend_main.py`: Application entrypoint, CORS configuration, SQLite/PostgreSQL database initialization, and default administrator account seeding (`admin@roadsense.gov`).
- `auth.py`: JWT token generation, SHA-256 password hashing via Werkzeug, and `@token_required` decorator for endpoint security.
- `models.py`: SQLAlchemy ORM definitions for `User` and `IssueReport`.
- `inference.py`: API blueprints for `/api/infer`, `/api/citizenreport`, and `/api/health`.
- `aws_service.py`: AWS SDK (`boto3`) wrapper for S3 image uploads, SQS message queuing, SNS alert publishing, and SSM parameter resolution.
- `utils/model_runner.py`: Multimodal computer vision inference engine coordinating Gemini 2.5 Flash, YOLOv8, and heuristic fallback detectors.

---

## 5. AI Computer Vision & Defect Detection Pipeline

RoadSense implements a **tri-tier fallback detection pipeline** in `lib/backend/utils/model_runner.py`:

```
               +--------------------------------------+
               | Raw Roadway Image (JPEG/PNG Buffer)  |
               +------------------+-------------------+
                                  |
                                  v
             [ Tier 1: Google Gemini 2.5 Flash Vision ]
                                  |
                     Is API Key Valid & Online?
                     /                        \
                   YES                         NO
                   /                             \
     +---------------------------+   +-------------------------------+
     | Gemini Multimodal Analysis|   | [ Tier 2: Local YOLOv8 Engine]|
     | - Normalized Bounding Box |   | - best_for_potholes.pt        |
     | - Defect Classification   |   | - best_for_garbage.pt         |
     | - Criticality Rating      |   +---------------+---------------+
     +-------------+-------------+                   |
                   |                    Are Model Weights Present?
                   |                    /                         \
                   |                  YES                          NO
                   |                  /                              \
                   |   +--------------------------+  +--------------------------+
                   |   | PyTorch YOLOv8 Inference |  | [ Tier 3: Smart CV Engine]|
                   |   | Dark depression & cavity |  | Edge detection, contour  |
                   |   | bounding box estimation  |  | analysis, darkness ratio |
                   |   +------------+-------------+  +------------+-------------+
                   |                |                             |
                   v                v                             v
           +---------------------------------------------------------------+
           | Standardized InferenceResult Object:                         |
           | (annotated_image, confidence: 0.94, label: "Potholes",       |
           |  severity: "critical", bbox: [ymin, xmin, ymax, xmax])       |
           +---------------------------------------------------------------+
```

### 5.1 Tier 1: Google Gemini 2.5 Flash Vision API

When `GEMINI_API_KEY` is present, the image is scaled to 720px max dimension, base64 encoded, and transmitted over HTTPS to:
`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`

**Prompt Specification:**

```text
You are RoadSense AI, an expert civil engineering and municipal road hazard detection system.
Analyze this roadway/civic image carefully to detect road defects and damage.
Identify whether there are Potholes, Waterlogging, Damaged Road (cracks/fissures), Broken Streetlight, or Garbage.
If there is any dark hole, cavity, depression, or crater in the asphalt/concrete, label it as 'Potholes'.
Respond ONLY with a JSON object in this exact schema:
{
  "hazard_detected": true,
  "label": "Potholes" | "Waterlogging" | "Damaged Road" | "Broken Streetlight" | "Garbage",
  "confidence": 0.95,
  "criticality": "Critical" | "High" | "Medium" | "Low",
  "box_2d": [ymin, xmin, ymax, xmax],
  "reasoning": "Detailed assessment of the hazard and risk to vehicles"
}
```

### 5.2 Tier 2: Local Ultralytics YOLOv8 Weights

When running in offline or edge-server environments, RoadSense loads pre-trained PyTorch weights:

- `lib/backend/utils/models/best_for_potholes.pt`
- `lib/backend/utils/models/best_for_garbage.pt`
  Bounding box predictions with confidence $>0.40$ are projected onto the output image using OpenCV/PIL with high-contrast safety borders.

### 5.3 Tier 3: Deterministic Smart Computer Vision (Fallback)

If external APIs and heavy weights are uninitialized, a deterministic OpenCV fallback inspects grayscale pixel luminance histograms, Sobel gradient edges, and bounding contour darkness ratios. Dark depression regions surrounded by asphalt road textures are categorized as potholes, ensuring the system **never fails silently**.

---

## 6. AWS Serverless Queuing, Event Processing & DLQ (SQS & Lambda)

### 6.1 Primary Ingestion Queue (`roadsense-prod-hazard-queue`)

- **Queue Type:** Standard SQS Queue.
- **Queue ARN:** `arn:aws:sqs:us-east-1:464817648755:roadsense-prod-hazard-queue`
- **Visibility Timeout:** `60 seconds` (provides sufficient headroom for Lambda processing).
- **Message Retention:** `345,600 seconds` (4 days).
- **Delivery Delay:** `0 seconds`.
- **Receive Message Wait Time:** `0 seconds` (short polling for batch trigger).

### 6.2 Dead-Letter Queue (`roadsense-prod-hazard-dlq`)

- **Queue ARN:** `arn:aws:sqs:us-east-1:464817648755:roadsense-prod-hazard-dlq`
- **Purpose:** Captures corrupted JSON payloads, malformed image URLs, or unhandled exceptions that fail Lambda processing.
- **Retention Period:** `1,209,600 seconds` (14 days — maximum AWS durability for post-mortem forensics).
- **Redrive Policy on Main Queue:**
  ```json
  {
    "deadLetterTargetArn": "arn:aws:sqs:us-east-1:464817648755:roadsense-prod-hazard-dlq",
    "maxReceiveCount": 3
  }
  ```
- **Redrive Allow Policy on DLQ:**
  ```json
  {
    "redrivePermission": "byQueue",
    "sourceQueueArns": [
      "arn:aws:sqs:us-east-1:464817648755:roadsense-prod-hazard-queue"
    ]
  }
  ```

### 6.3 Serverless Worker (`RoadSenseHazardWorker`)

- **Runtime:** Python 3.11 (Serverless Lambda).
- **Handler:** `lambda_function.lambda_handler`.
- **Execution Role:** `arn:aws:iam::464817648755:role/roadsense-prod-lambda-role`.
- **Memory Allocation:** 256 MB.
- **Timeout:** 30 seconds.
- **SQS Event Source Mapping:**
  - UUID: `cbaee3f5-95b2-4470-b6c9-65595c0ca02c`
  - State: `Enabled`
  - Batch Size: `10 records`

#### Municipal Triage Scoring Algorithm:

$$\text{Score} = \text{BaseScore}(\text{Severity}) + \text{TypeWeight}(\text{Label})$$

Where:

- $\text{BaseScore}(\text{Critical}) = 90$
- $\text{BaseScore}(\text{High}) = 75$
- $\text{BaseScore}(\text{Medium}) = 50$
- $\text{BaseScore}(\text{Low}) = 25$
- $\text{TypeWeight}(\text{Potholes}) = +10$
- $\text{TypeWeight}(\text{Waterlogging}) = +10$
- $\text{TypeWeight}(\text{Damaged Road}) = +5$
- $\text{TypeWeight}(\text{Broken Streetlight}) = 0$
- $\text{TypeWeight}(\text{Garbage}) = -5$

$$\text{Final Triage Score} = \min(100, \max(10, \text{Score}))$$

---

## 7. Emergency Notification & Fan-Out Alerting (Amazon SNS)

### 7.1 Topic Configuration

- **Topic Name:** `roadsense-prod-critical-alerts`
- **Topic ARN:** `arn:aws:sns:us-east-1:464817648755:roadsense-prod-critical-alerts`
- **Display Name:** `RoadSense Alert`
- **Active Subscriptions:** Confirmed email endpoint `rahulkewat9768@gmail.com`.

### 7.2 Trigger Condition

Triggered automatically whenever `severity` is evaluated as `'critical'` or `'high'`.

### 7.3 Dispatched Alert Format

```text
ROADSENSE MUNICIPAL RAPID RESPONSE ALERT
=========================================
Report ID: #9001
Hazard Type: Potholes
Severity: CRITICAL
Priority Score: 100/100
GPS Location: https://maps.google.com/?q=27.6194,85.5388
Reported By: citizen_rahul
Timestamp: 2026-10-26T00:05:00Z
Evidence Photo: https://roadsense-hazards-464817648755-us-east-1.s3.amazonaws.com/hazards/pothole_9001.jpg
Required Action: Municipal crew dispatch within 24 hours.
```

---

## 8. Scalable Asset Storage & Media Management (Amazon S3)

### 8.1 S3 Bucket Details

- **Bucket Name:** `roadsense-hazards-464817648755-us-east-1`
- **Region:** `us-east-1`
- **Default Encryption:** Server-Side Encryption with Amazon S3 Managed Keys (`SSE-S3`, AES-256).
- **Public Access Configuration:** `BlockPublicAcls = false`, bucket policy authorizes `s3:GetObject` for public CDN viewing of evidence photos.
- **Key Prefix Architecture:** `hazards/YYYY-MM-DD/report_{id}_{uuid}.jpg`.

### 8.2 CORS Configuration

```xml
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>HEAD</AllowedMethod>
        <AllowedHeader>*</AllowedHeader>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
    </CORSRule>
</CORSConfiguration>
```

---

## 9. Database Schema & Spatial Persistence (PostgreSQL & PostGIS)

### 9.1 Data Model: `issue_reports`

Mapped via SQLAlchemy in `lib/backend/models.py`:

| Column Name        | Data Type                        | Constraints                     | Description                                                   |
| :----------------- | :------------------------------- | :------------------------------ | :------------------------------------------------------------ |
| `issue_id`         | `INTEGER`                        | Primary Key, Auto-increment     | Unique incident identifier.                                   |
| `username`         | `VARCHAR(80)`                    | NOT NULL                        | Username of reporting citizen.                                |
| `location`         | `JSON` / `GEOMETRY(Point, 4326)` | NOT NULL                        | WGS-84 coordinates: `{"lat": 27.6194, "lng": 85.5388}`.       |
| `image_url`        | `VARCHAR(500)`                   | Nullable                        | Canonical Amazon S3 media URL.                                |
| `segmented_image`  | `TEXT`                           | Nullable                        | Base64-encoded defect annotation.                             |
| `confidence_score` | `FLOAT`                          | Default: `0.85`                 | AI model detection confidence (0.0 to 1.0).                   |
| `status`           | `VARCHAR(30)`                    | Default: `'reported'`           | Status: `reported`, `deployed`, `underprocessed`, `resolved`. |
| `severity`         | `VARCHAR(20)`                    | Default: `'medium'`             | Severity: `low`, `medium`, `critical`.                        |
| `description`      | `TEXT`                           | Nullable                        | Citizen textual commentary.                                   |
| `label`            | `VARCHAR(200)`                   | NOT NULL, Default: `'Potholes'` | Classification label.                                         |
| `created_at`       | `TIMESTAMP`                      | Default: `NOW()`                | UTC ingestion timestamp.                                      |

### 9.2 Data Model: `users`

Mapped via SQLAlchemy in `lib/backend/auth.py`:

| Column Name        | Data Type      | Constraints                 | Description                     |
| :----------------- | :------------- | :-------------------------- | :------------------------------ |
| `id`               | `INTEGER`      | Primary Key, Auto-increment | User identifier.                |
| `username`         | `VARCHAR(80)`  | Unique, NOT NULL            | Account login handle.           |
| `email`            | `VARCHAR(120)` | Unique, NOT NULL            | Citizen / Admin email.          |
| `password_hash`    | `VARCHAR(256)` | NOT NULL                    | Scrypt / PBKDF2 hashed secret.  |
| `is_administrator` | `BOOLEAN`      | Default: `FALSE`            | Role-Based Access Control flag. |

---

## 10. Municipal Decision Support Dashboard (React 18 / Vite / TypeScript)

### 10.1 UI/UX Architecture (`web-admin/src/`)

- **Framework:** React 18 with TypeScript 5.x and Vite 5.x bundler.
- **Styling:** Tailwind CSS with custom glassmorphism panels and responsive grid layouts.
- **Interactive Mapping:** Leaflet / OpenStreetMap displaying color-coded incident clusters (Red: Critical, Orange: High, Yellow: Medium, Green: Resolved).
- **Analytical Charts:** Recharts library visualizing 30-day incident frequency, defect distributions, and municipal zone compliance rates.

### 10.2 Core Dashboard Views

1. **Live Incident Command Center:** Real-time table of active reports with live status toggling (`Reported` $\rightarrow$ `Work Order Deployed` $\rightarrow$ `Resolved`).
2. **Geospatial Heatmap:** Kernel density estimation (KDE) highlighting high-risk roadway corridors.
3. **Pavement Analytics Center:** ASTM D6433 PCI ratings, cold-mix asphalt volume forecasting, and statutory SLA countdown timers.

---

## 11. ASTM D6433 Pavement Analytics & Civil Engineering Math

RoadSense incorporates real-world civil engineering standards to bridge software reporting with municipal procurement:

### 11.1 Pavement Condition Index (ASTM D6433)

The Pavement Condition Index (PCI) is a numerical rating between 0 and 100:

$$\text{PCI} = 100 - \sum_{i=1}^{p} \text{DeductValue}(T_i, S_i, D_i)$$

Where:

- $T_i$ = Defect distress type (Potholes, Cracking, Ravelling).
- $S_i$ = Severity weighting factor ($\text{Critical} = 3.5, \text{High} = 2.5, \text{Medium} = 1.5, \text{Low} = 0.8$).
- $D_i$ = Density of distress per 100 linear meters of roadway corridor.

**PCI Operational Scale:**

- **85 – 100 (Good):** Routine maintenance / Crack sealing.
- **55 – 84 (Fair):** Preventative micro-surfacing / Patching.
- **25 – 54 (Poor):** Asphalt structural overlay.
- **0 – 24 (Failed):** Full-depth reclamation & roadway reconstruction.

### 11.2 Automated Asphalt Tonnage & Budget Estimation

When a pothole is classified by the AI vision model, the system calculates required cold-mix asphalt patch material:

$$\text{Volume } (V) = \text{Estimated Area } (A) \times \text{Average Depth } (d)$$
$$\text{Mass (Tonnage)} = V \times \rho_{\text{asphalt}}$$

Where:

- $\text{Estimated Area} = \text{BBox Width} \times \text{BBox Height} \times k_{\text{ellipse}} \approx 0.15 \text{ m}^2 \text{ (avg)}$.
- $\text{Average Depth } (d) = 0.08 \text{ m (8 cm)}$.
- $\rho_{\text{asphalt}} = 2.4 \text{ metric tonnes/m}^3$ (standard compacted hot/cold mix density).
- $\text{Estimated Patch Weight} \approx 0.15 \times 0.08 \times 2.4 \approx 0.0288 \text{ tonnes (28.8 kg per pothole)}$.

**Budget Cost Forecasting:**
$$\text{Repair Cost} = (\text{Tonnage} \times \$120/\text{tonne}) + \text{Labor Allocation (\$45/patch)} + \text{Traffic Control Allocation (\$30)}$$

---

## 12. Cloud Security, IAM Policies & Access Control

### 12.1 SQS Resource-Based Access Policy (`aws/sqs_access_policy.json`)

Applied live to `roadsense-prod-hazard-queue`:

```json
{
  "Version": "2012-10-17",
  "Id": "RoadSenseProdHazardQueuePolicy",
  "Statement": [
    {
      "Sid": "AllowEC2AndLambdaQueueAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::464817648755:role/roadsense-prod-ec2-role",
          "arn:aws:iam::464817648755:role/roadsense-prod-lambda-role"
        ]
      },
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:us-east-1:464817648755:roadsense-prod-hazard-queue"
    },
    {
      "Sid": "AllowSNSToPublishToQueue",
      "Effect": "Allow",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:464817648755:roadsense-prod-hazard-queue"
    }
  ]
}
```

### 12.2 IAM Execution Roles

1. **`roadsense-prod-ec2-role`:**
   - `s3:PutObject`, `s3:GetObject` on `roadsense-hazards-*`.
   - `sqs:SendMessage` on `roadsense-prod-hazard-queue`.
   - `ssm:GetParameter`, `ssm:GetParametersByPath` on `/roadsense/*`.
   - `cloudwatch:PutMetricData`.
2. **`roadsense-prod-lambda-role`:**
   - `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` on `roadsense-prod-hazard-queue`.
   - `sqs:SendMessage` on `roadsense-prod-hazard-dlq`.
   - `sns:Publish` on `roadsense-prod-critical-alerts`.
   - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` on `/aws/lambda/RoadSenseHazardWorker`.

---

## 13. Observability, Monitoring & Alarms (Amazon CloudWatch & SSM)

### 13.1 CloudWatch High-CPU Alarm

- **Alarm Name:** `roadsense-prod-high-cpu-alarm`
- **Metric:** `AWS/EC2 -> CPUUtilization`
- **Threshold:** $\ge 75\%$ for 2 consecutive 5-minute evaluation periods.
- **Action:** Publishes alarm state notification to `roadsense-prod-critical-alerts`.

### 13.2 AWS CloudWatch Dashboard

- **Dashboard Name:** `RoadSense-Production-Dashboard`
- **Configured Widgets:**
  1. EC2 CPU Utilization & Network In/Out.
  2. SQS Visible Message Depth (`ApproximateNumberOfMessagesVisible`).
  3. SQS Age of Oldest Message (`ApproximateAgeOfOldestMessage`).
  4. Lambda Invocation Count, Duration, and Error Rate.
  5. SNS Dispatched Message Count.

### 13.3 Systems Manager (SSM) Parameter Store

All operational secrets are stored as encrypted SecureString / String parameters in AWS Systems Manager:

- `/roadsense/db_host` $\rightarrow$ Database hostname.
- `/roadsense/db_name` $\rightarrow$ `roadsense_prod`.
- `/roadsense/db_user` $\rightarrow$ Master DB role.
- `/roadsense/s3_bucket` $\rightarrow$ `roadsense-hazards-464817648755-us-east-1`.
- `/roadsense/sqs_queue_url` $\rightarrow$ `https://sqs.us-east-1.amazonaws.com/464817648755/roadsense-prod-hazard-queue`.
- `/roadsense/sns_topic_arn` $\rightarrow$ `arn:aws:sns:us-east-1:464817648755:roadsense-prod-critical-alerts`.

---

## 14. Complete REST API Specification

| HTTP Method | Route                     | Auth Required | Description                                    | Request Payload                     | Response Code             |
| :---------- | :------------------------ | :------------ | :--------------------------------------------- | :---------------------------------- | :------------------------ |
| `GET`       | `/api/health`             | No            | Target group & instance health check           | None                                | `200 OK`                  |
| `POST`      | `/auth/register`          | No            | Citizen account registration                   | `{"username", "email", "password"}` | `201 Created`             |
| `POST`      | `/auth/login`             | No            | User authentication                            | `{"email", "password"}`             | `200 OK` (`token`)        |
| `POST`      | `/api/infer`              | Yes (JWT)     | Hazard ingestion, AI inference & SQS enqueuing | Multipart / JSON Base64 + GPS       | `200 OK` / `202 Accepted` |
| `GET`       | `/api/citizenreport`      | Yes (JWT)     | Citizen's submitted report history             | Query param `username`              | `200 OK`                  |
| `GET`       | `/api/admin/reports`      | Yes (Admin)   | Comprehensive municipal incident list          | Filters: `severity`, `status`       | `200 OK`                  |
| `PATCH`     | `/api/admin/reports/<id>` | Yes (Admin)   | Updates incident status                        | `{"status": "deployed"}`            | `200 OK`                  |
| `GET`       | `/api/admin/stats`        | Yes (Admin)   | PCI index, counts, budget forecasts            | None                                | `200 OK`                  |

---

## 15. Verification, Testing & Live Demonstration Runbook

### 15.1 Automated Cloud Audit Command

Execute the automated live audit script from the repository root:

```bash
python aws/audit_aws.py
```

**Expected Output:**

- `✅ [S3] Bucket exists & reachable: roadsense-hazards-464817648755-us-east-1`
- `✅ [SQS] Queue: roadsense-prod-hazard-queue | Policy: True | RedrivePolicy: True`
- `✅ [SQS] Queue: roadsense-prod-hazard-dlq | Policy: True | RedrivePolicy: False`
- `✅ [SNS] Topic exists: arn:aws:sns:us-east-1:464817648755:roadsense-prod-critical-alerts (Subscriptions: 1)`
- `✅ [LAMBDA] RoadSenseHazardWorker | State: Active | Role: roadsense-prod-lambda-role`
- `   -> SQS EventSource: roadsense-prod-hazard-queue | State: Enabled`
- `✅ [SSM] Managed Parameters: 6 registered`
- `✅ [CloudWatch Alarm] roadsense-prod-high-cpu-alarm: 1 found (State: OK)`
- `✅ [CloudWatch Dashboard] RoadSense-Production-Dashboard: Active & Configured`

### 15.2 SQS Manual Test Payload

To test the live end-to-end serverless flow:

1. Navigate to **Amazon SQS > Queues > `roadsense-prod-hazard-queue` > Send and receive messages**.
2. Paste the test payload:
   ```json
   {
     "report_id": 9001,
     "label": "Potholes",
     "severity": "critical",
     "username": "rahulkewat",
     "location": { "lat": 27.6194, "lng": 85.5388 },
     "image_url": "https://roadsense-hazards-464817648755-us-east-1.s3.amazonaws.com/hazards/test_pothole_9001.jpg",
     "timestamp": "2026-10-26T00:05:00Z"
   }
   ```
3. Click **Send message**.
4. Check **CloudWatch Logs** under `/aws/lambda/RoadSenseHazardWorker` to view triage score calculation (`100/100`) and SNS alert dispatch.
5. Check `rahulkewat9768@gmail.com` inbox for the automated email alert.

---

## 16. Complete Codebase Directory Inventory

```
ChitraDartaa-A-Civic-Issue-Reporting-System/
├── aws/
│   ├── audit_aws.py                  # Automated live AWS verification script
│   ├── deploy_lambda.py              # Serverless Lambda packager and trigger mapper
│   ├── lambda_function.py            # Lambda serverless triage worker code
│   ├── roadsense-cloudformation.yaml # Infrastructure as Code (10 CloudFormation Stacks)
│   └── sqs_access_policy.json        # Resource-based queue authorization policy
├── docs/
│   ├── build_full_report.py          # Word document report compiler (1032 lines)
│   ├── generate_report_helpers.py    # Report styling and table helper functions
│   └── report_assets/                # Visual diagrams and benchmark evidence figures
├── lib/
│   ├── backend/
│   │   ├── admin_endpoint.py         # Municipal admin REST API blueprint
│   │   ├── auth.py                   # JWT user & administrator authentication
│   │   ├── aws_service.py            # Boto3 integration (S3, SQS, SNS, SSM)
│   │   ├── backend_main.py           # Flask application entrypoint & DB seed
│   │   ├── extension.py              # SQLAlchemy database instance
│   │   ├── inference.py              # Core image inference & reporting routes
│   │   ├── models.py                 # SQLAlchemy IssueReport data model
│   │   ├── requirements.txt          # Python pip dependencies
│   │   └── utils/
│   │       ├── image_utils.py        # Base64/PIL image encoding utilities
│   │       ├── model_runner.py       # Gemini 2.5 Flash / YOLOv8 / CV engine
│   │       └── setup_aws_lambda.py   # Lambda setup script
│   └── frontend/
│       ├── admin.dart                # Mobile admin inspection interface
│       ├── auth.dart                 # Flutter authentication service
│       ├── citizen.dart              # Citizen reporting screen & camera/GPS handler
│       ├── forgot_password.dart      # Password recovery UI
│       ├── login.dart                # Citizen/Admin login UI
│       └── signup.dart               # Registration UI
├── web-admin/
│   ├── src/
│   │   ├── App.tsx                   # Main React 18 Admin Application
│   │   ├── components/               # Incident tables, charts, and maps
│   │   └── index.css                 # Tailwind CSS styles
│   ├── package.json                  # React 18 / TypeScript / Vite dependencies
│   └── vite.config.ts                # Vite frontend bundler config
├── docker-compose.yml                # Multi-container orchestration (EC2 / Web)
├── DOCKER_GUIDE.md                   # Containerization and execution guide
├── pubspec.yaml                      # Flutter dependencies and asset registrations
├── RoadSense_Cloud_Architecture_Report.docx # Comprehensive 2.15MB Technical Report
└── PROJECT_MASTER_DOCUMENTATION.md   # This Master Specification Document
```

---

## 17. Local Setup, Dockerization & Cloud Deployment Guide

### 17.1 Local Backend Execution

```bash
# 1. Navigate to backend directory
cd lib/backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # On Linux/macOS
.\venv\Scripts\activate        # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Flask Development Server
python backend_main.py
```

The server will bind to `http://127.0.0.1:5000`.

### 17.2 Local Web Admin Execution

```bash
# 1. Navigate to web-admin directory
cd web-admin

# 2. Install Node dependencies
npm install

# 3. Start Vite dev server
npm run dev
```

The dashboard will be accessible at `http://localhost:5173`.

### 17.3 Flutter Mobile Application Execution

```bash
# 1. Check connected physical device / emulator
flutter devices

# 2. Fetch packages
flutter pub get

# 3. Launch on physical Android phone (OnePlus Nord)
flutter run -d AC2001
```

### 17.4 Production Deployment on AWS EC2

```bash
# Connect to EC2 instance
ssh -i Roadsensekey.pem ubuntu@44.215.69.114

# Pull latest code
cd /home/ubuntu/RoadSense
git pull origin main

# Restart Gunicorn service
sudo systemctl restart roadsense-backend.service

# Verify service status
sudo systemctl status roadsense-backend.service
```

---

_Document compiled and verified against live AWS Account `464817648755` (us-east-1)._
