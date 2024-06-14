from datetime import datetime

import streamlit as st

# 以下のimportにおける type: ignore は、誤判定を消すために記した
from modules.constants import CONTENTS_CONFIG  # type: ignore
from modules.get_data import get_data  # type: ignore
from views.add_data import add_data  # type: ignore
from views.check_status import check_status  # type: ignore
from views.metrics_and_register import metrics_and_register  # type: ignore
from views.modify_data import modify_data  # type: ignore
from views.search import search  # type: ignore

# 開始ログ
n = 20
print("\n\n\n\n" + "=" * n + " start app " + "=" * n + "\n")

# セッション状態の初期化
if "last_modified_time" not in st.session_state:
    st.session_state["last_modified_time"] = datetime.now().isoformat()

# ページ全般の設定
st.set_page_config(layout="wide")

# データの取得
df, st.session_state["last_modified_time"] = get_data(
    st.session_state["last_modified_time"]
)

# メインエリア
st.header("Choose your weapons", divider="gray")
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
    modify_data(filtered_df)

with tabs[2]:
    print("tab2")
    metrics_and_register(df, filtered_df)

with tabs[3]:
    print("tab3")
    check_status(df, filtered_df)
