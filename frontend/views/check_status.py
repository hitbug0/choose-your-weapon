import matplotlib.pyplot as plt
import streamlit as st

# 以下のimportにおける type: ignore は、誤判定を消すために記した
from modules.constants import DF_CONFIG  # type: ignore
from modules.utils import count_status  # type: ignore


def check_status(df, filtered_df):
    # todo 登録や計算の進捗を数値及びグラフで確認できる
    # todo グラフをそれっぽいものに変える
    st.dataframe(
        filtered_df,
        width=DF_CONFIG.DF_WIDTH,
        height=DF_CONFIG.DF_HEIGHT[0],
        hide_index=True,
        column_config=DF_CONFIG.COLUMN_CONFIG,
        column_order=DF_CONFIG.COLUMN_ORDER,
    )
    cols = st.columns(3)
    cols[0].scatter_chart(data=filtered_df, x="size_z", y="rate")
    cols[1].bar_chart(
        filtered_df.sort_values("rate", ascending=False),
        x="type",
        y="rate",
    )
    df_count = count_status(df, "status")
    fig, ax = plt.subplots()
    ax.pie(list(df_count.values), labels=list(df_count.index))
    cols[2].pyplot(fig)
