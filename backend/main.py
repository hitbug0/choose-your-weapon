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
from pydantic import BaseModel

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
        name TEXT,
        type TEXT,
        size TEXT,
        submit_date TEXT,
        update_date TEXT,
        reference TEXT,
        rate TEXT,
        remarks TEXT,
        registered BOOLEAN
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
        # CSVの内容をDBに挿入
        conn = get_db()
        cursor = conn.cursor()
        csv_data = pd.read_csv(io.StringIO(content.decode("utf-8")))
        uuid0 = str(uuid4())
        for _, row in csv_data.iterrows():
            cursor.execute(
                """INSERT INTO table1 (
                        uuid,
                        name,
                        type,
                        size,
                        submit_date,
                        update_date,
                        reference,
                        rate,
                        remarks,
                        registered
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"{uuid0}_{row['id']}",
                    row["name"],
                    row["type"],
                    row["size"],
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    "",
                    "未検討",
                    "",
                    False,
                ),
            )
        conn.commit()
        conn.close()

    return JSONResponse(content={"filename": file.filename, "status": "File uploaded"})


# データ検索処理
@app.get("/search")
async def search_data(
    name: Optional[str] = None, type: Optional[str] = None, size: Optional[str] = None
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM table1 WHERE 1=1"
    params = []
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if type:
        query += " AND type LIKE ?"
        params.append(f"%{type}%")
    if size:
        query += " AND size LIKE ?"
        params.append(f"%{size}%")

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


# 行追加処理
class RowData(BaseModel):
    name: str
    type: str
    size: str


@app.post("/add_row")
async def add_row(data: RowData):
    conn = get_db()
    cursor = conn.cursor()
    uuid0 = str(uuid4())
    cursor.execute(
        """INSERT INTO table1 (
                uuid,
                name,
                type,
                size,
                submit_date,
                update_date,
                reference,
                rate,
                remarks,
                registered
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            uuid0,
            data.name,
            data.type,
            data.size,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            "",
            "未検討",
            "",
            False,
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
            """UPDATE table1 SET name=?, type=?, size=?, update_date=? WHERE uuid=?""",
            (
                row["name"],
                row["type"],
                row["size"],
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


# 登録処理
class RegisterData(BaseModel):
    data: List[RowData]


@app.post("/register")
async def register_data(register_data: RegisterData):
    conn = get_db()
    cursor = conn.cursor()
    for row in register_data.data:
        cursor.execute(
            """UPDATE table1 SET registered=? WHERE uuid=?""",
            (row["registered"], row["uuid"]),
        )
    conn.commit()
    conn.close()
    return {"status": "Registration updated"}
