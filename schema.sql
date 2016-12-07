-- Copyright 2009 FriendFeed
--
-- Licensed under the Apache License, Version 2.0 (the "License"); you may
-- not use this file except in compliance with the License. You may obtain
-- a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
-- WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
-- License for the specific language governing permissions and limitations
-- under the License.

-- To create the database:
--   CREATE DATABASE dang DEFAULT CHARACTER SET utf8;
--   GRANT ALL PRIVILEGES ON dang.* TO 'dang'@'localhost' IDENTIFIED BY 'dang';
--
-- To reload the tables:
--   mysql --user=dang --password=dang --database=dang < schema.sql


-- SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+8:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS users;
CREATE TABLE users(
  id int, username CHAR(15) NOT NULL ,
  password CHAR(15) NOT NULL ,
  user VARCHAR(50) NOT NULL ,
  PRIMARY KEY (username)
  );

DROP TABLE IF EXISTS question;
create table question(
  qid CHAR(15),
  content VARCHAR(1000) NOT NULL ,
  answer CHAR(15) NOT NULL,
  PRIMARY KEY (qid)
  );

DROP TABLE IF EXISTS choice;
CREATE TABLE choice(
  content VARCHAR (1000) ,
  mask CHAR(15) ,
  ques_id CHAR(15) ,
  FOREIGN KEY (ques_id) REFERENCES question(qid) ON DELETE CASCADE
  );

DROP TABLE IF EXISTS rec;
CREATE TABLE rec(
  uid CHAR(15),
  qid CHAR(15),
  rec CHAR(15),
  ans CHAR(15),
  FOREIGN KEY (uid) REFERENCES users(username) ON DELETE CASCADE
  );

DROP TABLE IF EXISTS score;
CREATE TABLE score(
  username CHAR(15),
  user VARCHAR(50),
  single CHAR(15),
  multi CHAR(15),
  judge CHAR (15),
  total CHAR(15)
  );

DROP TABLE IF EXISTS survey;
CREATE TABLE survey(
  qid CHAR(15),
  content VARCHAR(100) NOT NULL ,
  A CHAR (15) DEFAULT 0,
  B CHAR (15) DEFAULT 0,
  C CHAR (15) DEFAULT 0,
  D CHAR (15) DEFAULT 0,
  E CHAR (15) DEFAULT 0,
  PRIMARY KEY (qid)
  );

