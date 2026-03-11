from app import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = "reports"

    report_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    hemoglobin = db.Column(db.Numeric(5,2), nullable=True)
    doctor_note = db.Column(db.Text, nullable=True)
    report_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    embeddings = db.relationship("ReportEmbedding", backref="report", lazy=True)


class ReportEmbedding(db.Model):
    __tablename__ = "report_embeddings"

    embedding_id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.report_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    embedding = db.Column(db.ARRAY(db.Float), nullable=False)  # double precision[]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
