# https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog

import time

import pandas as pd
import requests
import streamlit as st

DF_WIDTH = 2500
DF_HEIGHT1 = 250
DISABLED_COLUMNS = [
    "uuid",
    "first_upload_date",
    "update_date",
    "rate",
    "status",
]
# カラム名などは column_configで統一的に設定する
COLUMN_CONFIG = {
    "favorite": st.column_config.CheckboxColumn(  # todo　この辺書き換える
        "Your favorite?",
        help="Select your **favorite** widgets",
        default=False,
    ),
}


def modify_data(div, df_container, df):

    if "request_calculate" not in st.session_state:
        st.session_state["request_calculate"] = "init"

    col_l, col_r = div.columns(8)[:2]
    checkbox_container = col_l.empty()
    button_container = col_r.empty()

    # 編集モードでなければ登録処理のみ
    if not checkbox_container.checkbox("Modify Mode"):
        if button_container.button("Request Calculation"):
            submit(df)
        else:
            print(st.session_state.request_calculate)

        # div.write(response.json()) # デバッグ用
        return None

    # 以下は編集モードの場合
    df_modified = df_container.data_editor(
        df,
        width=DF_WIDTH,
        height=DF_HEIGHT1,
        column_config=COLUMN_CONFIG,
        disabled=DISABLED_COLUMNS,
        hide_index=True,
    )

    # 変更反映ボタンを押さなければ何もしない
    if not button_container.button("Save Changes"):
        return None

    # 以下は変更反映ボタンが押された場合
    print(df_modified)
    response = requests.put(
        "http://localhost:8000/update_data",
        json={"data": df_modified.to_json()},
    )
    st.success("反映変更した")  # todo エラーハンドリング
    # div.write(response.json())  # デバッグ用
    print(response.json())
    time.sleep(3)
    st.rerun()


@st.experimental_dialog("Request Calculation")
def submit(df):
    st.write("Are you sure you want to request calculation?")
    comment = st.text_input("Any Comments:")
    if st.button("Request"):
        registered_data = df.to_dict(orient="records")
        response = requests.post(
            "http://localhost:8000/register",
            json={"data": registered_data, "comment": comment},
        )
        st.session_state.request_calculate = response.json()
        st.rerun()
