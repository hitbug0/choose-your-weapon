import pandas as pd  # type: ignore
import requests  # type: ignore
import streamlit as st
from modules.constants import (  # type: ignore
    DF_CONFIG,
    CsvRowData,
    CsvTableData,
    RowData,
    TableData,
)
from modules.utils import diff_rows, logging_decorator, str2each_type  # type: ignore
from pydantic import ValidationError

SERVER_URL = "http://localhost:8000"


# データベースからデータと最終更新時刻を取得
@st.cache_data(ttl=300)
@logging_decorator
def get_data_api(last_modified_time):
    response = requests.get(f"{SERVER_URL}/fetch")
    status_code = response.status_code
    if status_code != 200:
        return False, False, f"failed to get data. code:{status_code}"

    response_json = response.json()
    try:
        data = response_json["data"]
        df = pd.DataFrame(
            data,
            columns=list(DF_CONFIG.COLUMN_TYPE.keys()),
        )
    except KeyError:
        return False, False, "The 'data' field is not found in the response."

    try:
        last_modified_time = response_json["last_update"]
    except KeyError:
        return data, False, "The 'last_update' field is not found in the response."

    # 各カラムのデータ型を変更
    for col, type_str in DF_CONFIG.COLUMN_TYPE.items():
        df[col] = str2each_type(df[col], type_str)
    # print(f"got data (last modified at {last_modified_time})")

    return df, last_modified_time, True


@logging_decorator
def add_row_api(
    id_: str, name: str, type_: str, size_x, size_y, size_z: str, remarks: str
):
    # 以下はボタンが押された場合は以下を実行
    response = requests.post(
        f"{SERVER_URL}/add_row",
        json={
            "id_by_user": id_,
            "name": name,
            "type": type_,
            "size_x": size_x,
            "size_y": size_y,
            "size_z": size_z,
            "remarks": remarks,
        },
    )
    return response.status_code == 200


@logging_decorator
def upload_file_api(file):
    response = requests.post(f"{SERVER_URL}/upload_file", files={"file": file})
    return response.status_code == 200


@logging_decorator
def upload_csv_api(csv_):
    # CSVを読み込む(バリデーションのため)
    try:
        df = pd.read_csv(csv_)
        df = df.rename(
            columns={
                "id": "id_by_user",
                "size x": "size_x",
                "size y": "size_y",
                "size z": "size_z",
            }
        )
        for col, type_str in DF_CONFIG.COLUMN_TYPE.items():
            if col in list(df.columns):
                df[col] = str2each_type(df[col], type_str)
        # print(DF_CONFIG.COLUMN_TYPE)
        # print(df)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False

    return check_and_send_data(
        df, "upload_csv", requests.post, [CsvTableData, CsvRowData], message=csv_.name
    )


def modify_data_api(df, df_modified):
    df_diff = diff_rows(df, df_modified)
    print(df_diff)

    return check_and_send_data(
        df_diff,
        "update_data",
        requests.put,
        [TableData, RowData],
        message="modification",
    )


@logging_decorator
def check_and_send_data(df, url, method, datamodels, message=""):
    # データのバリデーション
    try:
        data_list = df.to_dict(orient="records")
        validated_data = datamodels[0](
            data=[datamodels[1](**item) for item in data_list], message=message
        )
        print(validated_data)
    except ValidationError as e:
        print(f"Data validation error: {e}")
        return False

    # データのアップロード
    response = method(f"{SERVER_URL}/{url}", json=validated_data.model_dump())

    # レスポンスの検証
    status_code = response.status_code
    if status_code != 200:
        print(f"failed to send data. code:{status_code}")
        return False
    print(response.json()["msg"])
    print(f"sent data successfully. (message: {message})")
    return True


@logging_decorator
def calc_api(message):
    # print(f"message: {message}")
    response = requests.post(
        f"{SERVER_URL}/calc",
        json={"message": message},
    )
    print(response)
    return response.status_code == 200


@logging_decorator
def register_api(message):
    response = requests.post(
        f"{SERVER_URL}/register",
        json={"message": message},
    )
    print(response)
    return response.status_code == 200
