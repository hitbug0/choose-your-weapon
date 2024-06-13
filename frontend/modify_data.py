# https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog
# https://qiita.com/KanNishida/items/f540a02e7ff561ecf915
import json
import time
from datetime import datetime

import requests
import streamlit as st
from constants import DF_CONFIG


def diff_rows(df1, df2):
    # 2つのデータフレームが値のみが異なる行をdf2から抽出する
    # df1とdf2を比較し、異なる場所をTrue、同じ場所をFalseとするマスクを作成する
    mask = df1.ne(df2)

    # df2からマスクがTrueの行を抽出する
    diff_rows = df2[mask.any(axis=1)]
    return diff_rows


def modify_data(div, df_container, df):

    col_l, col_r = div.columns(8)[:2]
    checkbox_container = col_l.empty()
    button_container = col_r.empty()

    # 編集モードでなければ計算依頼のみ
    if not checkbox_container.checkbox("Modify Mode"):
        if button_container.button("Request Calculation"):
            calc(df[df["status"] == "just_uploaded"])

        # div.write(response.json()) # デバッグ用
        return None

    # 以下は編集モードの場合
    df_modified = df_container.data_editor(
        df,
        width=DF_CONFIG.DF_WIDTH,
        height=DF_CONFIG.DF_HEIGHT[1],
        column_config=DF_CONFIG.COLUMN_CONFIG,
        disabled=DF_CONFIG.DISABLED_COLUMNS,
        hide_index=True,
        column_order=DF_CONFIG.COLUMN_ORDER,
    )

    # 変更反映ボタンを押さなければ何もしない
    if not button_container.button("Save Changes"):
        return None

    # 以下は変更反映ボタンが押された場合
    # # orient='records': レコードごとにjson形式にする
    df_diff = diff_rows(df, df_modified)
    print(df_diff)

    response = requests.put(
        "http://localhost:8000/update_data",
        json={"data": json.loads(df_diff.to_json(orient="records"))},
    )
    st.success("反映変更した")  # todo エラーハンドリング
    # div.write(response.json())  # デバッグ用
    print(response.json())
    time.sleep(3)
    st.session_state["last_modified_time"] = datetime.now().isoformat()
    st.rerun()


@st.experimental_dialog("Calculate")
def calc(df):
    st.write("Are you sure you want to request calculation?")
    message = st.text_input("Any Comments:")
    if st.button("Request"):
        calc_data = json.loads(df.to_json(orient="records"))
        response = requests.post(
            "http://localhost:8000/calc",
            json={"data": calc_data, "message": message},
        )
        print(response)
        st.session_state["last_modified_time"] = datetime.now().isoformat()
        st.rerun()


@st.experimental_dialog("Request Register")
def register(df):
    st.write("Are you sure you want to request register?")
    message = st.text_input("Any Comments:")
    if st.button("Request"):
        registered_data = json.loads(df.to_json(orient="records"))
        response = requests.post(
            "http://localhost:8000/register",
            json={"data": registered_data, "message": message},
        )
        print(response)
        st.session_state["last_modified_time"] = datetime.now().isoformat()
        st.rerun()
