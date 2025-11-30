"""
Project AB Lizer

AB Lizer is a web application built with Python, Flask, and modern AI technologies
that helps marketers and data teams evaluate and interpret A/B test results more intelligently.

While traditional A/B testing tools show only raw numbers and significance values,
this project goes further by using Generative AI and machine learning to generate
human-readable insights, predict outcomes, and suggest data-driven improvements for future experiments.

The platform provides a clean API with full CRUD functionality,
a connected database for test storage, and an AI layer that turns data into actionable recommendations.
"""

import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

from data.db_manager import DBManager
from data.models import db, users
from routes.ai import generate_ai_recommendation, generate_ai_summary, generate_test_description
from utils.utils import two_proportion_z_test, transform_test_data, calculate_increase_percent

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

db.init_app(app)

db_manager = DBManager()


# =================================================================
# AUTHENTICATION
# =================================================================

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# =================================================================
# HELPER FUNCTIONS
# Having utils.py or helper.py script that gets imported here would be better
# =================================================================

@app.template_filter('initials')
def get_initials(name):
    """Extract initials from a full name"""
    if not name:
        return ''

    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return ''


# =================================================================
# LOGIN & REGISTRATION
# =================================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Get user by email
        user = db.session.query(users).filter_by(email=email).first()

        if user and user.password_hash and check_password_hash(user.password_hash, password):
            # Login successful
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Invalid email or password', 'error')

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration"""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        company_name = request.form.get("company_name")
        company_year = request.form.get("company_year")
        company_audience = request.form.get("company_audience")
        company_website = request.form.get("company_website")

        # Check if user already exists
        existing_user = db.session.query(users).filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        # Create company first
        company = db_manager.create_company(
            name=company_name,
            year=int(company_year),
            audience=company_audience,
            website=company_website
        )

        # Create user with hashed password
        password_hash = generate_password_hash(password)

        new_user = users(
            name=name,
            email=email,
            password_hash=password_hash,
            company_id=company.id
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


# =================================================================
# INDEX
# =================================================================

@app.route("/")
@login_required
def home_page():
    user_id = session.get('user_id')
    user = db_manager.get_user(user_id)

    total_tests = len(db_manager.get_ab_tests(user.company_id))
    total_variants = db_manager.get_all_variants(user.company_id)
    total_impressions = 0
    total_conversions = 0
    for variant in total_variants:
        total_impressions += variant.impressions
        total_conversions += variant.conversions

    # Data for the most recent test
    test = db_manager.get_recent_test(user.company_id)
    try:
        variants = db_manager.get_variants(test.id)
        report = db_manager.get_report(test.id)
    except AttributeError:
        variants = []
        report = None

    for variant in variants:
        # avoid division by zero
        if variant.impressions:
            variant.conversion_rate = round(float(variant.conversions) / float(variant.impressions) * 100, 2)
        else:
            variant.conversion_rate = 0.0

    return render_template("index.html",
                           user=user,
                           total_tests=total_tests,
                           total_impressions=total_impressions,
                           total_conversions=total_conversions,
                           test=test,
                           variants=variants,
                           report=report
                           )


@app.route("/home/<int:user_id>", methods=["POST"])
@login_required
def home_page_create_test(user_id):
    user = db_manager.get_user(user_id)
    company = db_manager.get_company(user.company_id)

    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")

    db_manager.create_ab_test(company.id, name, description, metric)

    return redirect(url_for("home_page", user_id=user_id))


@app.route("/home/variants/<int:user_id>/<int:test_id>", methods=["POST"])
@login_required
def home_page_create_variant(user_id, test_id):

    # Create Variant A
    name = "Variant A"
    impressions_a = request.form.get("var1_impressions")
    conversions_a = request.form.get("var1_conversions")
    conversion_rate = round(float(conversions_a) / float(impressions_a) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_a, conversions_a, conversion_rate)

    # Create Variant B
    name = "Variant B"
    impressions_b = request.form.get("var2_impressions")
    conversions_b = request.form.get("var2_conversions")
    conversion_rate = round(float(conversions_b) / float(impressions_b) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_b, conversions_b, conversion_rate)

    # Calculate significance
    report_data = two_proportion_z_test(
        int(impressions_a),
        int(conversions_a),
        int(impressions_b),
        int(conversions_b)
    )


    # Transform data for AI

    # 1. Company data
    user = db_manager.get_user(user_id)
    company = db_manager.get_company(user.company_id)
    company_data = {
        "name": company.name,
        "audience": company.audience,
        "year": company.year
    }
    # 2. Test data
    test_data = db_manager.get_test(test_id, company.id)
    transform_test_data(test_data, db_manager.get_variants(test_id), report_data)

    # 3. Report data
    ai_recommendation = generate_ai_recommendation(test_data, report_data, company_data)
    ai_summary = generate_ai_summary(ai_recommendation)

    # Calculate increase percentage
    increase_percent = calculate_increase_percent(
        report_data["conv_rate_a"],
        report_data["conv_rate_b"]
    )

    # Create report
    db_manager.create_report(test_id,
                             summary=ai_summary,
                             p_value=round(report_data["p_value"], 3),
                             significance=report_data["significant"],
                             increase_percent=increase_percent,
                             ai_recommendation=ai_recommendation)

    return redirect(url_for("home_page", user_id=user_id))


# =================================================================
# TESTS & VARIANTS
# =================================================================

@app.route("/tests/<int:user_id>")
@login_required
def tests_page(user_id):
    user = db_manager.get_user(user_id)
    tests = db_manager.get_ab_tests(user.company_id)
    variants = db_manager.get_all_variants(user.company_id)
    reports = db_manager.get_all_reports()

    return render_template("tests.html",
                           user=user,
                           tests=tests,
                           variants=variants,
                           reports=reports
                           )


@app.route("/tests/<int:user_id>", methods=["POST"])
@login_required
def tests_page_create_test(user_id):
    user = db_manager.get_user(user_id)
    company = db_manager.get_company(user.company_id)

    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")

    db_manager.create_ab_test(company.id, name, description, metric)

    return redirect(url_for("tests_page", user_id=user_id))


@app.route("/tests/<int:user_id>/<int:test_id>", methods=["POST"])
@login_required
def tests_page_delete_test(user_id, test_id):
    db_manager.delete_ab_test(test_id)

    return redirect(url_for("tests_page", user_id=user_id))


@app.route("/tests/variants/<int:user_id>/<int:test_id>", methods=["POST"])
@login_required
def tests_page_create_variant(user_id, test_id):

    # Create Variant A
    name = "Variant A"
    impressions_a = request.form.get("var1_impressions")
    conversions_a = request.form.get("var1_conversions")
    conversion_rate = round(float(conversions_a) / float(impressions_a) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_a, conversions_a, conversion_rate)

    # Create Variant B
    name = "Variant B"
    impressions_b = request.form.get("var2_impressions")
    conversions_b = request.form.get("var2_conversions")
    conversion_rate = round(float(conversions_b) / float(impressions_b) * 100, 2)
    db_manager.create_variant(test_id, name, impressions_b, conversions_b, conversion_rate)

    return redirect(url_for("tests_page", user_id=user_id))


# =================================================================
# ANALYSIS PAGE
# =================================================================

@app.route("/analysis/<int:user_id>/<int:test_id>")
@login_required
def analysis_page(user_id, test_id):
    user = db_manager.get_user(user_id)
    test = db_manager.get_test(test_id, user.company_id)
    variants = db_manager.get_variants(test_id)
    report = db_manager.get_report(test_id)

    # Convert variants to dictionaries for JSON serialization
    variants_data = []
    if variants and len(variants) >= 2:
        for variant in variants:
            # guard conversion rate computation
            if variant.impressions:
                conversion_rate = variant.conversions / variant.impressions
            else:
                conversion_rate = 0.0
            variants_data.append({
                'id': variant.id,
                'name': variant.name,
                'impressions': variant.impressions,
                'conversions': variant.conversions,
                'conversion_rate': conversion_rate
            })

        # Calculate relative uplift and other metrics
        variant_a = variants[0]
        variant_b = variants[1]

        # Calculate conversion rates as decimals with zero-division guards
        conv_rate_a = (variant_a.conversions / variant_a.impressions) if variant_a.impressions else 0.0
        conv_rate_b = (variant_b.conversions / variant_b.impressions) if variant_b.impressions else 0.0

        # Calculate standard errors for normal distribution
        import math
        std_error_a = math.sqrt((conv_rate_a * (1 - conv_rate_a)) / variant_a.impressions) if variant_a.impressions else 0.0
        std_error_b = math.sqrt((conv_rate_b * (1 - conv_rate_b)) / variant_b.impressions) if variant_b.impressions else 0.0

        # Calculate 95% confidence intervals
        z_score_95 = 1.96
        ci_lower_a = max(0, conv_rate_a - z_score_95 * std_error_a)
        ci_upper_a = min(1, conv_rate_a + z_score_95 * std_error_a)
        ci_lower_b = max(0, conv_rate_b - z_score_95 * std_error_b)
        ci_upper_b = min(1, conv_rate_b + z_score_95 * std_error_b)

        # Additional analysis data
        analysis_data = {
            'total_sessions': variant_a.impressions + variant_b.impressions,
            'total_conversions': variant_a.conversions + variant_b.conversions,
            'variant_a_sample_size': variant_a.impressions,
            'variant_b_sample_size': variant_b.impressions,
            'distribution_data': {
                'variant_a': {
                    'mean': conv_rate_a,
                    'std_error': std_error_a,
                    'ci_lower': ci_lower_a,
                    'ci_upper': ci_upper_a
                },
                'variant_b': {
                    'mean': conv_rate_b,
                    'std_error': std_error_b,
                    'ci_lower': ci_lower_b,
                    'ci_upper': ci_upper_b
                }
            }
        }
    else:
        analysis_data = None

    # Convert report to dictionary for JSON serialization
    report_data = None
    if report:
        report_data = {
            'id': report.id,
            'p_value': report.p_value,
            'significance': report.significance,
            'increase_percent': report.increase_percent,
            'summary': report.summary,
            'ai_recommendation': report.ai_recommendation
        }

    return render_template("analysis.html",
                           user=user,
                           test=test,
                           variants=variants,
                           variants_data=variants_data,
                           report=report,
                           report_data=report_data,
                           analysis_data=analysis_data)


# =================================================================
# EDIT TEST PAGE
# =================================================================

@app.route("/edit/<int:user_id>/<int:test_id>")
@login_required
def edit_test_page(user_id, test_id):
    user = db_manager.get_user(user_id)
    test = db_manager.get_test(test_id, user.company_id)
    variants = db_manager.get_variants(test_id)
    report = db_manager.get_report(test_id)

    return render_template("edit.html", user=user, test=test, variants=variants, report=report)


@app.route("/edit/<int:user_id>/<int:test_id>", methods=["POST"])
@login_required
def edit_test_page_update_variant(user_id, test_id):
    # Update test
    name = request.form.get("name")
    description = request.form.get("description")
    metric = request.form.get("metric")
    db_manager.update_ab_test(test_id, name, description, metric)

    # Update variants (multiple at once)
    variant_ids = request.form.getlist("variant_id[]")
    sessions_list = request.form.getlist("sessions[]")
    conversions_list = request.form.getlist("conversions[]")

    # Iterate through variant_ids and update their impressions and conversions
    for i in range(len(variant_ids)):
        variant_id = variant_ids[i]
        impressions = sessions_list[i]
        conversions = conversions_list[i]
        conversion_rate = round(float(conversions) / float(impressions) * 100, 2)
        db_manager.update_variant(variant_id, impressions, conversions, conversion_rate)

    # Get variant data
    variants = db_manager.get_variants(test_id)
    impressions_a = variants[0].impressions
    conversions_a = variants[0].conversions
    impressions_b = variants[1].impressions
    conversions_b = variants[1].conversions

    # Calculate significance
    report_data = two_proportion_z_test(
        int(impressions_a),
        int(conversions_a),
        int(impressions_b),
        int(conversions_b)
    )

    # Transform data for AI

    # 1. Company data
    user = db_manager.get_user(user_id)
    company = db_manager.get_company(user.company_id)
    company_data = {
        "name": company.name,
        "audience": company.audience,
        "year": company.year
    }
    # 2. Test data
    test_data = db_manager.get_test(test_id, company.id)
    transform_test_data(test_data, db_manager.get_variants(test_id), report_data)

    # 3. Report data
    ai_recommendation = generate_ai_recommendation(test_data, report_data, company_data)
    ai_summary = generate_ai_summary(ai_recommendation)

    # Calculate increase percentage
    increase_percent = calculate_increase_percent(
        report_data["conv_rate_a"],
        report_data["conv_rate_b"]
    )

    # Update report
    report = db_manager.get_report(test_id)
    db_manager.update_report(report.id,
                             summary=ai_summary,
                             p_value=round(report_data["p_value"], 3),
                             significance=report_data["significant"],
                             increase_percent=increase_percent,
                             ai_recommendation=ai_recommendation)

    return redirect(url_for("edit_test_page", user_id=user_id, test_id=test_id))


# =================================================================
# API
# =================================================================

@app.route("/api/test-ratios/<int:company_id>")
def get_test_ratios(company_id):
    """
    Calculate and return the ratio of winning, losing, and other tests.

    Winning: significant AND conversion increased (Variant B > Variant A)
    Losing: significant AND conversion decreased (Variant B < Variant A)
    Other: not significant
    """
    tests = db_manager.get_ab_tests(company_id)

    winning = 0
    losing = 0
    other = 0

    for test in tests:
        try:
            report = db_manager.get_report(test.id)
            variants = db_manager.get_variants(test.id)

            # Skip if no report or not enough variants
            if not report or len(variants) < 2:
                other += 1
                continue

            # Check if significant
            if report.significance:
                # Compare conversion rates (Variant A is index 0, Variant B is index 1)
                variant_a_rate = variants[0].conversion_rate
                variant_b_rate = variants[1].conversion_rate

                if variant_b_rate > variant_a_rate:
                    winning += 1
                else:
                    losing += 1
            else:
                other += 1

        except (AttributeError, IndexError):
            other += 1

    total = winning + losing + other

    if total == 0:
        return jsonify({
            "winning": 0,
            "losing": 0,
            "other": 0,
            "winning_percent": 0,
            "losing_percent": 0,
            "other_percent": 0
        })

    return jsonify({
        "winning": winning,
        "losing": losing,
        "other": other,
        "winning_percent": round((winning / total) * 100, 1),
        "losing_percent": round((losing / total) * 100, 1),
        "other_percent": round((other / total) * 100, 1)
    })


@app.route("/api/generate-description", methods=["POST"])
def generate_description_api():
    """
    Generate an AI-powered description for an AB test based on its name.
    """
    data = request.get_json()
    test_name = data.get("test_name", "")

    if not test_name:
        return jsonify({"error": "Test name is required"}), 400

    try:
        description = generate_test_description(test_name)
        return jsonify({"description": description})
    except Exception as e:
        print(f"Error generating description: {str(e)}")
        return jsonify({"error": "Failed to generate description"}), 500


# =================================================================
# SETTINGS
# =================================================================

@app.route("/settings/<int:user_id>")
@login_required
def settings(user_id):
    user = db_manager.get_user(user_id)
    company = db_manager.get_company(user.company_id)

    return render_template("settings.html",
                           user=user,
                           company=company
                           )


@app.route("/settings/<int:user_id>", methods=["POST"])
@login_required
def update_user(user_id):
    name = request.form.get("name")
    email = request.form.get("email")
    db_manager.update_user(user_id, name, email)

    return redirect(url_for("settings", user_id=user_id))


@app.route("/settings/<int:user_id>/<int:company_id>", methods=["POST"])
@login_required
def update_company(user_id ,company_id):
    name = request.form.get("company_name")
    year = request.form.get("year")
    audience = request.form.get("audience")
    website = request.form.get("website")
    db_manager.update_company(company_id, name, year, audience, website)

    return redirect(url_for("settings", user_id=user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    # app.run()
