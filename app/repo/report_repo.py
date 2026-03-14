from app import db
from app.models.report import Report, ReportEmbedding

class ReportRepo:
    @staticmethod
    def save_report(user_id, category, hemoglobin=None, report_date=None, filename=None, doctor_note=None):
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
    
    @staticmethod
    def get_reports_by_user(user_id, sort_order="newest"):
        query = Report.query.filter_by(user_id=user_id)
        if sort_order == "oldest":
            query = query.order_by(Report.created_at.asc())
        else:
            query = query.order_by(Report.created_at.desc())

        return query.all()
    
    @staticmethod
    def get_report_by_id(report_id):
        return Report.query.get(report_id)

    @staticmethod
    def delete_report(report):
        db.session.delete(report)
        db.session.commit()
    
    @staticmethod
    def get_user_hb_reports(user_id):
        return (
            Report.query
            .filter(Report.user_id == user_id)
            .filter(Report.hemoglobin != None)
            .order_by(Report.report_date.asc())
            .all()
        )
