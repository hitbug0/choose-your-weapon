from datetime import datetime

import streamlit as st
from add_data import add_files, add_single_row
from filter_dataframe import filter_dataframe
from get_data import get_data
from modify_data import modify_data

DF_WIDTH = 2500
DF_HEIGHT1 = 250
DF_HEIGHT2 = 550

# セッション状態の初期化
if "last_modified_time" not in st.session_state:
    st.session_state["last_modified_time"] = datetime.now().isoformat()


# 機能一覧
comment = """
# todo: ファイルサーバ空のファイル名取得とそれをプルダウンで選ぶ機能はまだできていない.削除もまだ。
"Add Data:                [追加] データベースへの行の追加、ファイルサーバへのファイルの追加(上書き保存のみ)
"Modify Data & Calculate: [更新/削除]データの確認/編集/削除と計算依頼
"Metrics & Register:      [更新] 計算結果が判明したデータのメトリクス確認
"Check Status:            [閲覧] 計算依頼/登録依頼をしたデータの内容確認/ステータス確認
"""
UTILITIES = [
    "Add Data　　　　",
    "Modify Data & Calculate　　　　",
    "Metrics & Register　　　　",
    "Check Status　　　　",
]

# ステータス一覧
# status_options = [  # データのフィルタリングのリスト
#     "just_uploaded",
#     "calculating",
#     "unregistered",
#     "registering",
#     "registered",
# ]
# default_status = ["uploaded"]
status_options = [  # データのフィルタリングのリスト
    "just_uploaded",
    "calculating",
    "unregistered",
    "registering",
    "registered",
]
default_status = [
    "just_uploaded",
    "calculating",
]


# ページ全般の設定
st.set_page_config(layout="wide")


# メインエリア
st.header("Choose your weapons", divider="gray")
# st.title("Choose your weapons")
# title_container = st.empty()
tab_container = st.empty()


# サイドバー
st.sidebar.title("Search Commands")
# with st.sidebar.expander("search condition"):
search_status_ = st.sidebar.multiselect(
    "Status", options=status_options, default=default_status
)
search_name = st.sidebar.text_input("name")
search_type = st.sidebar.text_input("type")
search_size_min = st.sidebar.text_input("min size")
search_size_max = st.sidebar.text_input("max size")

# todo: ちゃんとした入力バリデーションチェックを入れる
if search_size_min == "":
    search_size_min = None
if search_size_max == "":
    search_size_max = None


# データの取得
df, st.session_state["last_modified_time"] = get_data("last_modyfied_time")

# フィルタリング
filtered_df = filter_dataframe(
    df,
    name=search_name,
    size_min=search_size_min,
    size_max=search_size_max,
    type_=search_type,
    status=search_status_,
)
# print(filtered_df)

# 選んだアクションに従ってアクションの表示と処理の呼び出す
tabs = tab_container.tabs(UTILITIES)
with tabs[0]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_WIDTH,
        height=DF_HEIGHT1,
        hide_index=True,
    )
    col_l, col_r = st.columns(2)
    add_files(col_l)
    add_single_row(col_r)

with tabs[1]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_WIDTH,
        height=DF_HEIGHT1,
        hide_index=True,
    )
    col_c = st.columns(1)[0]
    modify_data(col_c, df_container, filtered_df)

with tabs[2]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_WIDTH,
        height=DF_HEIGHT1,
        hide_index=True,
    )
    # 計算後の項目のみに絞る（disable）
    # 分析結果を載せる
    # チェックボックスで登録するかどうかを選べる

with tabs[3]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_WIDTH,
        height=DF_HEIGHT2,
        hide_index=True,
    )
    # 登録依頼後の項目のみに絞る（disable）
