# Lab 4: Search Queries in SQL
Student: Mohamed hassan teama (ID: 2304266)

## Requirements
MySQL Server and client, Python 3.10 or newer.

## Problem 1 (database `company`)
Run these in the main folder:
```
mysql -u root -p < problem1_DDL.sql
mysql -u root -p < problem1_DML.sql
mysql -u root -p -t -vvv --force < problem1_Queries.sql > problem1_Answers.txt 2>&1
```
The last command runs Q1.1 to Q1.12 and saves the SQL, the output and the error messages in `problem1_Answers.txt`.

## Problem 2 (database `library`)
```
mysql -u root -p < problem2_DDL.sql
mysql -u root -p < problem2_DML.sql
mysql -u root -p library < problem2_Queries.sql
```

## Website
```
cd website
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Open `.env` and write your MySQL password (and the other values). Then run:
```
python app.py
```
Open http://127.0.0.1:5000/library

| Page | URL | Query |
|---|---|---|
| Library (Lab 3: show, add, edit, delete) | /library | |
| Search books (bonus: prepared statement) | /library/search | F2.1 |
| Catalogue | /library/page/F2.2 | F2.2 |
| Reports | /library/page/F2.3 | F2.3 |
| Loans | /library/page/F2.4 | F2.4 |
| Most borrowed | /library/page/F2.5 | F2.5 |
| Authors and books | /library/page/F2.6 | F2.6 |

The search page (F2.1) sends the typed values as `%s` placeholders, never inside the SQL text. Pages F2.2 to F2.6 read their SQL from `problem2_Queries.sql`.