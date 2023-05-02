CREATE TABLE STOCK_DATA(
    DATE_PREDICTED DATE,
    STOCK_SYMBOL VARCHAR(100),
    PRICE FLOAT,
	PRIMARY KEY(DATE_PREDICTED, STOCK_SYMBOL)
);


CREATE TABLE USERS(
    USERNAME_ VARCHAR(100) PRIMARY KEY UNIQUE NOT NULL,
    PASSWORD_ VARCHAR(300) NOT NULL,
    EMAIL_ VARCHAR(300) NOT NULL
);