from app import db
from app.models.report import Report, ReportEmbedding

class ReportRepo:
    @staticmethod
    def save_report(user_id, category, filename, hemoglobin, doctor_note, report_date):
        report = Report(
            user_id=user_id,
            category=category,
            filename=filename,
            hemoglobin=hemoglobin,
            doctor_note=doctor_note,
            report_date=report_date
        )
        db.session.add(report)
        db.session.commit()
        return report

    @staticmethod
    def save_embedding(report_id, user_id, vector):
        embedding = ReportEmbedding(
            report_id=report_id,
            user_id=user_id,
            embedding=vector
        )
        db.session.add(embedding)
        db.session.commit()
        return embedding
