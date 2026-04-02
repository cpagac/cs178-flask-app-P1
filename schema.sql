-- NOTE THIS CODE WAS GENERATED THROUGH AI ASSIATNCENTCE
-- schema.sql
-- Turing Test Game — database schema and seed data
-- Run with: mysql -h YOUR-RDS-ENDPOINT -u admin -p < schema.sql

CREATE DATABASE IF NOT EXISTS turing_test;
USE turing_test;

CREATE TABLE IF NOT EXISTS Categories (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS Authors (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    is_ai BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS Snippets (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    text        TEXT NOT NULL,
    category_id INT NOT NULL,
    author_id   INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Categories(id),
    FOREIGN KEY (author_id)   REFERENCES Authors(id)
);

INSERT INTO Categories (name) VALUES ('Python Code'), ('Poetry'), ('News Article');

INSERT INTO Authors (name, is_ai) VALUES ('GPT-4', TRUE), ('Claude', TRUE), ('Anonymous Human', FALSE);

INSERT INTO Snippets (text, category_id, author_id) VALUES
    ('def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)', 1, 1),
    ('def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a+b\n    return a', 1, 3),
    ('The stars align in perfect rows,\nAs data streams through silicon flows,\nA mind of math, yet cold and bright,\nCrafts verse by rules of day and night.', 2, 2),
    ('i left the kettle on again\nand watched the window fog\nwith something like forgetting\nsomething like a name', 2, 3),
    ('Researchers at a leading university announced Tuesday the development of a novel machine learning framework capable of processing natural language queries with unprecedented accuracy, according to a paper published in the journal Nature.', 3, 1);
