# Warbler

To get this application running, make sure you do the following in the Terminal:

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `createdb warbler`
5. `python seed.py`
6. `flask run`

**Create** local Database `postgresql://localhost/<DataBaseName>?user=<username>&password=<password>`

**Note**:
If you are using Python 3.8 instead of 3.7, then you will have issues with installing some of the packages in the requirements.txt file into your virtual environment.
For Python 3.8 pepole, we recommend deleting pyscopg2-binary from the requirements.txt file, and using pip install pyscopg2-binary in the terminal in order to successfully install this package.

**To run the tests**:
`python -m unittest <name-of-python-file>`
