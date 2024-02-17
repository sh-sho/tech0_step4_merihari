from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.database.database import get_db
from app.database.database import Product_Master, Transaction, TransactionDetail, Tax_Master

import decimal
from sqlalchemy import CHAR, VARCHAR, TIMESTAMP, Column, Transaction, create_engine

router = APIRouter()


# 機能名：商品マスタ検索
@router.get("/PRD_master/{code}", response_model=Product_Master)  # 商品コード(code)を引数として商品マスタ(PRD_master)テーブルへGETアクセス
def read_PRD_by_code(code: CHAR, db: Session = Depends(get_db)):  # read_PRD_by_CODE関数
    db_PRD = db.query(Product_Master).filter(Product_Master.code == code).first()
    if db_PRD is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return db_PRD


# 機能名：購入
# 1−1 取引テーブルへ登録する。
@router.post("/Transaction/", response_model=Transaction)
def create_new_transaction(
    TRD_id: int,
    employee_code: CHAR,
    store_code: CHAR,
    pos_no: CHAR,
    total_amount: int,
    total_amount_ex_tax: int,
    db: Session = Depends(get_db),
)-> Transaction:
    if employee_code is None:
        employee_code = 9999999999
    transaction = Transaction(
            TRD_id = Transaction.TRD_id.items()+1,
            employee_code = db.query(Transaction).filter(Transaction.employee_code == employee_code).first(),
            store_code = 30,
            pos_no = 90,
            total_amount = 0,
            total_amount_ex_tax = 0,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return TRD_id


# 1−2 取引明細へ登録する。
@router.post("/TransactionDetail/", response_model=TransactionDetail)
def create_transaction_detail(
    TRD_id: int,
    DTL_id: int,
    PRD_id: int,
    PRD_code: CHAR,
    PRD_name: VARCHAR,
    PRD_price: int,
    TAX_category: CHAR,
    db: Session = Depends(get_db),
)-> TransactionDetail:
    transaction_detail = TransactionDetail(
        TRD_id = TRD_id,  # フロントからどうやって受け取るんだ？
        DTL_id = TransactionDetail.DTL_id.items()+1,
        PRD_id = PRD_id,  # フロントからどうやって受け取るんだ？
        PRD_code = PRD_code,  # フロントからどうやって受け取るんだ？
        PRD_name = PRD_name,  # フロントからどうやって受け取るんだ？
        PRD_price = PRD_price,  # フロントからどうやって受け取るんだ？
        TAX_category = 10,  # フロントからどうやって受け取るんだ？
    )
    db.add(transaction_detail)
    db.commit()
    db.refresh(transaction_detail)
    return transaction_detail


# 1−3 合計や税金額を計算する。


# 1−4 取引テーブルを更新する。


# 1−5 合計金額、合計金額（税抜）をフロントへ返す。

