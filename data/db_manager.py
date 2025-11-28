from data.models import db, ab_tests, variants, reports, users, companies


class DBManager:

    # Create features
    def create_ab_test(self, company_id, name, description, metric):
        test = ab_tests(
            company_id=company_id,
            name=name,
            description=description,
            metric=metric,
            created_at=db.func.now()
        )
        db.session.add(test)
        db.session.commit()

    def create_variant(self, test_id, name, impressions, conversions, conversion_rate):
        variant = variants(
            test_id=test_id,
            name=name,
            impressions=impressions,
            conversions=conversions,
            conversion_rate=conversion_rate
        )
        db.session.add(variant)
        db.session.commit()

    def create_report(self, test_id, summary, p_value,significance, ai_recommendation):
        report = reports(
            test_id=test_id,
            p_value=p_value,
            significance=significance,
            summary=summary,
            ai_recommendation=ai_recommendation,
            created_at=db.func.now()
        )
        db.session.add(report)
        db.session.commit()

    def create_user(self, name, email):
        user = users(
            name=name,
            email=email)
        db.session.add(user)
        db.session.commit()

    def create_company(self, name, year, audience, url):
        company = companies(
            name=name,
            year=year,
            audience=audience,
            url=url)
        db.session.add(company)
        db.session.commit()


    # Read features
    def get_ab_tests(self, company_id):
        return ab_tests.query.filter_by(company_id=company_id).order_by(ab_tests.created_at.desc()).all()

    def get_recent_test(self, company_id):
        return ab_tests.query.filter_by(company_id=company_id).order_by(ab_tests.created_at.desc()).first()

    def get_test(self, test_id, company_id):
        return ab_tests.query.filter_by(id=test_id, company_id=company_id).first()

    def get_all_variants(self, company_id):
        return db.session.query(variants).join(ab_tests).filter(ab_tests.company_id == company_id).all()

    def get_variants(self, test_id):
        return variants.query.filter_by(test_id=test_id).all()

    def get_all_reports(self):
        return reports.query.all()

    def get_report(self, test_id):
        return reports.query.filter_by(test_id=test_id).first()

    def get_users(self):
        return users.query.all()

    def get_user(self, user_id):
        return users.query.filter_by(id=user_id).first()

    def get_companies(self):
        return companies.query.all()

    def get_company(self, company_id):
        return companies.query.filter_by(id=company_id).first()


    # Update features
    def update_ab_test(self, test_id, name, description, metric):
        test = ab_tests.query.filter_by(id=test_id).first()
        test.name = name
        test.description = description
        test.metric = metric
        db.session.commit()

    def update_variant(self, variant_id, impressions, conversions, conversion_rate):
        variant = variants.query.filter_by(id=variant_id).first()
        variant.impressions = impressions
        variant.conversions = conversions
        variant.conversion_rate = conversion_rate
        db.session.commit()

    def update_report(self, report_id, summary, significance, ai_recommendation):
        report = reports.query.filter_by(id=report_id).first()
        report.summary = summary
        report.significance = significance
        db.session.commit()

    def update_user(self, user_id, name, email):
        user = users.query.filter_by(id=user_id).first()
        user.name = name
        user.email = email
        db.session.commit()

    def update_company(self, company_id, name, year, audience, website):
        company = companies.query.filter_by(id=company_id).first()
        company.name = name
        company.year = year
        company.audience = audience
        company.website = website
        db.session.commit()


    # Delete features
    def delete_ab_test(self, test_id):
        self.delete_all_variants(test_id)
        ab_tests.query.filter(ab_tests.id == test_id).delete()
        db.session.commit()

    def delete_variant(self, variant_id):
        variants.query.filter(variants.id == variant_id).delete()
        db.session.commit()

    def delete_all_variants(self, test_id):
        variants.query.filter(variants.test_id == test_id).delete()
        db.session.commit()

    def delete_report(self, report_id):
        reports.query.filter(reports.id == report_id).delete()
        db.session.commit()

    def delete_user(self, user_id):
        users.query(users).filter(users.id == user_id).delete()
        db.session.commit()

    def delete_company(self, company_id):
        companies.query.filter(companies.id == company_id).delete()
        db.session.commit()
