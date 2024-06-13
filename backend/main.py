import asyncio
import io
import os
import sqlite3
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import aiofiles
import pandas as pd
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

DATABASE = "./database/database.db"
FILE_SERVER = "./file-server/"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup event")
    init_db()
    yield
    print("shutdown event")


app = FastAPI(lifespan=lifespan)


# データベース接続
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn


# DB初期化
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS table1 (
            uuid TEXT PRIMARY KEY,
            id_by_user TEXT,
            name TEXT NOT NULL,
            type TEXT,
            size_x REAL NOT NULL,
            size_y REAL NOT NULL,
            size_z REAL NOT NULL,
            remarks TEXT,
            first_upload_date TEXT NOT NULL,
            update_date TEXT NOT NULL,
            reference TEXT,
            rate REAL NOT NULL,
            status TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


# ファイルアップロード処理
@app.post("/upload_files")
async def upload_files(file: UploadFile = File(...)):
    file_location = os.path.join(FILE_SERVER, file.filename)
    async with aiofiles.open(file_location, "wb") as f:
        content = await file.read()
        await f.write(content)

    # summary.csvの処理
    if file.filename == "summary.csv":
        print("summary.csv来た")
        # CSVの内容をDBに挿入
        conn = get_db()
        cursor = conn.cursor()
        csv_data = pd.read_csv(io.StringIO(content.decode("utf-8")))
        uuid0 = str(uuid4())
        now = datetime.now().isoformat()
        for index, row in csv_data.iterrows():
            cursor.execute(
                """INSERT INTO table1 (
                        uuid,
                        id_by_user,
                        name,
                        type,
                        size_x,
                        size_y,
                        size_z,
                        remarks,
                        first_upload_date,
                        update_date,
                        reference,
                        rate,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    uuid0 + str(index + 1).zfill(3),
                    row["id"],
                    row["name"],
                    row["type"],
                    row["size x"],
                    row["size y"],
                    row["size z"],
                    row["remarks"],
                    now,
                    now,
                    "",
                    -1,
                    "just_uploaded",
                ),
            )
        conn.commit()
        conn.close()

    return JSONResponse(content={"filename": file.filename, "status": "File uploaded"})


# データ検索処理
# @app.get("/search")
# async def search_data(
#     name: Optional[str] = None, type: Optional[str] = None, size: Optional[str] = None
# ):
#     conn = get_db()
#     cursor = conn.cursor()
#     query = "SELECT * FROM table1 WHERE 1=1"
#     params = []
#     if name:
#         query += " AND name LIKE ?"
#         params.append(f"%{name}%")
#     if type:
#         query += " AND type LIKE ?"
#         params.append(f"%{type}%")
#     if size:
#         query += " AND size LIKE ?"
#         params.append(f"%{size}%")

#     cursor.execute(query, params)
#     data = cursor.fetchall()
#     conn.close()
#     return data


# データを全件取得し、最終更新日時を取得する関数
@app.get("/fetch")
async def fetch_data_and_last_update():
    conn = get_db()
    cursor = conn.cursor()

    # データ全件取得
    cursor.execute("SELECT * FROM table1")
    all_data = cursor.fetchall()

    # 最終更新日時取得
    cursor.execute("SELECT MAX(update_date) FROM table1")
    last_update = cursor.fetchone()[0]

    conn.close()

    return {"data": all_data, "last_update": last_update}


# 行追加処理
class RowData(BaseModel):
    id_by_user: str
    name: str
    type: str
    size_x: float = Field(gt=0)
    size_y: float = Field(gt=0)
    size_z: float = Field(gt=0)
    remarks: str
    status: Optional[str] = "just_uploaded"

    @validator("status")  # todo 書き換える
    def check_status(cls, v):
        allowed_statuses = {
            "just_uploaded",
            "calculating",
            "unregistered",
            "registering",
            "registered",
        }
        if v not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")
        return v


@app.post("/add_row")
async def add_row(data: RowData):
    conn = get_db()
    cursor = conn.cursor()
    uuid0 = str(uuid4())
    now = datetime.now().isoformat()
    cursor.execute(
        """INSERT INTO table1 (
                uuid,
                id_by_user,
                name,
                type,
                size_x,
                size_y,
                size_z,
                remarks,
                first_upload_date,
                update_date,
                reference,
                rate,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            uuid0,
            data.id_by_user,
            data.name,
            data.type,
            data.size_x,
            data.size_y,
            data.size_z,
            data.remarks,
            now,
            now,
            "",
            -1,
            "",
            "just_uploaded",
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "Row added"}


# データ更新処理
class UpdateData(BaseModel):
    data: List[RowData]


@app.put("/update_data")
async def update_data(update_data: UpdateData):
    conn = get_db()
    cursor = conn.cursor()
    for row in update_data.data:
        cursor.execute(
            """UPDATE table1 SET id_by_user=?, name=?, type=?, size=?, update_date=? WHERE uuid=?""",
            (
                row["id_by_user"],
                row["name"],
                row["type"],
                row["size_x"],
                row["size_y"],
                row["size_z"],
                datetime.now().isoformat(),
                row["uuid"],
            ),
        )
    conn.commit()
    conn.close()
    return {"status": "Data updated"}


# 添付ファイル追加処理
@app.post("/attach_file/{uuid}")
async def attach_file(uuid: str, file: UploadFile = File(...)):
    file_location = os.path.join(FILE_SERVER, file.filename)
    async with aiofiles.open(file_location, "wb") as f:
        content = await file.read()
        await f.write(content)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT reference FROM table1 WHERE uuid=?""", (uuid,))
    references = cursor.fetchone()[0]
    if references:
        references = references.split(",")
    else:
        references = []
    references.append(file.filename)
    cursor.execute(
        """UPDATE table1 SET reference=? WHERE uuid=?""", (",".join(references), uuid)
    )
    conn.commit()
    conn.close()
    return {"status": "File attached"}


# データ取得処理
@app.get("/get_data")
async def get_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table1")
    data = cursor.fetchall()
    conn.close()
    return data


# 計算依頼処理
class CalcData(BaseModel):
    data: List[RowData]


@app.post("/calc")
async def calc_data(calc_data: CalcData):
    conn = get_db()
    cursor = conn.cursor()
    for row in calc_data.data:
        cursor.execute(
            """UPDATE table1 SET status=? WHERE uuid=?""",
            (row["status"], row["uuid"]),
        )
    conn.commit()
    conn.close()
    return {"status": "Calculation requested"}


# 登録依頼処理（作成中）
class RegisterData(BaseModel):
    data: List[RowData]


@app.post("/register")
async def register_data(register_data: RegisterData):
    conn = get_db()
    cursor = conn.cursor()
    for row in register_data.data:
        cursor.execute(
            """UPDATE table1 SET status=? WHERE uuid=?""",
            (row["status"], row["uuid"]),
        )
    conn.commit()
    conn.close()
    return {"status": "Register requested"}
