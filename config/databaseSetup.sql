DROP DATABASE IF EXISTS inv_backup;
CREATE DATABASE inv_backup;
USE inv_backup;


CREATE TABLE allowedusers
(
    userSeq        INT auto_increment PRIMARY KEY,
    userID         VARCHAR(255) NULL unique,
    user_full_name VARCHAR(255) NULL,
    emailAddr      VARCHAR(50)  NOT NULL unique,
    theme          INT        default 1         NOT NULL,
    isSystemUser   tinyINT(1) default 0         NULL,
    addedBy       INT                         NULL,
    addedDate     datetime default CURRENT_TIMESTAMP NULL,
    updatedBy     INT                         NULL,
    updatedDate   datetime default CURRENT_TIMESTAMP NULL on update CURRENT_TIMESTAMP,
    CONSTRAINT foreign key (addedBy) references allowedusers (userSeq),
    CONSTRAINT foreign key (updatedBy) references allowedusers (userSeq)

);


CREATE TABLE recordtype
(
    typeSeq    INT auto_increment PRIMARY KEY,
    recordName VARCHAR(20) NULL,
    addedBy       INT                         NULL,
    addedDate     datetime default CURRENT_TIMESTAMP NULL,
    updatedBy     INT                         NULL,
    updatedDate   datetime default CURRENT_TIMESTAMP NULL on update CURRENT_TIMESTAMP,
    CONSTRAINT foreign key (addedBy) references allowedusers (userSeq),
    CONSTRAINT foreign key (updatedBy) references allowedusers (userSeq)
);

CREATE TABLE statuses
(
    statusID   INT auto_increment PRIMARY KEY,
    statusDesc VARCHAR(20) NULL,
    addedBy       INT                         NULL,
    addedDate     datetime default CURRENT_TIMESTAMP NULL,
    updatedBy     INT                         NULL,
    updatedDate   datetime default CURRENT_TIMESTAMP NULL on update CURRENT_TIMESTAMP,
    CONSTRAINT foreign key (addedBy) references allowedusers (userSeq),
    CONSTRAINT foreign key (updatedBy) references allowedusers (userSeq)
);

CREATE TABLE addresses
(
    addrSeq  INT AUTO_INCREMENT PRIMARY KEY,
    line1    VARCHAR(30) NULL,
    line2    VARCHAR(30) NULL,
    line3    VARCHAR(30) NULL,
    line4    VARCHAR(30) NULL,
    addrName VARCHAR(30) NULL,
    addedBy       INT                         NULL,
    addedDate     datetime default CURRENT_TIMESTAMP NULL,
    updatedBy     INT                         NULL,
    updatedDate   datetime default CURRENT_TIMESTAMP NULL on update CURRENT_TIMESTAMP,
    CONSTRAINT foreign key (addedBy) references allowedusers (userSeq),
    CONSTRAINT foreign key (updatedBy) references allowedusers (userSeq)
);

CREATE TABLE invoice
(
    invoiceID   INT auto_increment PRIMARY KEY,
    createdDate datetime default CURRENT_TIMESTAMP NULL,
    updateDate  datetime default CURRENT_TIMESTAMP NULL on update CURRENT_TIMESTAMP,
    creator     INT                                NULL,
    approved_by INT                                NULL,
    recordType  INT                                NULL,
    return_addr INT                                NULL,
    tax         decimal(8, 2)                      NULL,
    fees        decimal(8, 2)                      NULL,
    total       decimal(8, 2)                      NULL,
    statusID    INT                                NULL,
    addedBy       INT                         NULL,
    addedDate     datetime default CURRENT_TIMESTAMP NULL,
    updatedBy     INT                         NULL,
    updatedDate   datetime default CURRENT_TIMESTAMP NULL on update CURRENT_TIMESTAMP,
    CONSTRAINT foreign key (addedBy) references allowedusers (userSeq),
    CONSTRAINT foreign key (updatedBy) references allowedusers (userSeq),

    CONSTRAINT invoice_creator_fk
        foreign key (creator) references allowedusers (userSeq),
    CONSTRAINT invoice_recordType_fk
        foreign key (recordType) references recordtype (typeSeq),
    CONSTRAINT invoice_return_addr_fk
        foreign key (return_addr) references addresses (addrSeq),
    CONSTRAINT invoice_statusID_fk
        foreign key (statusID) references statuses (statusID),
    CONSTRAINT invoice_approved_by_fk
        foreign key (approved_by) references allowedusers (userSeq)
);


CREATE TABLE line
(
    lineSeq    INT auto_increment PRIMARY KEY,
    invoiceID  INT                         NOT NULL,
    lineID     INT                         NOT NULL,
    `desc`     VARCHAR(50) NULL,
    unit_price decimal(8, 2)               NULL,
    qty        INT                         NULL,
    total      decimal(8, 2)               NULL,
    addedBy       INT                         NULL,
    addedDate     datetime default CURRENT_TIMESTAMP NULL,
    updatedBy     INT                         NULL,
    updatedDate   datetime default CURRENT_TIMESTAMP NULL on update CURRENT_TIMESTAMP,
    CONSTRAINT foreign key (addedBy) references allowedusers (userSeq),
    CONSTRAINT foreign key (updatedBy) references allowedusers (userSeq),
    CONSTRAINT line_invoiceID_fk
        foreign key (invoiceID) references invoice (invoiceID)
);


CREATE TABLE permissions
(
    permSeq            INT auto_increment PRIMARY KEY,
    userSeq            INT                  NOT NULL,
    invEdit            tinyINT(1) default 0 NULL,
    invView            tinyINT(1) default 0 NULL,
    docEdit            tinyINT(1) default 0 NULL,
    docView            tinyINT(1) default 0 NULL,
    invAdmin           tinyINT(1) default 0 NULL,
    docAdmin           tinyINT(1) default 0 NULL,
    canApproveInvoices tinyINT(1) default 0 NOT NULL,
    canReceiveEmails   tinyINT(1) default 0 NULL,
    userAdmin          tinyINT(1) default 0 NULL,
    addedBy       INT                         NULL,
    addedDate     datetime default CURRENT_TIMESTAMP NULL,
    updatedBy     INT                         NULL,
    updatedDate   datetime default CURRENT_TIMESTAMP NULL on update CURRENT_TIMESTAMP,
    CONSTRAINT foreign key (addedBy) references allowedusers (userSeq),
    CONSTRAINT foreign key (updatedBy) references allowedusers (userSeq),
    CONSTRAINT permissions_allowedusers_userSeq_fk
        foreign key (userSeq) references allowedusers (userSeq)
);

# --- Lyra's Password scratch work --- 

alter table allowedUsers add column password varchar(255) not null;

CREATE TABLE passwordReset
(
    prSeq int auto_increment primary key,
    userSeq int not null unique,
    token varchar(40) not null unique,
    created_at datetime default CURRENT_TIMESTAMP,

    constraint foreign key (userSeq) references allowedUsers (userSeq)
);