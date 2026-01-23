# AB Lizer

AB Lizer is a web application built with Python, Flask, and modern AI technologies that helps marketers and data teams evaluate and interpret A/B test results more intelligently.

## Features

- **User Authentication**: Secure login and registration with password hashing
- **Multi-tenant Architecture**: Company-based user organization
- **A/B Test Management**: Create, edit, and delete A/B tests
- **Variant Tracking**: Track multiple variants with impressions and conversions
- **Statistical Analysis**: Two-proportion z-test with Fisher's exact test fallback, p-values, and 95% confidence intervals
- **AI-Powered Insights**: Get AI-generated recommendations and test descriptions
- **Multi-Provider AI Support**: Choose between OpenAI, Anthropic, and Google models
- **Model Selection**: Users can select their preferred AI model (GPT-4o, Claude, Gemini variants)
- **Visual Dashboard**: Interactive charts and metrics for quick insights
- **Stakeholder Reports**: Comprehensive reporting page with exportable data
- **Detailed Analysis**: In-depth analysis pages for each test with visualizations

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask sessions with werkzeug password hashing
- **AI Integration**: LangChain with support for multiple providers:
  - OpenAI (GPT-4o, GPT-4o Mini, GPT-4 Turbo)
  - Anthropic (Claude Opus 4.5, Claude Sonnet 4.5, Claude Sonnet 3.7)
  - Google (Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash)
- **Structured Output**: Pydantic for AI response validation
- **Statistics**: SciPy for statistical analysis
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
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   GOOGLE_API_KEY=your-google-api-key-here
   ```

   - `SECRET_KEY`: A random string for Flask session encryption (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)
   - `GOOGLE_API_KEY`: Your Google API key (optional)

   Note: At least one AI provider API key is required for AI features to work.

5. **Run the application**
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

6. **Select Your Preferred AI Model**
   - Go to Settings
   - Choose from available AI models based on your configured API keys
   - Your selection will be used for all AI-generated content

## Project Structure

```
ab-lizer/
├── app.py                    # Main Flask application
├── data/
│   ├── database.db          # SQLite database
│   ├── models.py            # SQLAlchemy database models
│   ├── db_manager.py        # Database operations
│   └── migrations/          # Database migration scripts
│       └── add_llm_model.py # LLM model field migration
├── routes/
│   ├── ai.py                # AI recommendation and description generation
│   └── llm_config.py        # LLM provider configuration and selection
├── utils/
│   └── utils.py             # Statistical calculations (z-test, Fisher's exact)
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── index.html          # Dashboard
│   ├── tests.html          # Tests listing page
│   ├── analysis.html       # Test analysis page
│   ├── edit.html           # Edit test page
│   ├── reports.html        # Stakeholder reports page
│   └── settings.html       # User settings page
├── static/                  # Static files (CSS, JS, images)
│   ├── style.css           # Main stylesheet
│   ├── analysis_charts.js  # Analysis visualization
│   ├── report_generator.js # Report generation logic
│   ├── report_exporter.js  # PDF export functionality
│   └── ...                 # Additional JS modules
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Models

- **users**: User accounts with authentication and LLM model preference
- **companies**: Company/organization information
- **ab_tests**: A/B test definitions
- **variants**: Test variants with metrics (impressions, conversions, conversion rate)
- **reports**: Statistical analysis results and AI recommendations (stored as JSON)

## Statistical Analysis

AB Lizer uses rigorous statistical methods to evaluate A/B test results:

- **Two-Proportion Z-Test**: Used when sample sizes are sufficient (min 5 counts per cell)
- **Fisher's Exact Test**: Fallback for small sample sizes
- **Metrics Calculated**:
  - P-value for statistical significance
  - 95% Confidence intervals
  - Effect size (absolute difference)
  - Relative change percentage

## Security Features

- Password hashing using werkzeug.security
- Session-based authentication
- Protected routes with @login_required decorator
- Unique email constraints for user accounts
- SQL injection prevention via SQLAlchemy ORM
- API keys stored in environment variables

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout

### Dashboard
- `GET /` - Main dashboard
- `POST /home/<user_id>` - Create test from dashboard
- `POST /home/variants/<user_id>/<test_id>` - Create variants from dashboard

### Tests
- `GET /tests/<user_id>` - View all tests
- `POST /tests/<user_id>` - Create new test
- `POST /tests/<user_id>/<test_id>` - Delete test
- `POST /tests/variants/<user_id>/<test_id>` - Create variants

### Analysis
- `GET /analysis/<user_id>/<test_id>` - View test analysis (AI recommendations are generated automatically when creating/updating variants)

### Edit
- `GET /edit/<user_id>/<test_id>` - Edit test page
- `POST /edit/<user_id>/<test_id>` - Update test and variants

### Reports
- `GET /reports/<user_id>` - Stakeholder reports page

### Settings
- `GET /settings/<user_id>` - User settings page
- `POST /settings/<user_id>` - Update user information
- `POST /settings/<user_id>/<company_id>` - Update company information

### API
- `GET /api/test-ratios/<company_id>` - Get test win/lose/other ratios
- `POST /api/generate-description` - Generate AI test description

## Development

To run in development mode with auto-reload:
```python
app.run(debug=True)
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License.
