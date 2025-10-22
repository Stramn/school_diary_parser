# school_diary_parser
Parser for schools.by. Collects grades of one student, stores them in JSON file and calculates average mark.

## Installation

### Prerequisites

- Python 3.8 or higher

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Stramn/school_diary_parser.git
cd school_diary_parser
```

2. (Optional) Create and activate virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
```
```bash
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Environment Configuration:
    - Create .env file
    - edit the .env file with your actual configuration values:
        LOGIN = "your_login"
        PASSWORD = "your_password"

## Usage 

```bash
python scraper.py 
```
collects marks from your account on schools.by,
creates marks.json file and fills it with marks
```bash
python calculate.py
``` 
calculates average marks from marks.json