from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ab_tests(db.Model):
    __tablename__ = 'ab_tests'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    metric = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    __repr__ = lambda self: f'<Ab_Test {self.id}>'

    __str__ = lambda self: f'{self.id}'


class variants(db.Model):
    __tablename__ = 'variants'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('ab_tests.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    impressions = db.Column(db.Integer, nullable=False)
    conversions = db.Column(db.Integer, nullable=False)
    conversion_rate = db.Column(db.Float, nullable=False)

    __repr__ = lambda self: f'<Variant {self.id}>'

    __str__ = lambda self: f'{self.id}'


class reports(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('ab_tests.id'), nullable=False)
    p_value = db.Column(db.Float, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    significance = db.Column(db.Boolean, nullable=False)
    increase_percent = db.Column(db.Float, nullable=True)
    ai_recommendation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    __repr__ = lambda self: f'<Report {self.id}>'

    __str__ = lambda self: f'{self.id}'


class users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for existing users
    llm_model = db.Column(db.String(100), nullable=False, default='openai-gpt-4o-mini')

    __repr__ = lambda self: f'<User {self.name}>'

    __str__ = lambda self: f'{self.name} - {self.email}'


class companies(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    audience = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(255), nullable=False)

    __repr__ = lambda self: f'<User {self.name}>'

    __str__ = lambda self: f'{self.name} - {self.email}'
