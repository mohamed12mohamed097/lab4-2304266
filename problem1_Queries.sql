USE company;

SELECT 'Q1.1 INSERT' AS question;
INSERT INTO employee VALUES ('777777777','Hana','Mostafa','1998-02-14','Alexandria','F',3800,'222222222',1);
INSERT INTO project VALUES (5,'Portal','Alexandria',1);
SELECT * FROM employee WHERE ssn='777777777';
SELECT * FROM project  WHERE Pnumber=5;
SELECT 'Next statement FAILS (error 1452): Dno 99 does not exist in DEPARTMENT, so the foreign key rejects the row and nothing is inserted.' AS note;
INSERT INTO employee VALUES ('888888888','Test','User','2000-01-01','Cairo','M',3000,NULL,99);

SELECT 'Q1.2 UPDATE' AS question;
UPDATE employee SET salary = salary * 1.10 WHERE Dno = 2;
SELECT ssn, fname, salary FROM employee WHERE Dno = 2;
UPDATE project SET Plocation = 'Giza' WHERE Pnumber = 2;
SELECT * FROM project WHERE Pnumber = 2;
SELECT 'Next statement FAILS (error 1452): the new Dno must already exist in DEPARTMENT.' AS note;
UPDATE employee SET Dno = 99 WHERE ssn = '333333333';

SELECT 'Q1.3 DELETE' AS question;
DELETE FROM dependent WHERE essn='222222222' AND dependent_name='Adam';
DELETE FROM works_on  WHERE essn='666666666' AND Pno=3;
SELECT 'Next statement FAILS (error 1451): department 2 is still referenced by employees (and project 3), so MySQL refuses the delete.' AS note;
DELETE FROM department WHERE Dnumber = 2;
SELECT 'Correct order (inside a transaction, rolled back so the data stays): first move or delete the rows that reference the department (employees, then projects), then delete the department.' AS note;
START TRANSACTION;
UPDATE employee SET Dno = 1 WHERE Dno = 2;
UPDATE project  SET Dno = 1 WHERE Dno = 2;
DELETE FROM department WHERE Dnumber = 2;
SELECT * FROM department;
ROLLBACK;
SELECT * FROM department;
SELECT 'DELETE without WHERE removes ALL rows of dependent; the SELECT inside the transaction shows an empty table; ROLLBACK cancels it and the rows come back.' AS note;
START TRANSACTION;
DELETE FROM dependent;
SELECT * FROM dependent;
ROLLBACK;
SELECT * FROM dependent;

SELECT 'Q1.4 WHERE, DISTINCT' AS question;
SELECT fname, lname, salary FROM employee
WHERE salary BETWEEN 3000 AND 6000 AND address LIKE '%Alexandria%'
ORDER BY salary DESC;
SELECT * FROM employee WHERE super_ssn IS NULL;
SELECT DISTINCT Dno FROM employee WHERE Dno IS NOT NULL;

SELECT 'Q1.5 Aggregation' AS question;
SELECT COUNT(*) AS employees, SUM(salary) AS total, AVG(salary) AS average,
       MIN(salary) AS smallest, MAX(salary) AS largest
FROM employee;

SELECT 'Q1.6 GROUP BY' AS question;
SELECT Dno, COUNT(*) AS employees, AVG(salary) AS average_salary
FROM employee GROUP BY Dno;

SELECT 'Q1.7 HAVING' AS question;
SELECT Dno, COUNT(*) AS employees FROM employee GROUP BY Dno HAVING COUNT(*) > 2;
SELECT Dno, COUNT(*) AS employees FROM employee WHERE salary > 3000 GROUP BY Dno HAVING COUNT(*) > 2;
SELECT 'WHERE filters single rows BEFORE grouping (no aggregates); HAVING filters whole groups AFTER grouping (can use COUNT, SUM, ...).' AS note;

SELECT 'Q1.8 JOIN' AS question;
SELECT CONCAT(e.fname,' ',e.lname) AS full_name, d.Dname
FROM employee e JOIN department d ON e.Dno = d.Dnumber;

SELECT 'Q1.9 JOIN of three tables' AS question;
SELECT e.lname, p.Pname, w.hours
FROM works_on w
JOIN employee e ON w.essn = e.ssn
JOIN project  p ON w.Pno  = p.Pnumber;

SELECT 'Q1.10 LEFT JOIN' AS question;
SELECT d.Dnumber, d.Dname, COUNT(e.ssn) AS employees
FROM department d LEFT JOIN employee e ON e.Dno = d.Dnumber
GROUP BY d.Dnumber, d.Dname;
SELECT p.Pnumber, p.Pname
FROM project p LEFT JOIN works_on w ON w.Pno = p.Pnumber
WHERE w.essn IS NULL;

SELECT 'Q1.11 Self join (LEFT JOIN keeps the employee with no supervisor)' AS question;
SELECT CONCAT(e.fname,' ',e.lname) AS employee,
       CONCAT(s.fname,' ',s.lname) AS supervisor
FROM employee e LEFT JOIN employee s ON e.super_ssn = s.ssn;

SELECT 'Q1.12 JOIN + GROUP BY + HAVING' AS question;
SELECT p.Pname, SUM(w.hours) AS total_hours
FROM project p JOIN works_on w ON w.Pno = p.Pnumber
GROUP BY p.Pnumber, p.Pname
HAVING SUM(w.hours) > 20
ORDER BY total_hours DESC;