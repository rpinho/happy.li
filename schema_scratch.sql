CREATE DATABASE visas;
USE visas;

CREATE TABLE cities (
        id INT NOT NULL AUTO_INCREMENT,
        Name CHAR(100),
        Number_of_Application INT,
        Year YEAR(4),
        primary key (id));

CREATE TABLE jobs (
        id INT NOT NULL AUTO_INCREMENT,
        Name CHAR(100),
        Number_of_Application INT,
        Year YEAR(4),
        primary key (id));

CREATE DATABASE demo;
USE demo;

CREATE TABLE jobs_cities (
        id INT NOT NULL AUTO_INCREMENT,
        job CHAR(100),
        city CHAR(100),
        n_postings INT,
        salary INT,
        relative_salary FLOAT,
        salaries_max INT,
        salaries_median INT,
        trend_last2first FLOAT,
        trend_median FLOAT,
        trend_max INT,
        primary key (id));

CREATE TABLE household_income (
        id INT NOT NULL AUTO_INCREMENT,
        state CHAR(2),
        zipcode INT,
        census_tract_id INT,
        mean_household_income INT,
        primary key (id));

CREATE TABLE payscale (
        id INT NOT NULL AUTO_INCREMENT,
        url TEXT,
        text LONGTEXT character set utf8,
        date DATETIME,
        primary key (id));

CREATE TABLE city_urls (
        id INT NOT NULL AUTO_INCREMENT,
        city varchar(63),
        state CHAR(2),
        url TEXT character set utf8,
        primary key (id));

CREATE TABLE city_description (
        id INT NOT NULL AUTO_INCREMENT,
        city varchar(63),
        state CHAR(2),
        state_name varchar(63),
        description LONGTEXT character set utf8,
        primary key (id)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
