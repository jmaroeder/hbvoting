DROP TABLE IF EXISTS person;
CREATE TABLE person (
  personid INTEGER, PRIMARY KEY autoincrement,
  assigned_id INTEGER,
  ethnicity VARCHAR NOT NULL,
  email VARCHAR NOT NULL,
  mentor VARCHAR NOT NULL,
  gender VARCHAR NOT NULL,
  city VARCHAR NOT NULL,
  party VARCHAR NOT NULL
);

DROP TABLE IF EXISTS vote;
CREATE TABLE vote (
  voteid INTEGER PRIMARY KEY,
  choice VARCHAR NOT NULL,
  personid INTEGER NOT NULL,
  FOREIGN KEY(personid) REFERENCES person(personid)
);
