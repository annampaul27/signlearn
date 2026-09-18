# SignLearn

SignLearn is a Django web application for learning and practising sign language. It combines structured sign lessons with browser-based hand capture and machine-learning recognition, then uses the recognition results in practice activities and tests.

## Features

- User registration, login, dashboard, and progress history.
- Alphabet learning pages with sign images, descriptions, difficulty, and ordering.
- Basic sign content managed through Django models and the admin site.
- Browser hand-capture interface for real-time recognition.
- Practice sessions that compare a target letter with the predicted letter, record confidence, and award points.
- Alphabet tests with generated question sets, answers, scores, and accuracy results.
- Uploaded sign images and videos served from the Django media directory during development.

## Project Structure

| Path | Purpose |
| --- | --- |
| `config/` | Django project settings, URL routing, ASGI, and WSGI configuration |
| `accounts/` | Authentication and user dashboard views |
| `core/` | Home and about pages |
| `learning/` | Sign and alphabet learning content |
| `recognition/` | Browser recognition endpoints and ML prediction pipeline |
| `practice/` | Practice sessions and attempt scoring |
| `tests_app/` | Tests, questions, answers, and result tracking |
| `templates/` | Shared and app-specific HTML templates |
| `static/` | Shared CSS and JavaScript assets |
| `media/signs/` | Sign media files used by the learning content |
| `recognition/ml_models/` | Local recognition model files, not included by default |
| `adminpanel/`|Admin related operation CURD operation via forms |

## Routes

- `/` - Home page
- `/about/` - About page
- `/accounts/` - Registration, login, and account dashboard
- `/learn/` - Alphabet and sign details
- `/recognition/` - Recognition capture and prediction endpoints
- `/practice/` - Practice dashboard and capture session
- `/tests/` - Test list, test-taking, and results
- `/adminpanel/` - Django administration

## Requirements

- Python 3.10 or newer
- PostgreSQL 13 or newer
- A compatible browser with camera access for recognition and practice
- The trained recognition model files described below

## Local Setup

1. Create and activate a virtual environment:

   ```text
   python -m venv .venv
   .venv\\Scripts\\activate
   ```

2. Install dependencies:

   ```text
   pip install -r requirements.txt
   ```

3. Create a PostgreSQL database, then copy `.env.example` to `.env` and set the database credentials. The application reads environment variables directly; load the values in your shell or use a tool such as `python-dotenv` when running locally.

4. Apply migrations and create an administrator:

   ```text
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Start the development server:

   ```text
   python manage.py runserver
   ```

   Open <http://127.0.0.1:8000/> in a browser.

## Recognition Model Files

The recognition pipeline expects these files in `recognition/ml_models/`:

- `isl_mlp_model.pkl`
- `label_encoder.pkl`
- `scaler.pkl`

The model must accept a 126-value feature vector representing two hands, with 21 three-dimensional landmarks per hand. The model files are intentionally kept out of source control unless explicitly added to the repository.

## Development Notes

- Use Django admin to create `Sign` and `Test` records before using the learning and test flows.
- Camera-based features require browser permission and are intended for local development or a secure deployment context.
- Keep `.env` private. Never commit database passwords, Django secret keys, or other credentials.
- Run the test suite with:

  ```text
  python manage.py test
  ```

## License

No license has been specified yet.
