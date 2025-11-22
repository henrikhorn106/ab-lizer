"""
Test Service
Business logic for AB tests, variants, and reports
"""

from data.db_manager import DBManager
from utils.significance_calculator import two_proportion_z_test


class TestService:
    """Service class for AB test operations"""

    def __init__(self):
        self.db_manager = DBManager()

    def create_test(self, user_id, name, description, metric):
        """
        Create a new AB test

        Args:
            user_id: ID of the user creating the test
            name: Name of the test
            description: Description of the test
            metric: Metric being tested

        Returns:
            Created test object
        """
        company = self.db_manager.get_company(user_id)
        return self.db_manager.create_ab_test(company.id, name, description, metric)

    def create_variants_with_data(self, test_id, impressions_a, conversions_a, impressions_b, conversions_b):
        """
        Create both variants (A and B) with their data and generate report

        Args:
            test_id: ID of the test
            impressions_a: Impressions for variant A
            conversions_a: Conversions for variant A
            impressions_b: Impressions for variant B
            conversions_b: Conversions for variant B
        """
        # Create Variant A
        conversion_rate_a = round(float(conversions_a) / float(impressions_a) * 100, 2)
        self.db_manager.create_variant(test_id, "Variant A", impressions_a, conversions_a, conversion_rate_a)

        # Create Variant B
        conversion_rate_b = round(float(conversions_b) / float(impressions_b) * 100, 2)
        self.db_manager.create_variant(test_id, "Variant B", impressions_b, conversions_b, conversion_rate_b)

        # Generate report with significance calculation
        self.create_report(test_id, impressions_a, conversions_a, impressions_b, conversions_b)

    def create_report(self, test_id, impressions_a, conversions_a, impressions_b, conversions_b):
        """
        Create a report with significance calculation

        Args:
            test_id: ID of the test
            impressions_a: Impressions for variant A
            conversions_a: Conversions for variant A
            impressions_b: Impressions for variant B
            conversions_b: Conversions for variant B
        """
        # Calculate significance using two-proportion z-test
        data = two_proportion_z_test(
            int(impressions_a),
            int(conversions_a),
            int(impressions_b),
            int(conversions_b)
        )

        # Generate summary
        summary = "Test was significant." if data["significant"] else "Test was not significant."

        # Create report in database
        self.db_manager.create_report(
            test_id,
            summary,
            data["p_value"],
            round(data["significant"], 2),
            "-"  # AI recommendation placeholder
        )

    def update_test(self, test_id, name, description, metric):
        """Update an existing test"""
        return self.db_manager.update_ab_test(test_id, name, description, metric)

    def update_variants_bulk(self, variant_data):
        """
        Update multiple variants at once

        Args:
            variant_data: List of tuples (variant_id, impressions, conversions)
        """
        for variant_id, impressions, conversions in variant_data:
            conversion_rate = round(float(conversions) / float(impressions) * 100, 2)
            self.db_manager.update_variant(variant_id, impressions, conversions, conversion_rate)

    def delete_test(self, test_id):
        """Delete a test and all associated data"""
        return self.db_manager.delete_ab_test(test_id)

    def get_dashboard_stats(self):
        """
        Get aggregated statistics for dashboard

        Returns:
            Dictionary with total_tests, total_impressions, total_conversions
        """
        total_tests = len(self.db_manager.get_ab_tests())
        total_variants = self.db_manager.get_all_variants()

        total_impressions = 0
        total_conversions = 0
        for variant in total_variants:
            total_impressions += variant.impressions
            total_conversions += variant.conversions

        return {
            'total_tests': total_tests,
            'total_impressions': total_impressions,
            'total_conversions': total_conversions
        }

    def get_recent_test_data(self):
        """
        Get data for the most recent test

        Returns:
            Dictionary with test, variants, and report
        """
        test = self.db_manager.get_recent_test()
        if not test or len(test) == 0:
            return None

        test_obj = test[0]
        variants = self.db_manager.get_variants(test_obj.id)
        report = self.db_manager.get_report(test_obj.id)

        # Calculate conversion rates
        for variant in variants:
            if variant.impressions > 0:
                variant.conversion_rate = round(float(variant.conversions) / float(variant.impressions) * 100, 2)

        return {
            'test': test,
            'variants': variants,
            'report': report
        }
