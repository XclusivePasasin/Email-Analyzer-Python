-- Create the database
CREATE DATABASE Informations;

-- Select the database
USE Informations;

-- Create the table Invoices
CREATE TABLE Invoices (
    Generation_Code VARCHAR(50) PRIMARY KEY,
    Control_Number VARCHAR(50),
    Receiver_Name VARCHAR(100),
    Issuer_Name VARCHAR(100),
    Issuer_Nit VARCHAR(20),
    Issuer_Nrc VARCHAR(20),
    Date VARCHAR(100),
    File_Path_JSON VARCHAR(255),
    File_Path_PDF VARCHAR(255)
);
