from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error

app = FastAPI()

# データベース接続情報
DATABASE_URL = "tech0-db-step4-studentrdb-7.mysql.database.azure.com"
DATABASE_USERNAME = "tech0gen5student"
DATABASE_PASSWORD = "vY7JZNfU7"
DATABASE_NAME = "flexibleserverdb"

# データベースに接続する関数
def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DATABASE_URL,
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME
        )
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

# ProductテーブルからCODEに基づいてNAMEとPRICEを取得するエンドポイント
@app.get("/products/{product_code}")
async def read_product(product_code: str):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = connection.cursor()
    cursor.execute(f"SELECT NAME, PRICE FROM Product WHERE CODE = '{product_code}'")
    product = cursor.fetchone()
    cursor.close()
    connection.close()
    if product:
        return {"name": product[0], "price": product[1]}
    else:
        raise HTTPException(status_code=404, detail="Product not found")
