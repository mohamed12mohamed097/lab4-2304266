USE library;

-- two Egyptian authors; author 4 has no books; author 1 has 4 books
INSERT INTO author (author_id, name, country) VALUES
 (1,'Naguib Mahfouz','Egypt'), (2,'Taha Hussein','Egypt'),
 (3,'Jane Austen','UK'),       (4,'Haruki Murakami','Japan');

-- publisher 1 and author 1 are both from Egypt
INSERT INTO publisher (publisher_id, name, country) VALUES
 (1,'Dar El Shorouk','Egypt'), (2,'Penguin','UK'), (3,'Kodansha','Japan');

INSERT INTO category (category_id, name) VALUES
 (1,'Novel'), (2,'History'), (3,'Science');

-- books 1, 5, 6 cost between 15 and 20; book 9 is never borrowed
INSERT INTO book (book_id, title, price, publish_year, author_id, publisher_id, category_id) VALUES
 (1,'Cairo Trilogy',       18.50,1956,1,1,1),
 (2,'Children of the Alley',14.00,1959,1,1,1),
 (3,'The Days',            22.00,1929,2,1,2),
 (4,'Pride and Prejudice', 12.00,1813,3,2,1),
 (5,'Emma',                16.00,1815,3,2,1),
 (6,'Persuasion',          19.99,1817,3,2,1),
 (7,'Egypt Through History',30.00,1950,2,2,2),
 (8,'Mirror of Egypt',     25.00,1947,1,1,2),
 (9,'Cosmos Basics',       40.00,2010,2,3,3),
 (10,'Quantum Notes',      35.00,2015,1,3,3);

-- member 5 has no loans
INSERT INTO member (member_id, name, email, join_date) VALUES
 (1,'Ali Mostafa','ali@mail.com','2026-01-10'),
 (2,'Mona Adel','mona@mail.com','2026-02-05'),
 (3,'Karim Nabil','karim@mail.com','2026-03-12'),
 (4,'Salma Hany','salma@mail.com','2026-04-20'),
 (5,'Hany Fouad','hany@mail.com','2026-05-01');

-- loans 7, 9 and 11 are not returned yet
INSERT INTO loan (loan_id, book_id, member_id, loan_date, return_date) VALUES
 (1,1,1,'2026-09-01','2026-09-10'),
 (2,1,2,'2026-09-12','2026-09-20'),
 (3,1,3,'2026-10-01','2026-10-08'),
 (4,2,1,'2026-09-05','2026-09-15'),
 (5,3,2,'2026-09-20','2026-09-30'),
 (6,4,1,'2026-10-02','2026-10-12'),
 (7,5,3,'2026-10-05',NULL),
 (8,6,4,'2026-10-10','2026-10-18'),
 (9,7,1,'2026-10-15',NULL),
 (10,8,2,'2026-10-20','2026-10-27'),
 (11,2,4,'2026-11-01',NULL),
 (12,10,1,'2026-11-03','2026-11-09');