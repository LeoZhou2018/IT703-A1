DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS contact;
DROP TABLE IF EXISTS title;

CREATE TABLE user (
  User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
  User_Name TEXT UNIQUE NOT NULL,
  Password TEXT NOT NULL
);

CREATE TABLE customer (
  Company_ID INTEGER PRIMARY KEY AUTOINCREMENT,
  Company_Name TEXT UNIQUE NOT NULL,
  Location_Country TEXT,
  Location_City TEXT,
  Location_Street TEXT,
  Location_Post_Code INTEGER,
  Postal_Country TEXT,
  Postal_City TEXT,
  Postal_Street TEXT,
  Postal_Post_Code INTEGER,
  State INTEGER DEFAULT 1
);

CREATE TABLE title (
  Title_ID INTEGER PRIMARY KEY AUTOINCREMENT,
  Title_Name TEXT UNIQUE NOT NULL
);

CREATE TABLE contact (
  Contact_ID INTEGER PRIMARY KEY AUTOINCREMENT,
  Title_ID INTEGER,
  Contact_Name TEXT NOT NULL,
  Company_ID INTEGER,
  Role TEXT,
  Location_Country TEXT,
  Location_City TEXT,
  Location_Street TEXT,
  Location_Post_Code INTEGER,
  Email TEXT,
  Phone_Work TEXT,
  Phone_Cell TEXT,
  Phone_Home TEXT,
  Notes TEXT,
  State INTEGER DEFAULT 1,
  FOREIGN KEY (Title_ID) REFERENCES title (Title_ID),
  FOREIGN KEY (Company_ID) REFERENCES customer (Company_ID)
);
