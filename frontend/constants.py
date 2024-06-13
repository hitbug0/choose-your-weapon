from typing import List

import streamlit as st
from pydantic import BaseModel


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


DF_CONFIG = DfConfig(
    DF_WIDTH=2500,
    DF_HEIGHT=(260, 550),
    DISABLED_COLUMNS=[
        "uuid",
        "first_upload_date",
        "update_date",
        "rate",
        "status",
        "reference",  # todo これどうしようか。自動割り当て？
    ],
    COLUMN_CONFIG={
        "favorite": st.column_config.CheckboxColumn(  # todo　この辺書き換える
            "Your favorite?",
            help="Select your **favorite** widgets",
            default=False,
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
