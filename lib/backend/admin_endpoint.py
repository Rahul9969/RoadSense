import json
import logging
from flask import Blueprint, jsonify, request
from models import IssueReport
from extension import db
from auth import token_required

logger = logging.getLogger("roadsense.admin")
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/reports", methods=["GET"])
def get_reports():
    """
    Returns list of all reported road hazards.
    Supports query parameters:
      - ?status=reported|deployed|underprocessed|resolved
      - ?severity=low|medium|critical
      - ?search=pothole
    """
    status_filter = request.args.get("status")
    severity_filter = request.args.get("severity")
    search_query = request.args.get("search")

    query = IssueReport.query

    if status_filter:
        query = query.filter_by(status=status_filter.lower())

    if severity_filter:
        query = query.filter_by(severity=severity_filter.lower())

    if search_query:
        search_term = f"%{search_query.lower()}%"
        query = query.filter(
            (IssueReport.label.ilike(search_term)) |
            (IssueReport.username.ilike(search_term)) |
            (IssueReport.description.ilike(search_term))
        )

    reports = query.order_by(IssueReport.created_at.desc()).all()
    formatted_reports = [report.to_dict() for report in reports]

    return jsonify({
        "reports": formatted_reports,
        "count": len(formatted_reports)
    }), 200


@admin_bp.route("/reports/<int:report_id>", methods=["PATCH", "PUT"])
def update_report(report_id):
    """
    Updates road hazard status (e.g. reported -> deployed -> underprocessed -> resolved)
    or severity level.
    """
    report = IssueReport.query.get_or_404(report_id)
    data = request.get_json(silent=True) or {}

    if "status" in data:
        valid_statuses = ["reported", "deployed", "underprocessed", "resolved"]
        new_status = data["status"].lower()
        if new_status in valid_statuses:
            report.status = new_status

    if "severity" in data:
        valid_severities = ["low", "medium", "critical"]
        new_severity = data["severity"].lower()
        if new_severity in valid_severities:
            report.severity = new_severity

    if "description" in data:
        report.description = data["description"]

    db.session.commit()
    logger.info(f"Updated report #{report_id} status to '{report.status}'")

    return jsonify({
        "message": "Report updated successfully",
        "report": report.to_dict()
    }), 200


@admin_bp.route("/stats", methods=["GET"])
def get_stats():
    """
    Returns aggregated KPI statistics for the RoadSense Admin Dashboard.
    """
    total = IssueReport.query.count()
    reported = IssueReport.query.filter_by(status="reported").count()
    deployed = IssueReport.query.filter_by(status="deployed").count()
    underprocessed = IssueReport.query.filter_by(status="underprocessed").count()
    resolved = IssueReport.query.filter_by(status="resolved").count()
    critical = IssueReport.query.filter_by(severity="critical").count()

    return jsonify({
        "total": total,
        "reported": reported,
        "deployed": deployed,
        "underprocessed": underprocessed,
        "resolved": resolved,
        "critical": critical
    }), 200