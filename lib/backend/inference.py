import os
import io
import time
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from extension import db
from models import IssueReport
from auth import token_required
from utils.image_utils import base64_to_image, image_to_base64
from utils.model_runner import run_inference
from aws_service import upload_image_to_s3, publish_critical_alert, enqueue_hazard_event

logger = logging.getLogger("roadsense.inference")

inference_bp = Blueprint("inference", __name__, url_prefix="/api/infer")
citizen_report = Blueprint("citizen_report", __name__, url_prefix="/api/citizenreport")
health_bp = Blueprint("health", __name__, url_prefix="/api/health")


@health_bp.route("", methods=["GET"])
def health_check():
    """
    Amazon EC2 / ALB target group health check endpoint.
    Returns 200 OK to confirm the backend instance is alive.
    """
    return jsonify({
        "status": "healthy",
        "service": "RoadSense Cloud Hazard Engine",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }), 200


@citizen_report.route("", methods=["POST", "GET"])
@token_required
def citizenreport():
    """Fetches reports submitted by the authenticated citizen."""
    data = request.get_json(silent=True) or {}
    username = data.get("username") or getattr(request, "user", None)

    if not username:
        return jsonify({"error": "No username provided"}), 400

    reports = IssueReport.query.filter_by(username=username).order_by(IssueReport.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reports]), 200


@inference_bp.route("", methods=["POST"])
@token_required
def infer_image():
    """
    Main Hazard Reporting & Inference Endpoint.
    1. Ingests image (Base64 or multipart form file).
    2. Runs AI hazard classification/detection.
    3. Uploads image to Amazon S3.
    4. Enqueues event into Amazon SQS.
    5. Dispatches Amazon SNS alert if hazard is critical.
    6. Persists hazard report to Amazon RDS.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No JSON payload received"}), 400

        username = data.get("username") or getattr(request, "user", "citizen_user")
        location_data = data.get("location", {})
        image_base64 = data.get("image")
        description = data.get("description", "Reported road issue")
        severity = data.get("severity", "medium").lower()
        custom_label = data.get("category") or data.get("label")

        # Location normalization
        if isinstance(location_data, dict):
            lat = float(location_data.get("lat", location_data.get("latitude", 27.6194)))
            lng = float(location_data.get("lng", location_data.get("longitude", 85.5388)))
            location = {"lat": lat, "lng": lng}
        else:
            return jsonify({"error": "Location must be an object with lat and lng"}), 400

        if not image_base64:
            return jsonify({"error": "Missing image field (Base64 string required)"}), 400

        # 1. Convert base64 -> PIL Image
        pil_image = base64_to_image(image_base64)
        if pil_image.mode in ("RGBA", "P"):
            pil_image = pil_image.convert("RGB")

        # Downscale oversized mobile camera uploads to prevent high memory usage
        max_dim = 1024
        if max(pil_image.size) > max_dim:
            scale = max_dim / float(max(pil_image.size))
            new_size = (int(pil_image.size[0] * scale), int(pil_image.size[1] * scale))
            pil_image = pil_image.resize(new_size, 1) # Image.Resampling.BILINEAR

        # 2. Run AI Inference / Segmentation
        hint = f"{description}".strip()
        infer_res = run_inference(pil_image, hint_text=hint)
        annotated_img, confidence, predicted_class = infer_res
        # Prioritize true AI prediction over static form dropdown defaults
        final_label = predicted_class if predicted_class else (custom_label or "Potholes")

        # Determine severity automatically from AI engine or hazard classification
        ai_severity = getattr(infer_res, "severity", None)
        if ai_severity:
            severity = str(ai_severity).lower()
        elif final_label in ["Potholes", "Waterlogging"]:
            severity = "critical"
        elif final_label in ["Damaged Road", "Broken Streetlight"]:
            severity = "medium"
        else:
            severity = "low"

        # Check if this request is a live camera/image preview check
        is_preview = data.get("is_preview", False) or request.args.get("preview", "false").lower() == "true"
        if is_preview:
            annotated_base64 = image_to_base64(annotated_img)
            return jsonify({
                "label": final_label,
                "confidence_score": confidence,
                "segmented_image": annotated_base64,
                "severity": severity,
                "is_preview": True
            }), 200

        # 3. Convert annotated image to bytes & Base64
        img_byte_arr = io.BytesIO()
        annotated_img.save(img_byte_arr, format='JPEG', quality=85)
        raw_bytes = img_byte_arr.getvalue()
        annotated_base64 = image_to_base64(annotated_img)

        # 4. Upload to Amazon S3
        s3_image_url = upload_image_to_s3(raw_bytes, filename_prefix="hazards")

        # 5. Persist to Database (Amazon RDS / SQLite fallback)
        # Point segmented_image to s3_image_url to eliminate 50MB payload bloat
        report = IssueReport(
            username=username,
            location=location,
            image_url=s3_image_url,
            segmented_image=s3_image_url,
            confidence_score=float(confidence),
            label=final_label,
            status="reported",
            severity=severity,
            description=description,
            filepath=s3_image_url,
            created_at=datetime.utcnow()
        )
        db.session.add(report)
        db.session.commit()

        # 6. Additional Cloud Capability 1: Amazon SNS Critical Hazard Alert
        if severity == "critical":
            publish_critical_alert(
                report_id=report.issue_id,
                label=final_label,
                severity=severity,
                location=location,
                reporter=username,
                image_url=s3_image_url
            )

        # 7. Additional Cloud Capability 2: Amazon SQS Asynchronous Queue
        enqueue_hazard_event({
            "report_id": report.issue_id,
            "username": username,
            "location": location,
            "label": final_label,
            "severity": severity,
            "image_url": s3_image_url,
            "timestamp": datetime.utcnow().isoformat()
        })

        # 8. Return response compatible with both Flutter app and Web App
        return jsonify({
            "message": "Hazard report submitted successfully",
            "report_id": report.issue_id,
            "id": report.issue_id,
            "label": final_label,
            "severity": severity,
            "segmented_image": annotated_base64,
            "image_url": s3_image_url,
            "confidence_score": confidence,
            "status": "reported"
        }), 200

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        logger.exception("Inference endpoint error")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
