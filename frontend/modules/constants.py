from typing import List, Optional

import streamlit as st
from pydantic import BaseModel, Field, validator


# dataframeの表示に関する設定
class DfConfig(BaseModel):
    DF_WIDTH: int
    DF_HEIGHT: tuple[int, int]
    DISABLED_COLUMNS: List[str]
    COLUMN_CONFIG: dict
    COLUMN_TYPE: dict
    COLUMN_ORDER: List[str]


# 表示内容の設定
class ContentsConfig(BaseModel):
    UTILITIES: List[str]  # 機能一覧
    STATUS_OPTIONS: List[str]  # ステータス一覧
    DEFAULT_STATUS: List[str]  # ステータスのフィルタリングにおけるデフォルト値


# table1のカラムの型
__COLUMN_TYPE = {
    "uuid": "str",
    "id_by_user": "str",
    "name": "str",
    "type": "str",
    "size_x": "float",
    "size_y": "float",
    "size_z": "float",
    "remarks": "str",
    "first_upload_date": "datetime",
    "update_date": "datetime",
    "reference": "str",
    "rate": "float",
    "status": "str",
}

__DATE_FORMAT = "YYYY/MM/DD hh:mm"

DF_CONFIG = DfConfig(
    DF_WIDTH=2500,
    DF_HEIGHT=(210, 550),
    DISABLED_COLUMNS=[
        "uuid",
        "first_upload_date",
        "update_date",
        "rate",
        "status",
        "reference",  # todo これどうしようか。自動割り当て？
    ],
    COLUMN_CONFIG={
        "id_by_user": st.column_config.TextColumn(
            "ID",
            max_chars=50,
            # validate="^st\.[a-z_]+$",
        ),
        "name": st.column_config.TextColumn(
            "Name",
            max_chars=50,
        ),
        "type": st.column_config.TextColumn(
            "Type",
            max_chars=50,
        ),
        "size_x": st.column_config.NumberColumn(
            "Size X [cm]",
            help="size x of the weapon",
            min_value=0,
            max_value=1000,
            step=0.01,
            format="%.2f",
        ),
        "size_y": st.column_config.NumberColumn(
            "Size Y [cm]",
            help="size y of the weapon",
            min_value=0,
            max_value=1000,
            step=0.01,
            format="%.2f",
        ),
        "size_z": st.column_config.NumberColumn(
            "Size Z [cm]",
            help="size z of the weapon",
            min_value=0,
            max_value=1000,
            step=0.01,
            format="%.2f",
        ),
        "remarks": st.column_config.TextColumn(
            "Remarks",
            max_chars=200,
        ),
        "first_upload_date": st.column_config.DatetimeColumn(
            "First Added",
            # min_value=datetime(2023, 6, 1),
            # max_value=datetime(2025, 1, 1),
            format=__DATE_FORMAT,
            step=60,
        ),
        "update_date": st.column_config.DatetimeColumn(
            "Last Updated", format=__DATE_FORMAT, step=60
        ),
        "reference": st.column_config.ListColumn(
            "References",
            help="The reference files you have uploaded",
            width="medium",
        ),
        "rate": st.column_config.ProgressColumn(
            "Rate",
            format="%.2f",
            min_value=0,
            max_value=1,
        ),
        "status": st.column_config.TextColumn(
            "Status",
        ),
    },
    COLUMN_TYPE=__COLUMN_TYPE,
    COLUMN_ORDER=list(__COLUMN_TYPE.keys())[1:],
)

CONTENTS_CONFIG = ContentsConfig(
    UTILITIES=[
        "Add Data　　　　",
        "Modify Data & Calculate　　　　",
        "Metrics & Register　　　　",
        "Check Status　　　　",
        "Check Files　　　　",
    ],
    STATUS_OPTIONS=[
        "just_uploaded",  # アップしたとこ
        "calculating",  # 計算中
        "under_review",  # 計算後のレビュー中
        "unregistered",  # 登録しないことにした
        "registering",  # 登録処理中
        "registered",  # 登録済み
    ],
    DEFAULT_STATUS=[],
)

""" # 機能一覧
"Add Data:                [追加] データベースへの行の追加、ファイルサーバへのファイルの追加(上書き保存のみ)
"Modify Data & Calculate: [更新/削除]データの確認/編集/削除と計算依頼
"Metrics & Register:      [更新] 計算結果が判明したデータのメトリクス確認
"Check Status:            [閲覧] 計算依頼/登録依頼をしたデータの内容確認/ステータス確認
"Check Files:             [追加/閲覧/削除] 過去にアップロードしたファイルに関するデータ確認/アップロード/ダウンロード/削除
"""


class CsvRowData(BaseModel):
    id_by_user: str
    name: str
    type: str
    size_x: float = Field(gt=0)
    size_y: float = Field(gt=0)
    size_z: float = Field(gt=0)
    remarks: str


class CsvTableData(BaseModel):
    data: List[CsvRowData]
    message: Optional[str] = ""


class RowData(BaseModel):
    uuid: str
    id_by_user: str
    name: str
    type: str
    size_x: float = Field(gt=0)
    size_y: float = Field(gt=0)
    size_z: float = Field(gt=0)
    remarks: str
    status: str

    @validator("status")
    def check_status(cls, v):
        allowed_statuses = set(CONTENTS_CONFIG.STATUS_OPTIONS)
        if v not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")
        return v


class TableData(BaseModel):
    data: List[RowData]
    message: Optional[str] = ""
