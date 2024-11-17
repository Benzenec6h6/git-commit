CREATE DATABASE pass_manage;
use flaskapp;

CREATE TABLE pass_manage.user (
    company VARCHAR(30),
    ID VARCHAR(30),
    password VARCHAR(30),
    savename VARCHAR(30)
);

INSERT INTO user
    (証券会社, ID, password, 保存名)
VALUES
    ('会社名', '任意のID', '任意のパスワード', '任意の保存名');