import asyncio
import os
import random
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List
from uuid import uuid4

# 以下のimportにおける type: ignore は、誤判定を消すために記した
import aiofiles  # type: ignore
from fastapi import BackgroundTasks, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from .constants import FILE_SERVER, INSERT_SQL_COMMAND  # type: ignore
from .models import RowData, TableData  # type: ignore
from .utils import combine_without_duplication, get_db, init_db  # type: ignore

# todo: debug_mode = ""  # "no log", "upload_files", "fetch", "add_row", "update_data"


# 起動時と終了時に走る関数
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup event")
    init_db()
    # todo 計算中にサーバが落ちてcalculatingになったままのレコードに対して計算を実行する機能を追加する
    yield
    print("shutdown event")


app = FastAPI(lifespan=lifespan)


# データ全件と最終更新日時を取得する関数
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

    return JSONResponse(
        content={
            "data": all_data,
            "last_update": last_update,
            "msg": "all data is here",
        }
    )


# ファイルアップロード処理
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    # file.filenameの型検証 (os.path.join のため)
    if type(file.filename) is not str:
        return JSONResponse(
            content={"msg": "type of file.filename is not str (may be None)"}
        )

    file_location = os.path.join(FILE_SERVER, file.filename)
    async with aiofiles.open(file_location, "wb") as f:
        content = await file.read()
        await f.write(content)

    return JSONResponse(content={"filename": file.filename, "msg": "File uploaded"})


# csvアップロード処理
@app.post("/upload_csv")
async def upload_csv(uploaded_data: TableData):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    uuid0 = str(uuid4())

    # CSVの内容をDBに挿入
    for index, row in enumerate(uploaded_data.data):
        cursor.execute(
            INSERT_SQL_COMMAND,
            (
                uuid0 + f"_{str(index + 1).zfill(3)}",
                row.id_by_user,
                row.name,
                row.type,
                row.size_x,  # sizeが数値になっているかバリデーションを入れる
                row.size_y,
                row.size_z,
                row.remarks,
                now,
                now,
                "",
                -1,
                "just_uploaded",
            ),
        )
    conn.commit()
    conn.close()

    return JSONResponse(
        # content={"filename": uploaded_data.message, "msg": "CSV uploaded"}
        content={"filename": "uploaded_data.message", "msg": "CSV uploaded"}
    )


# 行追加処理
@app.post("/add_row")
async def add_row(data: RowData):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        INSERT_SQL_COMMAND,
        (
            data.uuid,
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
            "just_uploaded",
        ),
    )
    conn.commit()
    conn.close()
    return JSONResponse(content={"msg": "Row added"})


# データ更新処理
@app.put("/update_data")
async def update_data(update_data: TableData):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    for row in update_data.data:
        cursor.execute(
            """UPDATE table1 SET id_by_user=?,
                name=?,
                type=?,
                size_x=?,
                size_y=?,
                size_z=?,
                remarks=?,
                update_date=? WHERE uuid=?""",
            (
                row.id_by_user,
                row.name,
                row.type,
                row.size_x,
                row.size_y,
                row.size_z,
                row.remarks,
                now,
                row.uuid,
            ),
        )
    conn.commit()
    conn.close()
    return JSONResponse(content={"msg": "Data updated"})


# グローバル変数として計算タスク状態を保持
# 計算実行対象のレコードのuuidを入れていく # 量や計算時間によっては一時ファイル化などする
calculation_in_progress: List[str] = []
calculation_lock = asyncio.Lock()
register_in_progress: List[str] = []
register_lock = asyncio.Lock()


# 計算依頼処理
# todo 動くようにする
@app.put("/calc")
async def calc_data(background_tasks: BackgroundTasks):
    global calculation_in_progress

    # ステータスの更新
    # 更新した直後に異常終了して計算が実行されなかったケースを考える
    conn = get_db()
    cursor = conn.cursor()
    for row in calc_data.data:
        cursor.execute(
            """UPDATE table1 SET status=?,
                update_date=? WHERE uuid=?""",
            ("calculating", now, row.uuid),
        )
    conn.commit()
    conn.close()

    # 計算のバックグラウンド実行
    # DBにおいてjust_uploadedのものをcalculatingに一気に変える処理を書く。
    # その後が肝？　DBの扱いをどうするか（viewみたいなものを用意するか）
    now = datetime.now().isoformat()
    calc_uuid_list = [row.uuid for row in aaa]  # todo 考える
    print(aaa)
    async with calculation_lock:
        calculation_in_progress = combine_without_duplication(
            calculation_in_progress, calc_uuid_list
        )

    print(calculation_in_progress)
    for uuid in calc_uuid_list:
        # 同期関数を使って非同期タスクを実行する
        background_tasks.add_task(run_calculation_sync, uuid)

    return JSONResponse(content={"msg": "Calculation started"})


# 非同期関数を同期関数でラップする
def run_calculation_sync(uuid):
    asyncio.run(run_calculation(uuid))


# 計算実行（demo）
async def run_calculation(uuid):
    global calculation_in_progress
    await asyncio.sleep(20)  # シミュレート
    result = random.uniform(0, 1)

    async with calculation_lock:
        calculation_in_progress.remove(uuid)

    # ステータスの更新
    now = datetime.now().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE table1 SET status=?,
            update_date=?, rate=? WHERE uuid=?""",
        ("under_review", now, result, uuid),
    )
    conn.commit()
    conn.close()
    print(f"calc end at {now}: {uuid}")


# 登録依頼処理（作成中）# todo
@app.post("/register")
async def register_data(register_data: TableData):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    for row in register_data.data:
        cursor.execute(
            """UPDATE table1 SET status=?,
                update_date=? WHERE uuid=?""",
            (row.status, now, row.uuid),
        )
    conn.commit()
    conn.close()
    return JSONResponse(content={"msg": "Register requested"})


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
