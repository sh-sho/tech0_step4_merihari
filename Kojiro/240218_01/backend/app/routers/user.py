from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from requests import request
from sqlalchemy.orm import Session, joinedload

from app.database.database import get_db
from app.database.database import Product_Master, Transaction, TransactionDetail, Tax_Master,TransactionUpdate

import decimal
from sqlalchemy import CHAR, VARCHAR, TIMESTAMP, Column, Transaction, create_engine

router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

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
            #TRD_id = Transaction.TRD_id.items()+1, #ここは自動でインクリメントされるようなのでコメントアウト
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
@router.post("フロントエンドから指定されたURL")
def get_data(Purchase_lists: List[Purchase_list]):
    new_Purchase_list = []
    for Purchase_list in Purchase_lists:
        new_Purchase_list.append({
            "TRD_id": Purchase_list.TRD_id,
            "PRD_id": Purchase_list.PRD_id,
            "PRD_code": Purchase_list.PRD_code,
            "PRD_name": Purchase_list.PRD_name,
            "PRD_price": Purchase_list.PRD_price,})
    # 整形したデータをレスポンスbodyを送信
    return new_Purchase_list

# @app.post("/users/")
# 上で定義したUserモデルのリクエストbodyをリストに入れた形で受け取る
# users = [{"user_id": 1, "name": "太郎"},{"user_id": 2, "name": "次郎"}]
# def create_users(users: List[User]):
    new_users = []
    for user in users:
        new_users.append({"res": "ok", "ID": user.user_id, "名前": user.name})
    # 整形したデータをレスポンスbodyを送信
    return new_users

@router.post("/TransactionDetail/", response_model=TransactionDetail)
def create_transaction_detail(
    TRD_id: int,
    #DTL_id: int, #ここは自動的にインクリメントされるのでコメントアウト
    PRD_id: int,
    PRD_code: CHAR,
    PRD_name: VARCHAR,
    PRD_price: int,
    TAX_category: CHAR,
    db: Session = Depends(get_db),
)-> TransactionDetail:
    
    transaction_detail = TransactionDetail(
        TRD_id = TRD_id,  # フロントからどうやって受け取るんだ？
        #DTL_id = TransactionDetail.DTL_id.items()+1, #ここは自動的にインクリメントされるのでコメントアウト
        PRD_id = PRD_id,  # フロントからどうやって受け取るんだ？
        PRD_code = PRD_code,  # フロントからどうやって受け取るんだ？
        PRD_name = PRD_name,  # フロントからどうやって受け取るんだ？
        PRD_price = PRD_price,  # フロントからどうやって受け取るんだ？
        TAX_category = "10",  # フロントからどうやって受け取るんだ？
    )
    db.add(transaction_detail)
    
    db.commit()
    db.refresh(transaction_detail)
    return transaction_detail


# 1−3 合計や税金額を計算する。
# 1−4 取引テーブルを更新する。
# 1−5 合計金額、合計金額（税抜）をフロントへ返す。
@router.put("/update_transaction/{TRD_id}", response_model=TransactionUpdate)
def update_transaction_amounts(
    TRD_id: int,
    db: Session = Depends(get_db)
) -> TransactionUpdate:
    # 取引明細から情報を取得
    transaction_details = db.query(TransactionDetail).filter(TransactionDetail.TRD_id == TRD_id).all()
    if not transaction_details:
        raise HTTPException(status_code=404, detail="Transaction details not found")

    # 合計金額と税金の計算
    total_amount = decimal(0) #decimal型：floatよりも誤差が少なく、お金の計算はこの型が一般的らしい
    total_tax = decimal(0)
    for detail in transaction_details:
        product_price =decimal(detail.PRD_price)
        tax_rate = db.query(Tax_Master).filter(Tax_Master.TAX_category == detail.TAX_category).first().rate
        tax_amount = product_price * decimal(tax_rate)
        total_amount += product_price + tax_amount
        total_tax += tax_amount

    # 税抜き合計金額の計算
    total_amount_ex_tax = sum(decimal(detail.PRD_price) for detail in transaction_details)

    # 取引テーブルの更新
    transaction = db.query(Transaction).filter(Transaction.TRD_id == TRD_id).first()
    if transaction:
        transaction.total_amount = total_amount
        transaction.total_amount_ex_tax = total_amount_ex_tax
        db.commit()
        return TransactionUpdate(total_amount=total_amount, total_amount_ex_tax=total_amount_ex_tax)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")





