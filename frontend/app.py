import streamlit as st
from add_data import add_files, add_single_row
from get_data import get_data
from modify_data import modify_data

DF_WIDTH = 2500

# 機能一覧
comment = """
# todo: ファイルサーバ空のファイル名取得とそれをプルダウンで選ぶ機能はまだできていない.削除もまだ。
"Add Data:                         [追加] データベースへの行の追加、ファイルサーバへのファイルの追加(上書き保存のみ)
"Modify Data & Request Calculaing: [更新/削除]データの確認/編集/削除と計算依頼
"Calculating Progress:             [閲覧] 計算依頼をしたデータの内容確認/ステータス確認
"Metrics:                          [閲覧] 計算結果が判明したデータのメトリクス確認
"Registering Progress:             [閲覧] 登録依頼をしたデータの内容確認/ステータス確認
"""
UTILITIES = [
    "Add Data　　　　",
    "Modify Data & Request Calculaing　　　　",
    "Calculating Progress　　　　",
    "Metrics　　　　",
    "Registering Progress　　　　",
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
    "ItemA",
    "ItemB",
    "ItemC",
    "ItemD",
]
default_status = [
    "ItemA",
    "ItemB",
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
selected_status = st.sidebar.multiselect(
    "Status:", options=status_options, default=default_status
)
search_name = st.sidebar.text_input("name")
search_type = st.sidebar.text_input("type")
search_size = st.sidebar.text_input("min size")
# search_size2 = st.text_input("max size")


# データの取得とフィルタリング
df, last_modyfied_time = get_data("last_modyfied_time")
# todo: name, typeなどの検索も実装する
if selected_status:
    # filtered_df = df[df["Status"].isin(selected_status)]
    filtered_df = df[df["name"].isin(selected_status)]
else:
    filtered_df = df  # 何も選択されていない場合、全てのデータを表示


# 選んだアクションに従ってアクションの表示と処理の呼び出す
tabs = tab_container.tabs(UTILITIES)
with tabs[0]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_WIDTH,
        hide_index=True,
    )
    col_l, col_r = st.columns(2)
    add_files(col_l)
    add_single_row(col_r)

with tabs[1]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_WIDTH,
        hide_index=True,
    )
    col_c = st.columns(1)[0]
    modify_data(col_c, df_container, filtered_df)

with tabs[2]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_WIDTH,
        hide_index=True,
    )
    # 内容確認/修正が完了した後の項目に絞る

with tabs[3]:
    pass
    # 表とグラフの連携とかができそうならdfも表示する
    # df_container = st.dataframe(
    #     filtered_df,
    #     width=DF_WIDTH,
    #     hide_index=True,
    # )
    # 計算後の項目のみに絞る（disable）
    # 分析結果を載せる
    # チェックボックスで登録するかどうかを選べる

with tabs[4]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_WIDTH,
        hide_index=True,
    )
    # 登録依頼後の項目のみに絞る（disable）
