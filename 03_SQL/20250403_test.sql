 CREATE DATABASE TEST_DB;
 
 CREATE DATABASE HR;
 
 SHOW DATABASES;
 
 -- GRANT ALL privileges ON TEST_DB.customer to growing@'%';
 
 -- DROP DATABASE HR;
 -- DROP DATABASE MY_DB;
 
 USE TEST_DB;
 
 
 ###########################
 ########테이블생성###########
 ###########################
 CREATE TABLE MEMBER(
	id VARCHAR(10) primary key -- 최대 10글자
    , password varchar(10) NOT NULL-- not null은 필수 입력check
    , name varchar(50) NOT NULL
    , age int check(age > 1) -- check는 조건을 넣을 수 있다.
    , email varchar(100) NOT NULL UNIQUE -- unique 중복값을 허용하지않음.
    , point int default 1000 -- 값을 넣지 않으면 기본 값을 1000으로 세팅
    , join_date timestamp not null default current_timestamp
    );
-- 테이블들 조회
SHOW TABLES;
-- 테이블의 컬럼정보 조회
DESC MEMBER;
-- 테이블 삭제
-- DROP TABLE MEMBER;
INSERT INTO MEMBER 
VALUES (
	'id_100'
    , '1111'
    , '죠죠'
    , 5000
    , 'jojo@a.com'
    , 30
    , '2023-12-10 11:32:33'
);

INSERT INTO MEMBER 
(
	id
    , password
    , name
    , age
    , email
)
VALUES (
	'id_101'
    , '1111'
    , '디아크'    
    , 31
    , 'dark@a.com'
);

INSERT INTO MEMBER 
(
	id
    , password
    , name
    , age
    , email
    , point
)
VALUES (
	'id_102'
    , '1111'
    , '렌'    
    , 33
    , 'ren@a.com'
    , null
);

INSERT INTO MEMBER 
(
	id
    , password
    , name
    , age
    , email
    , point
)
VALUES (
	'id_103'
    , '1111'
    , '세이지'    
    , 5
    , 'sage@a.com'
    , null
);





commit;
SELECT * 
  FROM MEMBER;
 