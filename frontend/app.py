from datetime import datetime

import matplotlib.pyplot as plt
import streamlit as st

# 以下のimportにおける type: ignore は、誤判定を消すために記した
from add_data import add_csv, add_files, add_single_row  # type: ignore
from constants import CONTENTS_CONFIG, DF_CONFIG  # type: ignore
from filter_dataframe import filter_dataframe  # type: ignore
from get_data import check_size_type, get_data  # type: ignore
from modify_data import modify_data  # type: ignore

# セッション状態の初期化
if "last_modified_time" not in st.session_state:
    st.session_state["last_modified_time"] = datetime.now().isoformat()


def count_categories(df, column_name):
    if column_name not in df.columns:
        raise ValueError(f"Column {column_name} does not exist in the DataFrame")

    return df[column_name].value_counts()


# ページ全般の設定
st.set_page_config(layout="wide")

# データの取得
df, st.session_state["last_modified_time"] = get_data(
    st.session_state["last_modified_time"]
)


# メインエリア
st.header("Choose your weapons", divider="gray")
# st.title("Choose your weapons")
# title_container = st.empty()
tab_container = st.empty()


# サイドバー
st.sidebar.title("Search Commands")
# with st.sidebar.expander("search condition"):
search_status = st.sidebar.multiselect(
    "Status",
    options=CONTENTS_CONFIG.STATUS_OPTIONS,
    default=CONTENTS_CONFIG.DEFAULT_STATUS,
)
search_name = st.sidebar.text_input("Name")
search_type = st.sidebar.text_input("Type")
search_size_max_str = st.sidebar.text_input("Max Size")
search_size_min_str = st.sidebar.text_input("Min Size")  # minの検索いらんか?
filtered_df = filter_dataframe(
    df,
    name=search_name,
    size_min=check_size_type(search_size_min_str),
    size_max=check_size_type(search_size_max_str),
    type_=search_type,
    status=search_status,
)

st.sidebar.title("Reload")
if st.sidebar.button("Reload Data"):
    st.cache_data.clear()
    st.rerun()
# print(filtered_df)


# 選んだアクションに従ってアクションの表示と処理の呼び出す
tabs = tab_container.tabs(CONTENTS_CONFIG.UTILITIES)
with tabs[0]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_CONFIG.DF_WIDTH,
        height=DF_CONFIG.DF_HEIGHT[0],
        hide_index=True,
        column_order=DF_CONFIG.COLUMN_ORDER,
    )
    columns_ = st.columns([2, 3])
    columns_[0].subheader("Upload")
    add_files(columns_[0])
    add_csv(columns_[0])
    add_single_row(columns_[1])

with tabs[1]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_CONFIG.DF_WIDTH,
        height=DF_CONFIG.DF_HEIGHT[1],
        hide_index=True,
        column_order=DF_CONFIG.COLUMN_ORDER,
    )
    col_c = st.columns(1)[0]
    modify_data(col_c, df_container, filtered_df)

with tabs[2]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_CONFIG.DF_WIDTH,
        height=DF_CONFIG.DF_HEIGHT[0],
        hide_index=True,
        column_order=DF_CONFIG.COLUMN_ORDER,
    )
    cols = st.columns(3)
    cols[0].scatter_chart(data=filtered_df, x="size_x", y="rate")
    cols[1].bar_chart(
        filtered_df.sort_values("rate", ascending=False),
        x="name",
        y="rate",
    )
    df_count = count_categories(df, "status")
    fig, ax = plt.subplots()
    ax.pie(list(df_count.values), labels=list(df_count.index))
    cols[2].pyplot(fig)

    # 計算後の項目のみに絞る（disable）
    # 分析結果を載せる
    # チェックボックスで登録するかどうかを選べる

with tabs[3]:
    df_container = st.dataframe(
        filtered_df,
        width=DF_CONFIG.DF_WIDTH,
        height=DF_CONFIG.DF_HEIGHT[1],
        hide_index=True,
        column_order=DF_CONFIG.COLUMN_ORDER,
    )
    # 登録依頼後の項目のみに絞る（disable）
