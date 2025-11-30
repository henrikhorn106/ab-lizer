# AB Lizer

AB Lizer is a web application built with Python, Flask, and modern AI technologies that helps marketers and data teams evaluate and interpret A/B test results more intelligently.

## Features

- **User Authentication**: Secure login and registration with password hashing
- **Multi-tenant Architecture**: Company-based user organization
- **A/B Test Management**: Create, edit, and delete A/B tests
- **Variant Tracking**: Track multiple variants with impressions and conversions
- **Statistical Analysis**: Automated p-value calculation and significance testing
- **AI-Powered Insights**: Get AI-generated recommendations and test descriptions
- **Visual Dashboard**: Interactive charts and metrics for quick insights
- **Detailed Reporting**: Comprehensive analysis pages for each test

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask sessions with werkzeug password hashing
- **AI Integration**: OpenAI API for recommendations and insights
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Custom visualization components

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ab-lizer
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-api-key-here
   ```

   - `SECRET_KEY`: A random string for Flask session encryption (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `OPENAI_API_KEY`: Your OpenAI API key for AI features

5. **Run the database migration** (if upgrading from a previous version)
   ```bash
   python migrate_add_password.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## Getting Started

1. **Register an Account**
   - Navigate to `/register`
   - Fill in your personal information (name, email, password)
   - Provide your company information (name, founded year, target audience, website)
   - Click "Create Account"

2. **Log In**
   - Navigate to `/login`
   - Enter your email and password
   - Click "Login"

3. **Create Your First A/B Test**
   - On the dashboard, click "Add AB Test"
   - Enter test name, description, and main metric
   - Click "Create"

4. **Add Variants**
   - Click "Add Variants" for your test
   - Enter impressions and conversions for Variant A and B
   - Click "Create"

5. **View Analysis**
   - Navigate to the analysis page for your test
   - View statistical significance, p-values, and conversion rates
   - Get AI-powered recommendations for your test results

## Project Structure

```
ab-lizer/
├── app.py                    # Main Flask application
├── data/
│   ├── models.py            # SQLAlchemy database models
│   └── db_manager.py        # Database operations
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── index.html          # Dashboard
│   ├── tests.html          # Tests listing page
│   ├── analysis.html       # Test analysis page
│   ├── edit.html           # Edit test page
│   └── settings.html       # User settings page
├── static/                  # Static files (CSS, JS, images)
├── migrate_add_password.py  # Database migration script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Models

- **users**: User accounts with authentication
- **companies**: Company/organization information
- **ab_tests**: A/B test definitions
- **variants**: Test variants with metrics
- **reports**: Statistical analysis results

## Security Features

- Password hashing using werkzeug.security
- Session-based authentication
- Protected routes with @login_required decorator
- Unique email constraints for user accounts
- SQL injection prevention via SQLAlchemy ORM

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout

### Dashboard
- `GET /` - Main dashboard
- `POST /home/<user_id>` - Create test from dashboard
- `POST /home/<user_id>/<test_id>` - Create variant from dashboard

### Tests
- `GET /tests/<user_id>` - View all tests
- `POST /tests/<user_id>` - Create new test
- `POST /tests/<user_id>/<test_id>` - Delete test
- `POST /tests/variants/<user_id>/<test_id>` - Create variants

### Analysis
- `GET /analysis/<user_id>/<test_id>` - View test analysis
- `POST /analysis/<user_id>/<test_id>` - Generate AI recommendation

### Edit
- `GET /edit/<user_id>/<test_id>` - Edit test page
- `POST /edit/<user_id>/<test_id>` - Update test and variants

### Settings
- `GET /settings/<user_id>` - User settings page
- `POST /settings/<user_id>` - Update user information
- `POST /settings/<user_id>/<company_id>` - Update company information

### AI Features
- `POST /generate-description` - Generate AI test description

## Development

To run in development mode with auto-reload, uncomment the last line in `app.py`:
```python
app.run(debug=True)
```

## Migration from Previous Versions

If you're upgrading from a version without authentication:

1. Run the migration script:
   ```bash
   python migrate_add_password.py
   ```

2. Existing users will need to:
   - Register new accounts through `/register`
   - Or have passwords set manually in the database

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License.