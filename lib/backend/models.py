from extension import db
from datetime import datetime

class IssueReport(db.Model):
    __tablename__ = "issue_reports"

    issue_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    location = db.Column(db.JSON, nullable=False)
    
    # Cloud storage URL (Amazon S3) & legacy base64 support
    image_url = db.Column(db.String(500), nullable=True)
    segmented_image = db.Column(db.Text, nullable=True)  # base64 fallback
    confidence_score = db.Column(db.Float, nullable=False, default=0.85)

    # Status: 'reported', 'deployed', 'underprocessed', 'resolved'
    status = db.Column(db.String(30), default="reported")
    
    # Severity: 'low', 'medium', 'critical'
    severity = db.Column(db.String(20), default="medium")
    description = db.Column(db.Text, nullable=True, default="Road hazard reported by citizen")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    filepath = db.Column(db.String(300), nullable=True)
    label = db.Column(db.String(200), nullable=False, default="Potholes")

    def to_dict(self):
        # Format location lat/lng safely
        loc = self.location if isinstance(self.location, dict) else {}
        lat = float(loc.get("lat", loc.get("latitude", 27.6194)))
        lng = float(loc.get("lng", loc.get("longitude", 85.5388)))

        # Format image source: Prefer S3 URL, fallback to segmented base64 or filepath
        img = self.image_url or self.segmented_image or ""

        return {
            "id": self.issue_id,
            "issue_id": self.issue_id,
            "title": f"{self.label} at ({lat:.4f}, {lng:.4f})",
            "description": self.description or f"Road hazard ({self.label}) reported by {self.username}",
            "reporter": self.username,
            "username": self.username,
            "location": {"lat": lat, "lng": lng},
            "status": self.status or "reported",
            "severity": self.severity or "medium",
            "confidence_score": round(self.confidence_score, 3) if self.confidence_score else 0.85,
            "image_url": self.image_url or "",
            "segmented_image": self.segmented_image or "",
            "image": img,
            "timestamp": self.created_at.isoformat() if self.created_at else datetime.utcnow().isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else datetime.utcnow().isoformat(),
            "label": self.label,
        }