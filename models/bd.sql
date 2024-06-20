-- Create the database
CREATE DATABASE Information;

-- Select the database
USE Information;

-- Create the table Invoices
CREATE TABLE Invoices (
    GenerationCode INT PRIMARY KEY,
    ControlNumber VARCHAR(50),
    ReceiverName VARCHAR(100),
    IssuerName VARCHAR(100),
    IssuerNit VARCHAR(20),
    IssuerNrc VARCHAR(20),
    Date DATE
);
