# Agrobot - Django Project
This is a Django project skeleton for the **Agrobot**.
It includes:
- Text, image and voice front-end (voice via browser Web Speech API)
- Rule-based symptom matching (difflib + symptom DB)
- Sentence construction via templates (NLTK-style simple approach)
- Grammar correction hook (language_tool_python if installed)
- Simple image-analysis using OpenCV (color-based heuristic)
- Django admin for superuser/admin management

IMPORTANT:
- Some libraries (googletrans, language_tool_python, speech recognition, OpenCV) may require internet or system-level dependencies.
- To run the project:
  1. Create a Python virtualenv with Python 3.8+.
  2. Install requirements: `pip install -r requirements.txt`
  3. Run migrations: `python manage.py migrate`
  4. Create superuser: `python manage.py createsuperuser`
  5. Run server: `python manage.py runserver`
- For voice support in the browser, use the included JS (Web Speech API).

