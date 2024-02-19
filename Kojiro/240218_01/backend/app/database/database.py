import decimal
from sqlalchemy import CHAR, VARCHAR, TIMESTAMP, Column, create_engine,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://[ユーザー]:[パスワード]@[ホスト名]/[データベース名]"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Product_Master(Base):
    __tablename__ = "PRD_master"
    PRD_id = Column(int, primary_key=True, index=True)
    code = Column(CHAR(13))
    name = Column(VARCHAR(50))
    price = Column(int)

class Transaction(Base):
    __tablename__ = "transactions"
    TRD_id = Column(int, primary_key=True, index=True)
    datetime = Column(TIMESTAMP)
    employee_code = Column(CHAR(10))
    store_code = Column(CHAR(5))
    pos_no = Column(CHAR(3))
    total_amount = Column(int)
    total_amount_excl_tax = Column(int)

class TransactionDetail(Base):
    __tablename__ = "transaction_details"
    #TRD_id = Column(int, primary_key=True, index=True)
    #DTL_id = Column(int, primary_key=True, index=True)
    DTL_id = Column(int, primary_key=True, autoincrement=True)  # 自動インクリメント
    TRD_id = Column(int, ForeignKey('transactions.TRD_id'))  # 外部キーとして定義
    PRD_id = Column(int)
    PRD_code = Column(CHAR(13))
    PRD_name = Column(VARCHAR(50))
    PRD_price = Column(int)
    TAX_category = Column(CHAR(2))
    transactions = relationship('transactions')

class Tax_Master(Base):
    __tablename__ = "TAX_master"
    TAX_id = Column(int, primary_key=True, index=True)
    TAX_code = Column(CHAR(2))
    TAX_name = Column(VARCHAR(20)) # 50から20に変更
    percent = Column(decimal)

class TransactionUpdate(Base):
    total_amount: decimal
    total_amount_ex_tax: decimal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)