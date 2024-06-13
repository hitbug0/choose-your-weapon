import pandas as pd
import requests
import streamlit as st
from constants import DF_CONFIG  # type: ignore


# データベースからデータと最終更新時刻を取得
@st.cache_data(ttl=300)
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
        df[col] = astype(df[col], type_str)
    # print(f"got data (last modified at {last_modified_time})")
    return df, last_modified_time


# todo: ちゃんとした入力バリデーションチェックを入れる
def check_size_type(num_str: str) -> float | None:
    try:
        num = float(num_str)
    except ValueError:
        # print(e)
        num = None
    return num


def astype(df, type_str):
    if type_str == "str":
        return df.astype(str)
    elif type_str == "int":
        return df.astype(int)
    elif type_str == "float":
        return df.astype(float)
    elif type_str == "datetime":
        return pd.to_datetime(df)
    else:
        print("unknown type")
        return False
