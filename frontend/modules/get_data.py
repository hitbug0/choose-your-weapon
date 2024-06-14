import pandas as pd
import requests
import streamlit as st
from modules.constants import DF_CONFIG  # type: ignore
from modules.utils import logging_decorator, str2each_type


# データベースからデータと最終更新時刻を取得
@st.cache_data(ttl=300)
@logging_decorator
def get_data(last_modified_time):
    response = requests.get("http://localhost:8000/fetch")
    if response.status_code != 200:
        return (
            False,
            False,
        )

    data = response.json()["data"]
    last_modified_time = response.json()["last_update"]
    df = pd.DataFrame(
        data,
        columns=list(DF_CONFIG.COLUMN_TYPE.keys()),
    )
    # 各カラムのデータ型を変更
    for col, type_str in DF_CONFIG.COLUMN_TYPE.items():
        df[col] = str2each_type(df[col], type_str)
    # print(f"got data (last modified at {last_modified_time})")
    return df, last_modified_time
