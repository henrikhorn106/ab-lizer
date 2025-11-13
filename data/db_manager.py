from data.models import db, ab_tests, variants, reports, users

class DBManager:

    def create_ab_test(self, name, description, metric):
        test = ab_tests(name=name, description=description, metric=metric)
        db.session.add(test)
        db.session.commit()

    def create_variant(self, test_id, name, impressions, conversions, conversion_rate):
        variant = variants(test_id=test_id, name=name, impressions=impressions, conversions=conversions, conversion_rate=conversion_rate)
        db.session.add(variant)
        db.session.commit()

    def create_report(self, test_id, summary, significance, ai_recommendation):
        report = reports(test_id=test_id, summary=summary, significance=significance, ai_recommendation=ai_recommendation)
        db.session.add(report)
        db.session.commit()

    def create_user(self, name, email):
        user = users(name=name, email=email)
        db.session.add(user)
        db.session.commit()

    def get_ab_tests(self):
        return ab_tests.query.all()

    def get_recent_test(self):
        return ab_tests.query.order_by(ab_tests.created_at.desc()).limit(1).all()

    def get_all_variants(self):
        return variants.query.all()

    def get_variants(self, test_id):
        return variants.query.filter_by(test_id=test_id).all()

    def get_reports(self, test_id):
        return reports.query.filter_by(test_id=test_id).all()

    def get_users(self):
        return users.query.all()
