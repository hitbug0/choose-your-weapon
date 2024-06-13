FILE_SERVER = "./file-server/"


INSERT_SQL_COMMAND = """
INSERT INTO table1 (
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
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


STATUS_OPTIONS = [
    "just_uploaded",  # アップしたとこ
    "calculating",  # 計算中
    "under_review",  # 計算後のレビュー中
    "unregistered",  # 登録しないことにした
    "registering",  # 登録処理中
    "registered",  # 登録済み
]
