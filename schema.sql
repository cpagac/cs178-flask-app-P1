-- NOTE THIS CODE WAS GENERATED THROUGH AI ASSIATNCENTCE
-- schema.sql
-- Updated with Global Metrics for the Uncanny Valley index
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
    id               INT AUTO_INCREMENT PRIMARY KEY,
    text             TEXT NOT NULL,
    category_id      INT NOT NULL,
    author_id        INT NOT NULL,
    correct_guesses  INT DEFAULT 0,
    incorrect_guesses INT DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES Categories(id),
    FOREIGN KEY (author_id)   REFERENCES Authors(id)
);
