# https://qiita.com/takashiuesaka/items/491b21e9afb34bbb6e6d
# https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog
# https://qiita.com/KanNishida/items/f540a02e7ff561ecf915
# https://zenn.dev/levtech/articles/aee2cf0845cad9
# https://zenn.dev/dataheroes/articles/2eae5a5ad92534

from datetime import datetime

import streamlit as st

# 以下のimportにおける type: ignore は、誤判定を消すために記した
from api.api import get_data_api  # type: ignore
from modules.constants import CONTENTS_CONFIG  # type: ignore
from streamlit import session_state as stss
from views.add_data import add_data  # type: ignore
from views.check_status import check_status  # type: ignore
from views.metrics_and_register import metrics_and_register  # type: ignore
from views.modify_and_calc import modify_and_calc  # type: ignore
from views.search import search  # type: ignore


# セッション状態の初期化関数
# キャッシュは持たない。
# 時間がかかる処理ではないし、たまにキャッシュがあるのにセッション状態がないケースが起こり、バグにつながるため
def initialize_config_and_session_state():
    print("initialize_session_state")

    # ページ全般の設定
    st.set_page_config(layout="wide")

    # セッション状態の初期化
    if "last_modified_time" not in stss:
        stss.last_modified_time = datetime.now().isoformat()


# 初期ロード時のみ走る関数
# いかなる状況でも内容が変わらないコンテンツはここで定義しておく
@st.cache_data(ttl=60)
def initialize_static_contents():
    print("=============== initialize static contents ===============")

    # メインエリア
    st.header("Choose your weapons", divider="gray")


def main():
    initialize_config_and_session_state()
    initialize_static_contents()

    # データの取得
    df, stss["last_modified_time"], is_sccess = get_data_api(stss["last_modified_time"])
    if not is_sccess:
        st.write("Failed to get data.")
        return False

    tab_container = st.empty()

    # サイドバー
    # データのフィルタ結果を返す
    filtered_df = search(st.sidebar, df)

    # タブ
    # 選んだアクションに従ってアクションの表示と処理の呼び出す
    tabs = tab_container.tabs(CONTENTS_CONFIG.UTILITIES)
    with tabs[0]:
        print("tab0")
        add_data(filtered_df)

    with tabs[1]:
        print("tab1")
        modify_and_calc(filtered_df)

    with tabs[2]:
        print("tab2")
        metrics_and_register(df, filtered_df)

    with tabs[3]:
        print("tab3")
        check_status(df, filtered_df)


if __name__ == "__main__":
    main()
