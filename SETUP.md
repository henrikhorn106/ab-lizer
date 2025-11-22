# AB Lizer - Setup & Installation Guide

## 📁 Neue modulare Struktur

```
ab-lizer/
├── app.py                      # Application Factory (Flask App)
├── config.py                   # Konfiguration (Dev/Test/Prod)
├── requirements.txt            # Python Dependencies
│
├── services/                   # Business Logic Layer
│   ├── __init__.py
│   └── test_service.py        # Test/Variant/Report Logik
│
├── routes/                     # Flask Blueprints (MVC Controller)
│   ├── __init__.py
│   ├── home.py                # Dashboard Routes
│   ├── tests.py               # Tests & Variants Routes
│   └── settings.py            # User/Company Settings Routes
│
├── data/                       # Data Layer
│   ├── models.py              # SQLAlchemy ORM Models
│   ├── db_manager.py          # Database Operations
│   └── database.db            # SQLite Database
│
├── utils/                      # Utility Functions
│   └── significance_calculator.py
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html
│   ├── index.html
│   ├── tests.html
│   ├── detail.html
│   └── settings.html
│
└── static/                     # CSS, JS, Images
    ├── style.css
    ├── modal_test.js
    ├── modal_variant.js
    └── logo_ab-lizer.png
```

## 🚀 Installation

### 1. Virtual Environment erstellen (empfohlen)

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Aktivieren (Windows)
venv\Scripts\activate
```

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 3. Environment Variablen konfigurieren (optional)

```bash
# .env.example zu .env kopieren
cp .env.example .env

# .env bearbeiten und anpassen
nano .env
```

### 4. Anwendung starten

```bash
# Direkter Start (Development)
python app.py

# Oder mit Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Die Anwendung läuft jetzt auf: **http://127.0.0.1:5000**

## 🏗️ Architektur-Änderungen

### Application Factory Pattern

**Vorher:** Alle Routes in `app.py` (262 Zeilen)
**Nachher:** Modulare Blueprints + Application Factory (76 Zeilen)

```python
# app.py (vereinfacht)
from config import config
from routes import register_blueprints

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    register_blueprints(app)

    return app
```

### Blueprints (MVC Controller)

Routes sind jetzt in separate Blueprints aufgeteilt:

- **`routes/home.py`**: Dashboard (/, /home/...)
- **`routes/tests.py`**: Tests & Variants (/tests/...)
- **`routes/settings.py`**: User & Company Settings (/settings/...)

### Service Layer (Business Logic)

Business Logic aus den Routes extrahiert:

- **`services/test_service.py`**:
  - `create_test()`, `create_variants_with_data()`
  - `create_report()`, `update_test()`, `delete_test()`
  - `get_dashboard_stats()`, `get_recent_test_data()`

### Configuration Management

Drei Umgebungen unterstützt:

- **Development**: SQLite, Debug Mode
- **Testing**: In-Memory DB, No CSRF
- **Production**: Env-based DB URL, No Debug

## 📝 URL-Änderungen durch Blueprints

Templates verwenden jetzt Blueprint-Namen in `url_for()`:

```jinja2
<!-- Vorher -->
{{ url_for('home_page') }}
{{ url_for('tests_page', user_id=1) }}
{{ url_for('settings', user_id=1) }}

<!-- Nachher -->
{{ url_for('home.home_page') }}
{{ url_for('tests.tests_page', user_id=1) }}
{{ url_for('settings.settings_page', user_id=1) }}
```

## 🧪 Testing (zukünftig)

```bash
# Unit Tests ausführen
pytest

# Mit Coverage Report
pytest --cov=. --cov-report=html
```

## 📊 Vorteile der Modularisierung

✅ **Separation of Concerns**: Business Logic getrennt von Routes
✅ **Testbarkeit**: Services können unabhängig getestet werden
✅ **Skalierbarkeit**: Neue Features einfach als Blueprints hinzufügen
✅ **Wartbarkeit**: Kleinere, fokussierte Dateien statt Monolith
✅ **Configuration**: Verschiedene Umgebungen (Dev/Test/Prod)
✅ **Wiederverwendbarkeit**: Services können von mehreren Routes genutzt werden

## 🔜 Nächste Schritte

1. **Unit Tests schreiben** (`tests/test_significance_calculator.py`)
2. **API Blueprint hinzufügen** (`routes/api.py` für REST API)
3. **Authentication** implementieren (statt hardcoded `user_id=1`)
4. **Logging** konfigurieren (Flask-Logging)
5. **Error Handling** verbessern (Custom Error Pages)
6. **Database Migrations** mit Alembic

## 🐛 Troubleshooting

### Import Errors

```bash
# Stelle sicher, dass du im richtigen Verzeichnis bist
cd /path/to/ab-lizer

# Virtual Environment aktiviert?
source venv/bin/activate

# Dependencies installiert?
pip install -r requirements.txt
```

### Template Not Found

Die Templates sind jetzt Blueprint-aware. Stelle sicher, dass alle `url_for()` Aufrufe den Blueprint-Namen enthalten (z.B. `'home.home_page'` statt `'home_page'`).

### Database Errors

```bash
# Datenbank neu erstellen
rm data/database.db
python app.py  # Erstellt automatisch neue DB
```
