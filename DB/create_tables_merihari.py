import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

load_dotenv()
# set env
# MYSQL_HOST = os.getenv('MYSQL_HOST')
# MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
# MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
# DATABASE_NAME = os.getenv('DATABASE_NAME')
# SSL_CA = os.getenv('SSL_CA')
# Obtain connection string information from the portal

MYSQL_HOST = 'tech0-db-step4-studentrdb-7.mysql.database.azure.com'
MYSQL_USERNAME = 'tech0gen5student'
MYSQL_PASSWORD = 'vY7JZNfU7'
DATABASE_NAME = 'flexibleserverdb'


config = {
    'host':MYSQL_HOST,
    'user':MYSQL_USERNAME,
    'password':MYSQL_PASSWORD,
    'database':DATABASE_NAME
    # 'ssl_ca':SSL_CA
}
# Construct connection string

try:
    conn = mysql.connector.connect(**config)
    print("Connection established")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor = conn.cursor()

# Drop previous table of same name if one exists
cursor.execute("""DROP TABLE IF EXISTS Transaction_details;""")
cursor.execute("""DROP TABLE IF EXISTS Product;""")
cursor.execute("""DROP TABLE IF EXISTS Transaction;""")
cursor.execute("""DROP TABLE IF EXISTS Tax;""")
print("Finished dropping table (if existed).")

# Create table
#CODEカラムが2文字のアルファベットと11文字の数字で構成されるパターンでユニークになるよう制御
cursor.execute("""
CREATE TABLE Product (
    PRD_ID INT AUTO_INCREMENT PRIMARY KEY, 
    CODE CHAR(13) UNIQUE, 
    NAME VARCHAR(50), 
    PRICE INT,
    CHECK (CODE REGEXP '^[0-9]{13}$')
);
""")
print("Finished creating Product table.")

cursor.execute("""
CREATE TABLE Transaction (
    TRD_ID INT AUTO_INCREMENT PRIMARY KEY, 
    DATETIME DATETIME, 
    EMP_CD CHAR(10), 
    STORE_CD CHAR(5), 
    POS_NO CHAR(3), 
    TOTAL_AMT INT, 
    TTL_AMT_EX_TAX INT);
""")
print("Finished creating Transaction table.")

#CODEカラムが2文字のアルファベットで構成されるパターンでユニークになるよう制御
cursor.execute("""
CREATE TABLE Tax (
    ID INT AUTO_INCREMENT PRIMARY KEY, 
    CODE CHAR(2) UNIQUE, 
    NAME VARCHAR(20), 
    PERCENT DECIMAL(5,2),
    CHECK (CODE REGEXP '^[A-Z]{2}$')
);
""")
print("Finished creating Tax table.")

cursor.execute("""
CREATE TABLE Transaction_details (
    TRD_ID INT, 
    DTL_ID INT AUTO_INCREMENT, 
    PRD_ID INT, 
    PRD_CODE CHAR(13),
    PRD_NAME VARCHAR(50),
    PRD_PRICE INT,
    TAX_CD CHAR(2),
    PRIMARY KEY (DTL_ID, TRD_ID),
    FOREIGN KEY (TRD_ID) REFERENCES Transaction(TRD_ID), 
    FOREIGN KEY (PRD_ID) REFERENCES Product(PRD_ID),
    FOREIGN KEY (PRD_CODE) REFERENCES Product(CODE), 
    FOREIGN KEY (TAX_CD) REFERENCES Tax(CODE) 
);
""")
print("Finished creating Transaction_details table.")



# Insert some data into User table
cursor.execute("""
INSERT INTO Product (CODE, NAME, PRICE) VALUES
    ('4901480372600', '手帳', 100),
    ('4901306075517', '野菜生活', 200);
""")
print("Inserted", cursor.rowcount, "row(s) of data to Product table.")

cursor.execute("""
INSERT INTO Transaction (DATETIME, EMP_CD, STORE_CD, POS_NO, TOTAL_AMT, TTL_AMT_EX_TAX) VALUES
    ('2024-02-01 12:00:00', '1111111111', '11111', '111', 110, 100),
    ('2023-02-02 15:00:00', '2222222222', '22222', '222', 220, 200);
""")
print("Inserted", cursor.rowcount, "row(s) of data to Transaction table.")

cursor.execute("""
INSERT INTO Tax (CODE, NAME, PERCENT) VALUES
    ('IN', '店内消費', 10),
    ('OT', '店外消費', 8);
""")
print("Inserted", cursor.rowcount, "row(s) of data to Tax table.")

# Commit
conn.commit()

# Cleanup
cursor.close()
conn.close()
print("Done.")
