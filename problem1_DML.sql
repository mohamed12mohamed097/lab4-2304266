USE company;

-- departments (manager is filled in after the employees exist)
INSERT INTO department (Dnumber, Dname) VALUES
 (1, 'Research'), (2, 'Administration'), (3, 'Headquarters'),
 (4, 'Marketing');                       -- no employees on purpose

-- 111111111 has no supervisor; Research (1) has more than 2 employees
INSERT INTO employee VALUES
 ('111111111','Ahmed','Hassan', '1975-03-10','Alexandria','M',8000,NULL,       3),
 ('222222222','Sara', 'Ali',    '1985-07-21','Cairo',     'F',5500,'111111111',1),
 ('333333333','Omar', 'Khaled', '1990-01-15','Alexandria','M',4200,'222222222',1),
 ('444444444','Mona', 'Samir',  '1992-11-02','Giza',      'F',3500,'222222222',1),
 ('555555555','Youssef','Nabil','1988-05-30','Alexandria','M',2800,'111111111',2),
 ('666666666','Laila','Fathy',  '1995-09-09','Cairo',     'F',3000,'555555555',2);

UPDATE department SET mgr_ssn='222222222', mgr_start_date='2020-01-01' WHERE Dnumber=1;
UPDATE department SET mgr_ssn='555555555', mgr_start_date='2021-06-01' WHERE Dnumber=2;
UPDATE department SET mgr_ssn='111111111', mgr_start_date='2018-03-15' WHERE Dnumber=3;

-- project 4 has nobody working on it
INSERT INTO project VALUES
 (1,'ProductX',       'Alexandria',1),
 (2,'ProductY',       'Cairo',     1),
 (3,'Computerization','Cairo',     2),
 (4,'Reorganization', 'Alexandria',3);

-- Sara (222222222) and Omar (333333333) work on two projects
INSERT INTO works_on VALUES
 ('222222222',1,15),('222222222',2,10),
 ('333333333',1,20),('333333333',2, 8),
 ('444444444',2,12),('555555555',3,25),
 ('666666666',3,10),('111111111',1, 5);

INSERT INTO dependent VALUES
 ('222222222','Alice','F','2010-04-01','Daughter'),
 ('222222222','Adam', 'M','2012-06-15','Son'),
 ('555555555','Nour', 'F','1990-02-02','Spouse');