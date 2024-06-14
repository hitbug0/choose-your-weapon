# https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog
# https://qiita.com/KanNishida/items/f540a02e7ff561ecf915
# https://zenn.dev/levtech/articles/aee2cf0845cad9
import json
import time
from datetime import datetime

import requests
import streamlit as st
from modules.constants import DF_CONFIG
from modules.utils import diff_rows


def modify_data(df):
    df_container = st.empty()
    col_l, col_r = st.columns(8)[:2]
    checkbox_container = col_l.empty()
    button_container = col_r.empty()

    # 編集モードでなければデータ表示と計算依頼のみ
    if not checkbox_container.checkbox("Modify Mode"):
        df_container.dataframe(
            df,
            width=DF_CONFIG.DF_WIDTH,
            height=DF_CONFIG.DF_HEIGHT[1],
            hide_index=True,
            column_order=DF_CONFIG.COLUMN_ORDER,
        )

        if button_container.button("Request Calculation"):
            calc(df[df["status"] == "just_uploaded"])

        # st.write(response.json()) # デバッグ用
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
    inform_modified()
    # st.success("反映変更した")  # todo エラーハンドリング
    # st.write(response.json())  # デバッグ用
    print(response.json())
    time.sleep(3)
    st.session_state["last_modified_time"] = datetime.now().isoformat()
    st.rerun()


@st.experimental_dialog("Saved")
def inform_modified():
    st.write("Modification saved")


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
