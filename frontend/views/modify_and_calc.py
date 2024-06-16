from datetime import datetime

import streamlit as st
from api.api import calc_api, modify_data_api
from modules.constants import DF_CONFIG
from streamlit import session_state as stss


def modify_and_calc(df):
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
            column_config=DF_CONFIG.COLUMN_CONFIG,
            column_order=DF_CONFIG.COLUMN_ORDER,
        )

        if button_container.button("Request Calculation"):
            calc()

        # st.write(response.json()) # デバッグ用
        return None

    # 以下は編集モードの場合
    df_modified = df_container.data_editor(
        df,
        width=DF_CONFIG.DF_WIDTH,
        height=DF_CONFIG.DF_HEIGHT[1],
        hide_index=True,
        column_config=DF_CONFIG.COLUMN_CONFIG,
        column_order=DF_CONFIG.COLUMN_ORDER,
        disabled=DF_CONFIG.DISABLED_COLUMNS,
    )

    # 変更反映ボタンを押さなければ何もしない
    if not button_container.button("Save Changes"):
        return None

    # 以下は変更反映ボタンが押された場合
    is_success = modify_data_api(df, df_modified)
    inform_modified(is_success)
    stss["last_modified_time"] = datetime.now().isoformat()
    st.rerun()


@st.experimental_dialog("Saved")
def inform_modified(is_success):
    print(is_success)
    if is_success:
        st.success("Modification saved")
    else:
        st.error("Modification failed")


@st.experimental_dialog("Calculate")
def calc():
    st.write("Are you sure you want to request calculation?")
    message = st.text_input("Any Comments:")
    is_success = False
    if st.button("Request"):
        is_success = calc_api(message)
    if is_success:
        stss["last_modified_time"] = datetime.now().isoformat()
        st.rerun()
