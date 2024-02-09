# mln-flask-backend-2

All refactored (REST-API) code is located within "\_\_init\_\_.py".

## Instructions

1. Clone the repo:

```bash
git clone https://github.com/Kaushal-Top5699/mln-backend
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source ./venv/bin/activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Create an empty "users" folder in the root directory of project.

5. Execute script:

```bash
python3 __init__.py
```

NOTE: `flask run` \(or `flask --app __init__.py run`\) will not work due to non-relative path imports, and can cause issues if the port 5000 is pre-occupied by another service.
