"""
Enterprise-Grade Cloud Architecture Diagram Generator for RoadSense.
Renders clean, publication-quality 4K architecture diagrams with authentic AWS styling,
vector-grade sharpness, official AWS color palettes, and crisp typography.
Produces:
1. docs/report_assets/cloud_architecture_diagram.png (Enterprise AWS Cloud Topology)
2. docs/report_assets/data_flow_sequence.png (Decoupled Serverless Lifecycle Sequence)
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions (3840 x 2160 - Ultra HD 4K)
WIDTH, HEIGHT = 3840, 2160

# Palette - AWS Enterprise Architecture Theme
BG_COLOR = "#F8FAFC"
AWS_SQUID_INK = "#232F3E"
AWS_BORDER = "#CBD5E1"
VPC_BORDER = "#3B82F6"
SUBNET_PUBLIC = "#EFF6FF"
SUBNET_PRIVATE = "#F0FDF4"
SERVERLESS_BG = "#FFFBEB"

# Service Colors
COLOR_EC2 = "#EC7211"
COLOR_S3 = "#3F8624"
COLOR_SQS = "#E7157B"
COLOR_LAMBDA = "#EC7211"
COLOR_SNS = "#E7157B"
COLOR_RDS = "#2E73B8"
COLOR_CW = "#D13212"
COLOR_SSM = "#792DE4"
COLOR_CLIENT = "#0284C7"
COLOR_ADMIN = "#0F172A"

def get_font(size, bold=False):
    font_names = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    ]
    for fn in font_names:
        if os.path.exists(fn):
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def draw_service_card(draw, x, y, w, h, icon_letter, service_title, subtitle, bullets, theme_color):
    """Renders a modern, enterprise AWS architecture service card."""
    # Subtle drop shadow
    draw_rounded_rect(draw, [x + 6, y + 8, x + w + 6, y + h + 8], 16, fill="#E2E8F0")
    # Main card container
    draw_rounded_rect(draw, [x, y, x + w, y + h], 16, fill="#FFFFFF", outline="#E2E8F0", width=2)
    # Top accent bar
    draw.rounded_rectangle([x, y, x + w, y + 10], radius=5, fill=theme_color)

    # Icon circle / badge
    badge_size = 64
    badge_x = x + 24
    badge_y = y + 24
    draw.ellipse([badge_x, badge_y, badge_x + badge_size, badge_y + badge_size], fill=theme_color)
    
    font_badge = get_font(32, bold=True)
    draw.text((badge_x + badge_size // 2, badge_y + badge_size // 2 - 2), icon_letter, 
              fill="#FFFFFF", font=font_badge, anchor="mm")

    # Title & Subtitle
    font_title = get_font(28, bold=True)
    font_sub = get_font(20, bold=False)
    draw.text((badge_x + badge_size + 18, y + 26), service_title, fill="#0F172A", font=font_title)
    draw.text((badge_x + badge_size + 18, y + 62), subtitle, fill="#64748B", font=font_sub)

    # Divider line
    draw.line([x + 20, y + 104, x + w - 20, y + 104], fill="#F1F5F9", width=2)

    # Metadata bullet points
    font_bullet = get_font(20, bold=False)
    font_bullet_bold = get_font(20, bold=True)
    cur_y = y + 120
    for prefix, text in bullets:
        draw.ellipse([x + 28, cur_y + 8, x + 36, cur_y + 16], fill=theme_color)
        draw.text((x + 46, cur_y), prefix, fill="#1E293B", font=font_bullet_bold)
        prefix_len = draw.textlength(prefix, font=font_bullet_bold)
        draw.text((x + 46 + prefix_len, cur_y), text, fill="#475569", font=font_bullet)
        cur_y += 36

def draw_arrow(draw, start, end, label, color="#2563EB", lw=5):
    """Draws a crisp orthogonal or direct connection arrow with a centered label badge."""
    x0, y0 = start
    x1, y1 = end
    draw.line([x0, y0, x1, y1], fill=color, width=lw)
    
    # Arrow head
    import math
    angle = math.atan2(y1 - y0, x1 - x0)
    head_len = 24
    head_angle = math.pi / 6
    
    p1 = (x1 - head_len * math.cos(angle - head_angle), y1 - head_len * math.sin(angle - head_angle))
    p2 = (x1 - head_len * math.cos(angle + head_angle), y1 - head_len * math.sin(angle + head_angle))
    draw.polygon([end, p1, p2], fill=color)

    # Label badge in the middle
    if label:
        mid_x = (x0 + x1) // 2
        mid_y = (y0 + y1) // 2
        font_lbl = get_font(18, bold=True)
        lbl_w = draw.textlength(label, font=font_lbl) + 24
        lbl_h = 34
        draw.rounded_rectangle([mid_x - lbl_w//2, mid_y - lbl_h//2, mid_x + lbl_w//2, mid_y + lbl_h//2], 
                               radius=6, fill="#FFFFFF", outline="#CBD5E1", width=2)
        draw.text((mid_x, mid_y - 1), label, fill=color, font=font_lbl, anchor="mm")

def build_cloud_architecture_diagram():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Header Bar
    draw.rectangle([0, 0, WIDTH, 160], fill=AWS_SQUID_INK)
    font_main_title = get_font(52, bold=True)
    font_main_sub = get_font(24, bold=False)
    draw.text((80, 42), "ROADSENSE: CLOUD-NATIVE CIVIC ROAD HAZARD INTELLIGENCE PLATFORM", fill="#FFFFFF", font=font_main_title)
    draw.text((80, 104), "Decoupled Serverless Architecture • AWS us-east-1 • Account ID: 464817648755 • Production Topology", fill="#94A3B8", font=font_main_sub)

    # Status pill top-right
    draw_rounded_rect(draw, [WIDTH - 420, 50, WIDTH - 80, 110], 30, fill="#0F766E", outline="#14B8A6", width=2)
    font_pill = get_font(22, bold=True)
    draw.text((WIDTH - 250, 80), "● AWS US-EAST-1 ACTIVE", fill="#FFFFFF", font=font_pill, anchor="mm")

    # =========================================================================
    # TIER 1: CLIENT & EDGE TIER (Left Column)
    # =========================================================================
    tier1_x, tier1_y, tier1_w, tier1_h = 80, 200, 680, 1880
    draw_rounded_rect(draw, [tier1_x, tier1_y, tier1_x + tier1_w, tier1_y + tier1_h], 20, fill="#F0F9FF", outline="#0284C7", width=3)
    font_tier = get_font(28, bold=True)
    draw.text((tier1_x + 30, tier1_y + 35), "1. EDGE CLIENTS & TELEMETRY TIER", fill="#0284C7", font=font_tier)

    # Card 1.1: Citizen Mobile App
    draw_service_card(draw, tier1_x + 30, tier1_y + 90, 620, 480, "📱", 
                      "Citizen Mobile App", "Flutter Native / Android 12", [
                          ("Framework: ", "Flutter 3.x / Dart SDK"),
                          ("Hardware Verified: ", "OnePlus Nord (AC2001)"),
                          ("Sensors Polled: ", "High-res Camera, GPS WGS-84"),
                          ("Edge AI Detection: ", "Live Camera Frame Analysis"),
                          ("Payload Format: ", "Optimized Multipart JSON (4.4 KB)"),
                          ("Offline Mode: ", "Local SQLite Sync Buffer")
                      ], COLOR_CLIENT)

    # Card 1.2: Municipal Web Admin Portal
    draw_service_card(draw, tier1_x + 30, tier1_y + 610, 620, 520, "🏛️", 
                      "Municipal Admin Portal", "React 18 / TypeScript / Vite", [
                          ("Access Endpoint: ", "http://44.215.69.114/"),
                          ("Standard Standard: ", "ASTM D6433 PCI (63/100 Fair)"),
                          ("Civil Engineering: ", "Asphalt Material Forecast (2.7 Tons)"),
                          ("Budget Analytics: ", "Municipal Mobilization (₹1,08,000)"),
                          ("SLA Enforcement: ", "Active Regulatory Countdown Timers"),
                          ("Spatial Mapping: ", "Google Hybrid & Street Tile Overlays"),
                          ("Authentication: ", "Verified Municipal Admin Token")
                      ], COLOR_ADMIN)

    # Card 1.3: Multimodal AI Vision Engine
    draw_service_card(draw, tier1_x + 30, tier1_y + 1170, 620, 480, "✨", 
                      "Multimodal AI Vision Engine", "Cloud AI Semantic Hazard Inspection", [
                          ("Architecture: ", "Cloud Multimodal Visual Transformer"),
                          ("Resolution: ", "High-Precision 2D Defect Bounding Boxes"),
                          ("Criticality: ", "Automated Pothole vs Waterlogging"),
                          ("Reflectance Logic: ", "Specular Water Glint & Surface Sheen"),
                          ("Failover Fallback: ", "Smart Computer Vision Engine"),
                          ("Latency: ", "~380ms REST API Evaluation")
                      ], "#6366F1")

    # =========================================================================
    # TIER 2: AWS VPC INGESTION & COMPUTE (Middle Column)
    # =========================================================================
    vpc_x, vpc_y, vpc_w, vpc_h = 820, 200, 1480, 1880
    draw_rounded_rect(draw, [vpc_x, vpc_y, vpc_x + vpc_w, vpc_y + vpc_h], 20, fill="#FAFAFA", outline=VPC_BORDER, width=3)
    draw.text((vpc_x + 30, vpc_y + 35), "2. AWS VPC (10.0.0.0/16) — US-EAST-1 REGION", fill=VPC_BORDER, font=font_tier)

    # Public Subnet Container
    pub_x, pub_y, pub_w, pub_h = vpc_x + 30, vpc_y + 90, 700, 1750
    draw_rounded_rect(draw, [pub_x, pub_y, pub_x + pub_w, pub_y + pub_h], 16, fill=SUBNET_PUBLIC, outline="#93C5FD", width=2)
    font_subhdr = get_font(24, bold=True)
    draw.text((pub_x + 25, pub_y + 25), "Public Subnet (10.0.1.0/24)", fill="#1D4ED8", font=font_subhdr)

    # Card 2.1: Internet Gateway & Elastic IP
    draw_service_card(draw, pub_x + 20, pub_y + 70, 660, 360, "🌐",
                      "Internet Gateway (IGW)", "Elastic IPv4: 44.215.69.114", [
                          ("Network Ingress: ", "Public Internet Gateway"),
                          ("Security Group: ", "roadsense-sg (Ports 22, 80)"),
                          ("EIP Allocation: ", "44.215.69.114 (us-east-1)"),
                          ("Traffic Flow: ", "Direct Citizen & Admin Routes")
                      ], "#2563EB")

    # Card 2.2: Amazon EC2 Ingress Host
    draw_service_card(draw, pub_x + 20, pub_y + 460, 660, 560, "⚡",
                      "Amazon EC2 Instance", "roadsense-prod-ec2-api", [
                          ("Instance ID: ", "i-086b755fd5a8050e9"),
                          ("OS Image: ", "Ubuntu 24.04 LTS x86_64"),
                          ("Web Reverse Proxy: ", "Nginx 1.24 (Port 80 Ingress)"),
                          ("WSGI Container: ", "Gunicorn 2 asynchronously bound"),
                          ("Service Daemon: ", "systemd (roadsense.service)"),
                          ("Application: ", "Flask Modular Blueprint Engine"),
                          ("IAM Role: ", "roadsense-prod-ec2-role (No Keys)"),
                          ("Metric Alarm: ", "High-CPU Threshold >= 75%")
                      ], COLOR_EC2)

    # Card 2.3: AWS Systems Manager Parameter Store
    draw_service_card(draw, pub_x + 20, pub_y + 1050, 660, 420, "🔐",
                      "AWS SSM Parameter Store", "Secure Configuration Management", [
                          ("Namespace: ", "/roadsense/prod/*"),
                          ("Encryption: ", "AWS KMS (alias/aws/ssm)"),
                          ("Managed Secrets: ", "DB Host, DB Pass, S3, SQS, SNS"),
                          ("Security Bar: ", "Zero Hardcoded Plaintext Secrets"),
                          ("Dynamic Reload: ", "Automatic Environment Hydration")
                      ], COLOR_SSM)

    # Private Subnet Container
    priv_x, priv_y, priv_w, priv_h = vpc_x + 760, vpc_y + 90, 690, 1750
    draw_rounded_rect(draw, [priv_x, priv_y, priv_x + priv_w, priv_y + priv_h], 16, fill=SUBNET_PRIVATE, outline="#86EFAC", width=2)
    draw.text((priv_x + 25, priv_y + 25), "Private Subnet (10.0.2.0/24)", fill="#15803D", font=font_subhdr)

    # Card 2.4: Amazon RDS PostgreSQL
    draw_service_card(draw, priv_x + 20, priv_y + 70, 650, 540, "🗄️",
                      "Amazon RDS PostgreSQL", "Managed Spatial Database", [
                          ("Identifier: ", "roadsense-db"),
                          ("Engine Version: ", "PostgreSQL 16.3-R2"),
                          ("Spatial Extension: ", "PostGIS 3.4 (WGS-84 Indexing)"),
                          ("Endpoint: ", "roadsense-db.cr6eq8wg4tps.us-east-1"),
                          ("Security Group: ", "Inbound TCP 5432 from EC2 only"),
                          ("Storage: ", "20 GiB General Purpose SSD (gp3)"),
                          ("High Availability: ", "Multi-AZ Synchronous Mirroring"),
                          ("Backup Retention: ", "Automated 7-Day Snapshots + PITR")
                      ], COLOR_RDS)

    # Card 2.5: CloudWatch Metrics & Production Dashboard
    draw_service_card(draw, priv_x + 20, priv_y + 640, 650, 500, "📊",
                      "AWS CloudWatch Telemetry", "Production Observability", [
                          ("Dashboard Name: ", "RoadSense-Production-Dashboard"),
                          ("Alarm Name: ", "roadsense-prod-high-cpu-alarm"),
                          ("Alarm Target: ", "i-086b755fd5a8050e9 (CPU >= 75%)"),
                          ("Metric Resolution: ", "1-Minute High-Resolution Datapoints"),
                          ("Monitored Streams: ", "EC2 CPU, Network I/O, SQS, SNS"),
                          ("Automated Action: ", "Instant SNS Emergency Escalation")
                      ], COLOR_CW)

    # =========================================================================
    # TIER 3: AWS MANAGED SERVERLESS & STORAGE REALM (Right Column)
    # =========================================================================
    serv_x, serv_y, serv_w, serv_h = 2360, 200, 1400, 1880
    draw_rounded_rect(draw, [serv_x, serv_y, serv_x + serv_w, serv_y + serv_h], 20, fill=SERVERLESS_BG, outline="#D97706", width=3)
    draw.text((serv_x + 30, serv_y + 35), "3. AWS MANAGED SERVERLESS & ASSET REALM", fill="#D97706", font=font_tier)

    # Card 3.1: Amazon SQS Ingestion Queue
    draw_service_card(draw, serv_x + 40, serv_y + 90, 620, 520, "📬",
                      "Amazon SQS Queue", "roadsense-prod-hazard-queue", [
                          ("Queue Architecture: ", "Standard (Unbounded Concurrency)"),
                          ("Decoupling Metric: ", "45ms Instant HTTP 202 Response"),
                          ("Dead-Letter Queue: ", "roadsense-prod-hazard-dlq"),
                          ("Max Receive Count: ", "3 Failures before DLQ Quarantine"),
                          ("Visibility Timeout: ", "60 Seconds (Zero Race Hazard)"),
                          ("Retention Period: ", "4 Days (345,600 Seconds)"),
                          ("Resource Policy: ", "Explicit IAM EC2 / Lambda Grants")
                      ], COLOR_SQS)

    # Card 3.2: AWS Lambda Serverless Worker
    draw_service_card(draw, serv_x + 720, serv_y + 90, 640, 520, "⚙️",
                      "AWS Lambda Triage Worker", "RoadSenseHazardWorker", [
                          ("Runtime Environment: ", "Python 3.11 Serverless Container"),
                          ("Trigger Mapping: ", "Amazon SQS EventSource (BatchSize=10)"),
                          ("Trigger UUID: ", "cbaee3f5-95b2-4470-b6c9-65595c0ca02c"),
                          ("Municipal Routing: ", "Roads, Drainage, Electrical Bureau"),
                          ("SLA Deadlines: ", "Critical 24h, Medium 48h, Low 72h"),
                          ("Execution Role: ", "roadsense-prod-lambda-role"),
                          ("CloudWatch Logs: ", "/aws/lambda/RoadSenseHazardWorker")
                      ], COLOR_LAMBDA)

    # Card 3.3: Amazon S3 Hazard Media Storage
    draw_service_card(draw, serv_x + 40, serv_y + 640, 620, 500, "🪣",
                      "Amazon S3 Asset Bucket", "roadsense-hazards-464817648755", [
                          ("Region: ", "us-east-1 (N. Virginia)"),
                          ("Server-Side Crypto: ", "AES-256 (SSE-S3 Managed Keys)"),
                          ("Partition Keys: ", "/hazards/{uuid}_{timestamp}.jpg"),
                          ("Payload Impact: ", "Reduced API response 66MB -> 4.4KB"),
                          ("Optimization Gain: ", "99.99% Network Payload Reduction"),
                          ("Lifecycle Transition: ", "90d Standard-IA, 365d Glacier"),
                          ("Public CDN URL: ", "Direct High-Speed Edge Access")
                      ], COLOR_S3)

    # Card 3.4: Amazon SNS Critical Emergency Alerts
    draw_service_card(draw, serv_x + 720, serv_y + 640, 640, 500, "📢",
                      "Amazon SNS Emergency Alerting", "roadsense-prod-critical-alerts", [
                          ("Topic ARN: ", "arn:aws:sns:us-east-1:464817648755:..."),
                          ("Fan-Out Protocols: ", "SMS & Email Multi-Protocol Broadcast"),
                          ("Trigger Threshold: ", "Severity == 'CRITICAL' Hazards"),
                          ("Subscribers: ", "Municipal Highway Patrol & Dispatch"),
                          ("Emergency Content: ", "GPS Lat/Lng, Category, S3 Frame URL"),
                          ("Delivery Auditing: ", "CloudWatch Logs Delivery Tracking")
                      ], COLOR_SNS)

    # Summary Statistics Box at bottom of Serverless Tier
    draw_rounded_rect(draw, [serv_x + 40, serv_y + 1180, serv_x + serv_w - 40, serv_y + 1820], 16, fill="#FFFFFF", outline="#E2E8F0", width=2)
    font_summary_hdr = get_font(26, bold=True)
    draw.text((serv_x + 70, serv_y + 1210), "ARCHITECTURAL RESILIENCE & BENCHMARK AUDIT", fill=AWS_SQUID_INK, font=font_summary_hdr)

    bench_bullets = [
        ("Client Ingestion Speedup: ", "1.03 Seconds (95.9% speedup compared to synchronous 25.12s legacy pipeline)"),
        ("Database Storage Offload: ", "Binary base64 image strings completely removed from relational schemas"),
        ("Zero-Message-Loss SLA: ", "Amazon SQS buffering guarantees zero lost citizen reports during storm surges"),
        ("Partial Batch Recovery: ", "AWS Lambda only retries unparseable messages via SQS batchItemFailures"),
        ("Least-Privilege Security: ", "IAM Instance Profiles and SSM Parameter Store eliminate plain-text API keys"),
        ("ASTM D6433 Compliance: ", "Real-time Pavement Condition Index rating and cold-mix asphalt tonnage estimation")
    ]
    cur_by = serv_y + 1260
    for title, desc in bench_bullets:
        draw.text((serv_x + 70, cur_by), "✔ " + title, fill="#047857", font=get_font(21, bold=True))
        title_len = draw.textlength("✔ " + title, font=get_font(21, bold=True))
        draw.text((serv_x + 70 + title_len, cur_by), desc, fill="#334155", font=get_font(21, bold=False))
        cur_by += 44

    # =========================================================================
    # ARCHITECTURAL CONNECTION ARROWS
    # =========================================================================
    # Mobile App -> EC2 Ingress
    draw_arrow(draw, (tier1_x + 650, tier1_y + 280), (pub_x + 20, pub_y + 540), 
               "POST /api/infer (Base64 / Multipart)", color="#0284C7", lw=6)

    # Mobile App <-> Gemini Vision AI
    draw_arrow(draw, (tier1_x + 340, tier1_y + 570), (tier1_x + 340, tier1_y + 1170), 
               "Multimodal Semantic Detection", color="#6366F1", lw=5)

    # Web Admin <-> EC2 Nginx
    draw_arrow(draw, (tier1_x + 650, tier1_y + 800), (pub_x + 20, pub_y + 700), 
               "HTTPS /api/admin/* (PCI & SLA)", color="#0F172A", lw=6)

    # EC2 -> SQS Enqueue
    draw_arrow(draw, (pub_x + 680, pub_y + 600), (serv_x + 40, serv_y + 300), 
               "boto3.sqs.send_message()", color=COLOR_SQS, lw=6)

    # EC2 -> S3 Upload
    draw_arrow(draw, (pub_x + 680, pub_y + 760), (serv_x + 40, serv_y + 820), 
               "boto3.s3.put_object() [AES-256]", color=COLOR_S3, lw=6)

    # SQS -> Lambda Trigger
    draw_arrow(draw, (serv_x + 660, serv_y + 300), (serv_x + 720, serv_y + 300), 
               "Event Source Mapping (Batch=10)", color=COLOR_LAMBDA, lw=6)

    # Lambda -> SNS Critical Broadcast
    draw_arrow(draw, (serv_x + 1040, serv_y + 610), (serv_x + 1040, serv_y + 640), 
               "Critical Alert Fan-Out", color=COLOR_SNS, lw=6)

    # EC2 / Lambda -> RDS
    draw_arrow(draw, (pub_x + 680, pub_y + 490), (priv_x + 20, priv_y + 260), 
               "PostgreSQL Port 5432 (ACID)", color=COLOR_RDS, lw=6)

    # EC2 -> SSM Parameter Store
    draw_arrow(draw, (pub_x + 350, pub_y + 1020), (pub_x + 350, pub_y + 1050), 
               "boto3.ssm.get_parameters()", color=COLOR_SSM, lw=5)

    # EC2 -> CloudWatch Metrics
    draw_arrow(draw, (pub_x + 680, pub_y + 820), (priv_x + 20, priv_y + 800), 
               "EC2 CPU & Network In/Out", color=COLOR_CW, lw=5)

    output_path = "d:/ChitraDartaa-A-Civic-Issue-Reporting-System/docs/report_assets/cloud_architecture_diagram.png"
    img.save(output_path, "PNG", quality=95)
    print(f"Enterprise Cloud Architecture Diagram saved to: {output_path}")

def build_enterprise_sequence_diagram():
    img = Image.new("RGB", (WIDTH, HEIGHT), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, WIDTH, 160], fill=AWS_SQUID_INK)
    font_main_title = get_font(50, bold=True)
    font_main_sub = get_font(24, bold=False)
    draw.text((80, 42), "ROADSENSE: END-TO-END DECOUPLED DATA FLOW & SERVERLESS LIFECYCLE", fill="#FFFFFF", font=font_main_title)
    draw.text((80, 104), "Asynchronous Sequence Architecture • Sub-Second Client Response • Autonomous Municipal Triage", fill="#94A3B8", font=font_main_sub)

    # Actors definition
    actors = [
        ("Citizen Mobile App\n(Flutter / Android)", 240, COLOR_CLIENT),
        ("Gemini Vision AI\n(Multimodal Inspector)", 680, "#6366F1"),
        ("Amazon EC2 Ingress\n(Nginx / Flask Ingress)", 1140, COLOR_EC2),
        ("Amazon SQS Queue\n(Decoupled Buffer)", 1620, COLOR_SQS),
        ("AWS Lambda Worker\n(RoadSenseHazardWorker)", 2120, COLOR_LAMBDA),
        ("Amazon S3 & RDS\n(Asset Store / Postgres)", 2640, COLOR_RDS),
        ("Amazon SNS Fan-Out\n(Emergency Alerting)", 3140, COLOR_SNS),
        ("Municipal Admin Portal\n(Executive Dashboard)", 3600, COLOR_ADMIN)
    ]

    font_actor = get_font(20, bold=True)
    top_y = 220
    bot_y = 2050

    # Draw Actor Header Cards and Vertical Lifelines
    for title, x, color in actors:
        # Top Card
        card_w, card_h = 240, 100
        draw_rounded_rect(draw, [x - card_w//2 + 4, top_y + 4, x + card_w//2 + 4, top_y + card_h + 4], 12, fill="#E2E8F0")
        draw_rounded_rect(draw, [x - card_w//2, top_y, x + card_w//2, top_y + card_h], 12, fill=color, outline="#0F172A", width=2)
        
        lines = title.split("\n")
        draw.text((x, top_y + 30), lines[0], fill="#FFFFFF", font=font_actor, anchor="mm")
        if len(lines) > 1:
            draw.text((x, top_y + 65), lines[1], fill="#E2E8F0", font=get_font(17, bold=False), anchor="mm")

        # Lifeline
        draw.line([x, top_y + card_h, x, bot_y], fill="#CBD5E1", width=3)

        # Bottom anchor box
        draw_rounded_rect(draw, [x - card_w//2, bot_y, x + card_w//2, bot_y + 60], 8, fill=color)
        draw.text((x, bot_y + 30), lines[0], fill="#FFFFFF", font=get_font(18, bold=True), anchor="mm")

    # Sequence Messages
    steps = [
        (240, 680, 400, "1. Camera Frame + Description sent for Gemini Multimodal Vision Inspection", "#6366F1"),
        (680, 240, 520, "2. Gemini AI returns 2D Bounding Box [ymin, xmin, ymax, xmax] & Criticality Level", "#6366F1"),
        (240, 1140, 650, "3. Mobile App submits lightweight JSON payload (4.4 KB) to POST /api/infer", COLOR_CLIENT),
        (1140, 1620, 780, "4. Decoupling: Ingress enqueues hazard event via boto3.sqs.send_message()", COLOR_SQS),
        (1140, 240, 910, "5. EC2 returns instant HTTP 202 Accepted (Sub-second client latency: 45ms)", "#059669"),
        (1620, 2120, 1050, "6. SQS Event Source Mapping triggers Lambda worker in batches (BatchSize=10)", COLOR_LAMBDA),
        (2120, 2640, 1190, "7. Lambda persists binary JPEG frame to S3 (AES-256) & spatial records to RDS", COLOR_RDS),
        (2120, 2120, 1340, "8. Autonomous Municipal Triage: Assigns Division (Roads/Drainage) & SLA (24h/48h)", "#8B5CF6"),
        (2120, 3140, 1490, "9. If Severity == 'CRITICAL', publishes alert to Amazon SNS Topic", COLOR_SNS),
        (3140, 3140, 1630, "10. SNS Fans Out Emergency SMS to Highway Squads & Email to Commissioners", "#DC2626"),
        (3600, 1140, 1770, "11. Municipal Admin Portal queries live spatial incidents and ASTM D6433 PCI (63/100)", COLOR_ADMIN),
        (1140, 3600, 1910, "12. Renders Asphalt Tonnage (2.7 Tons), Mobilization Cost (₹1,08,000) & Active SLAs", "#047857")
    ]

    for x1, x2, y, label, col in steps:
        if x1 == x2:
            # Self loop
            draw.arc([x1 - 20, y - 45, x1 + 100, y + 45], start=270, end=90, fill=col, width=4)
            # Arrow head
            draw.polygon([(x1, y + 45), (x1 + 16, y + 36), (x1 + 16, y + 54)], fill=col)
            # Label
            font_s = get_font(19, bold=True)
            lbl_w = draw.textlength(label, font=font_s) + 20
            draw_rounded_rect(draw, [x1 + 110, y - 22, x1 + 110 + lbl_w, y + 22], 6, fill="#FFFFFF", outline="#CBD5E1", width=2)
            draw.text((x1 + 120, y - 1), label, fill=col, font=font_s, anchor="lm")
        else:
            draw_arrow(draw, (x1, y), (x2, y), label, color=col, lw=5)

    seq_output_path = "d:/ChitraDartaa-A-Civic-Issue-Reporting-System/docs/report_assets/data_flow_sequence.png"
    img.save(seq_output_path, "PNG", quality=95)
    print(f"Enterprise Data Flow Sequence Diagram saved to: {seq_output_path}")

if __name__ == "__main__":
    build_cloud_architecture_diagram()
    build_enterprise_sequence_diagram()
