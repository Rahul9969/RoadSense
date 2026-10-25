"""
Script to generate high-resolution architecture diagrams for RoadSense Cloud Documentation.
Generates:
1. docs/report_assets/cloud_architecture_diagram.png (High-res AWS topology)
2. docs/report_assets/data_flow_sequence.png (Sequence diagram of issue lifecycle)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

def generate_cloud_architecture():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    ax.set_facecolor('#F8FAFC')
    fig.patch.set_facecolor('#FFFFFF')
    
    # Title
    plt.suptitle("RoadSense: Cloud-Native Serverless & Decoupled Architecture (AWS us-east-1)", 
                 fontsize=18, fontweight='bold', color='#0F172A', y=0.96)
    plt.title("End-to-End Pipeline: Mobile Edge AI -> EC2 Reverse Proxy -> Amazon SQS -> AWS Lambda -> Amazon S3 / RDS -> Amazon SNS -> Municipal Web Admin", 
              fontsize=11, color='#475569', pad=15)
    
    # Define bounding boxes for tiers
    tiers = [
        ("EDGE & CLIENT TIER", 0.5, 0.8, 4.0, 7.8, '#E0F2FE', '#0284C7'),
        ("AWS COMPUTE & INGESTION TIER", 5.0, 0.8, 5.0, 7.8, '#F3E8FF', '#7E22CE'),
        ("SERVERLESS DECOUPLING & STORAGE TIER", 10.5, 0.8, 5.0, 7.8, '#FEF3C7', '#D97706'),
    ]
    
    for title, x, y, w, h, bg, border in tiers:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", 
                                      facecolor=bg, edgecolor=border, linewidth=1.8, linestyle='--')
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.35, title, ha='center', va='center', 
                fontsize=11, fontweight='bold', color=border)

    # Component Nodes
    components = [
        # Client Tier
        {"id": "mobile", "label": "Citizen Mobile App\n(Flutter / Android)\nEdge YOLOv8 Detection\nInstant Offline Cache", "x": 2.5, "y": 6.8, "color": "#0284C7", "text_color": "#FFFFFF"},
        {"id": "gps", "label": "Device Sensors\nGPS WGS-84 Telemetry\nCamera EXIF & Compass", "x": 2.5, "y": 4.5, "color": "#38BDF8", "text_color": "#0F172A"},
        {"id": "webadmin", "label": "Municipal Web Admin\n(React 18 / Vite / TS)\nLive Cloud Telemetry\nASTM D6433 PCI Triage", "x": 2.5, "y": 2.2, "color": "#0369A1", "text_color": "#FFFFFF"},
        
        # Compute Tier
        {"id": "ec2", "label": "Amazon EC2 Instance\n(Ubuntu 24.04 / 44.215.69.114)\nNginx Reverse Proxy\nGunicorn WSGI Application", "x": 7.5, "y": 6.8, "color": "#7E22CE", "text_color": "#FFFFFF"},
        {"id": "api", "label": "Flask REST Backend\nModel Runner Service\nOptimized Serializer (4.4KB)\nIAM Role Authentication", "x": 7.5, "y": 4.5, "color": "#A855F7", "text_color": "#FFFFFF"},
        {"id": "ssm", "label": "AWS Systems Manager\nParameter Store\nEncrypted Secrets & Config\nIAM Instance Profile", "x": 7.5, "y": 2.2, "color": "#9333EA", "text_color": "#FFFFFF"},

        # Serverless / Storage Tier
        {"id": "sqs", "label": "Amazon SQS Queue\nroadsense-prod-hazard-queue\nDecoupled Buffer & Throttling\nDLQ: maxReceiveCount=3", "x": 13.0, "y": 7.0, "color": "#D97706", "text_color": "#FFFFFF"},
        {"id": "lambda", "label": "AWS Lambda Function\nRoadSenseHazardWorker\nBatch Parsing (BatchSize=10)\nDepartment Triage & SLA", "x": 13.0, "y": 5.0, "color": "#EA580C", "text_color": "#FFFFFF"},
        {"id": "s3", "label": "Amazon S3 Bucket\nroadsense-hazards-*\nAES-256 Object Storage\nLifecycle & Public CDN URL", "x": 13.0, "y": 3.2, "color": "#B45309", "text_color": "#FFFFFF"},
        {"id": "rds", "label": "Amazon RDS PostgreSQL 16\nACID Spatial Storage\nPostGIS Proximity Index\nAuto Automated Snapshots", "x": 13.0, "y": 1.5, "color": "#15803D", "text_color": "#FFFFFF"},
    ]

    for comp in components:
        box = patches.FancyBboxPatch((comp["x"] - 1.8, comp["y"] - 0.65), 3.6, 1.3, 
                                     boxstyle="round,pad=0.15", facecolor=comp["color"], 
                                     edgecolor='#0F172A', linewidth=1.2)
        ax.add_patch(box)
        ax.text(comp["x"], comp["y"], comp["label"], ha='center', va='center', 
                fontsize=8.5, fontweight='bold', color=comp["text_color"], multialignment='center')

    # Draw connection arrows with labels
    arrows = [
        # Mobile -> EC2
        ((4.3, 6.8), (5.7, 6.8), "POST /api/report_hazard\n(Lightweight Multipart, 4.4KB)", "#0284C7"),
        # EC2 -> SQS
        ((9.3, 6.8), (11.2, 7.0), "boto3.send_message()\n(Decoupled Ingestion)", "#7E22CE"),
        # SQS -> Lambda
        ((13.0, 6.35), (13.0, 5.65), "Event Source Mapping\n(BatchSize=10)", "#D97706"),
        # Lambda -> S3
        ((11.2, 4.8), (11.2, 3.4), "boto3.put_object()\n(Hazard Image Frame)", "#EA580C"),
        # Lambda -> RDS
        ((13.0, 4.35), (13.0, 2.15), "SQL INSERT / UPDATE\n(SLA, Dept, GeoJSON)", "#15803D"),
        # Lambda -> SNS
        # EC2 -> S3 / RDS
        ((9.3, 4.5), (11.2, 3.2), "Read Asset URLs", "#64748B"),
        ((9.3, 4.5), (11.2, 1.5), "Fetch Hazard Records", "#64748B"),
        # Web Admin <-> EC2
        ((4.3, 2.2), (5.7, 4.2), "GET /api/admin/*\nTelemetry & Triage APIs", "#0369A1"),
    ]

    for start, end, label, color in arrows:
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", color=color, lw=2.0, mutation_scale=15))
        # Add text in the middle
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2 + 0.18
        ax.text(mid_x, mid_y, label, ha='center', va='center', fontsize=7.5, 
                color='#1E293B', fontweight='bold',
                bbox=dict(boxstyle="square,pad=0.15", facecolor="#FFFFFF", edgecolor="#CBD5E1", alpha=0.9))

    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    plt.tight_layout()
    output_path = "d:/ChitraDartaa-A-Civic-Issue-Reporting-System/docs/report_assets/cloud_architecture_diagram.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved architecture diagram to:", output_path)

def generate_data_flow_sequence():
    fig, ax = plt.subplots(figsize=(15, 8), dpi=300)
    ax.set_facecolor('#FFFFFF')
    fig.patch.set_facecolor('#FFFFFF')
    
    plt.suptitle("RoadSense: End-to-End Civic Hazard Data Flow & Decoupled Execution Lifecycle", 
                 fontsize=16, fontweight='bold', color='#0F172A', y=0.96)
    
    actors = [
        ("Citizen Mobile App\n(Flutter / Android)", 1.5, "#0284C7"),
        ("EC2 Ingestion API\n(Nginx / Flask)", 4.0, "#7E22CE"),
        ("Amazon SQS\n(Hazard Buffer)", 6.5, "#D97706"),
        ("AWS Lambda Worker\n(RoadSenseHazardWorker)", 9.0, "#EA580C"),
        ("Amazon S3 & RDS\n(Asset CDN & PostgreSQL)", 11.5, "#15803D"),
        ("Admin Web Portal\n(Executive Dashboard)", 14.0, "#0369A1"),
    ]
    
    # Draw vertical lifelines
    for name, x, color in actors:
        box = patches.FancyBboxPatch((x - 1.0, 7.5), 2.0, 0.8, boxstyle="round,pad=0.1", 
                                     facecolor=color, edgecolor='#0F172A', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x, 7.9, name, ha='center', va='center', fontsize=8, fontweight='bold', color='#FFFFFF')
        ax.plot([x, x], [0.8, 7.5], color='#94A3B8', linestyle='--', linewidth=1.2)
    
    # Sequence Messages
    steps = [
        (1.5, 4.0, 7.0, "1. Capture Hazard Frame + GPS Telemetry + Local YOLOv8 Inference", "#0284C7"),
        (4.0, 6.5, 6.3, "2. Decouple: Write Message to SQS ('roadsense-prod-hazard-queue')", "#7E22CE"),
        (4.0, 1.5, 5.6, "3. Return Instant HTTP 202 Accepted (Sub-second response, 4.4KB)", "#059669"),
        (6.5, 9.0, 4.9, "4. Event Source Mapping triggers Lambda in Batches (BatchSize=10)", "#D97706"),
        (9.0, 11.5, 4.2, "5. Upload Binary Frame to S3 (AES-256) & Insert Record into RDS", "#EA580C"),
        (9.0, 9.0, 3.5, "6. Municipal Triage: Assign Dept (Roads/Stormwater) & Calculate SLA", "#C026D3"),
        (9.0, 14.0, 2.8, "7. SNS Fan-Out: SMS/Push Alert if Hazard Severity == 'CRITICAL'", "#DC2626"),
        (14.0, 4.0, 2.1, "8. Admin Portal Polls Telemetry & ASTM D6433 Pavement Health Index", "#0369A1"),
        (4.0, 14.0, 1.4, "9. Real-Time Status, Asphalt Tonnage Forecast & Budget Rendered", "#0284C7"),
    ]
    
    for x1, x2, y, label, color in steps:
        if x1 == x2:
            # Self loop
            loop = patches.Arc((x1 + 0.35, y), 0.7, 0.4, angle=0, theta1=270, theta2=90, color=color, lw=1.8)
            ax.add_patch(loop)
            ax.text(x1 + 0.8, y, label, ha='left', va='center', fontsize=7.5, fontweight='bold', color=color)
        else:
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.8, mutation_scale=12))
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y + 0.15, label, ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=color,
                    bbox=dict(boxstyle="square,pad=0.1", facecolor="#FFFFFF", edgecolor="#E2E8F0", alpha=0.95))
            
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0.5, 8.8)
    ax.axis('off')
    plt.tight_layout()
    output_path = "d:/ChitraDartaa-A-Civic-Issue-Reporting-System/docs/report_assets/data_flow_sequence.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved data flow sequence diagram to:", output_path)

if __name__ == "__main__":
    generate_cloud_architecture()
    generate_data_flow_sequence()
