create database Invoices;
create database InvoiceTest;

create table addresses (
    addrSeq int not null primary key auto_increment,
    Line1 varchar(40),
    Line2 varchar(40),
    Line3 varchar(40),
    Line4 varchar(40),
);

create table statuses (
    statusID int not null primary key auto_increment,
    status varchar(40)
);

create table allowedusers (
    userID int not null primary key auto_increment,
);

create table record (
    id int not null primary key auto_increment,
    createdDate datetime default current_timestamp,
    creator varchar(40),
    approver varchar(40),
    recordType enum('invoice', 'sga_budget', 'c_invoice'),
    return_addr int,
    tax decimal(10,2),
    fees decimal(10,2),
    total decimal(10,2),
    statusID int,
    foreign key (statusID) references statuses(statusID),
    foreign key (return_addr) references addresses(addrSeq)
);

create table inv_line (
    lineSeq int not null primary key auto_increment,
    recordID int,
    `line` int,
    `desc` varchar(40),
    ammt decimal(10,2),
    qty int,
    total decimal(10,2),
    foreign key (recordID) references record(id) 
);

use InvoiceTest;

DELIMITER //

CREATE PROCEDURE importBackup() 
BEGIN
-- Drop our old tables, if they exist
   DROP TABLE IF EXISTS InvoiceTest.inv_line;
   DROP TABLE IF EXISTS InvoiceTest.Record;
   DROP TABLE IF EXISTS InvoiceTest.Addresses;
   DROP TABLE IF EXISTS InvoiceTest.Statuses;
   DROP TABLE IF EXISTS InvoiceTest.allowedusers;
   
-- Create our new tables, with the same structure as the main tables
	CREATE TABLE InvoiceTest.allowedusers like invoices.allowedusers;
	CREATE TABLE InvoiceTest.Statuses like Invoices.Statuses;
    CREATE TABLE InvoiceTest.Addresses like Invoices.addresses;
    CREATE TABLE InvoiceTest.record like Invoices.record;
	CREATE TABLE InvoiceTest.inv_line like Invoices.inv_line;
-- For some reason, some FKs dont carry over... Let's make them!

	alter table record add foreign key (statusID) references statuses(statusID);
	alter table record add foreign key (return_addr) references addresses(addrSeq);
	alter table inv_line add foreign key (recordID) references record(id);
    
    INSERT INTO InvoiceTest.Statuses SELECT * FROM Invoices.Statuses;
    INSERT INTO InvoiceTest.Addresses SELECT * FROM Invoices.Addresses;
    INSERT INTO InvoiceTest.allowedusers SELECT * FROM Invoices.allowedusers;
    INSERT INTO InvoiceTest.record SELECT * FROM Invoices.record;
    INSERT INTO InvoiceTest.inv_line SELECT * FROM Invoices.inv_line;
    
END//

DELIMITER ;

call importBackup();