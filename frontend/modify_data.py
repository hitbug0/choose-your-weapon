import pandas as pd
import requests
import streamlit as st

DF_WIDTH = 2500


def modify_data(div, df_container, df):
    col_l, col_r = div.columns(8)[:2]
    checkbox_container = col_l.empty()
    button_container = col_r.empty()

    # 編集モードでなければ登録処理のみ
    if not checkbox_container.checkbox("Modify Mode"):
        if not button_container.button("Register Request"):
            return None

        registered_data = df.to_dict(orient="records")
        response = requests.post(
            "http://localhost:8000/register", json={"data": registered_data}
        )
        div.write(response.json())
        return None

    # 以下は編集モードの場合
    df_modified = df_container.data_editor(
        df,
        width=DF_WIDTH,
        column_config={
            "favorite": st.column_config.CheckboxColumn(
                "Your favorite?",
                help="Select your **favorite** widgets",
                default=False,
            )
        },
        disabled=[
            "uuid",
            "submit_date",
            "update_date",
            "rate",
            "registered",
        ],
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
    div.write(response.json())  # デバッグ用
