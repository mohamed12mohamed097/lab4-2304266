DROP DATABASE IF EXISTS library;
CREATE DATABASE library;
USE library;

CREATE TABLE author (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(80) NOT NULL,
    country   VARCHAR(50),
    image     VARCHAR(255) NULL
);

CREATE TABLE publisher (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(80) NOT NULL,
    country      VARCHAR(50)
);

CREATE TABLE category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50) NOT NULL
);

CREATE TABLE book (
    book_id      INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(120) NOT NULL,
    price        DECIMAL(8,2) NOT NULL,
    publish_year INT,
    author_id    INT NOT NULL,
    publisher_id INT NOT NULL,
    category_id  INT NOT NULL,
    image        VARCHAR(255) NULL,
    FOREIGN KEY (author_id)    REFERENCES author(author_id)       ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES publisher(publisher_id),
    FOREIGN KEY (category_id)  REFERENCES category(category_id)
);

CREATE TABLE member (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(80) NOT NULL,
    email     VARCHAR(100),
    join_date DATE
);

CREATE TABLE loan (
    loan_id     INT AUTO_INCREMENT PRIMARY KEY,
    book_id     INT NOT NULL,
    member_id   INT NOT NULL,
    loan_date   DATE NOT NULL,
    return_date DATE NULL,                 -- NULL = still borrowed
    FOREIGN KEY (book_id)   REFERENCES book(book_id)     ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES member(member_id)
);