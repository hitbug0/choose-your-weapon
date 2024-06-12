import pandas as pd
import requests
import streamlit as st


# メインエリア上部に表示する表の中身の取得
@st.cache_data
def get_data(last_modyfied_time):
    response = requests.get("http://localhost:8000/search")
    """
    # デカいDBの場合は以下のようにするが、今回はそこまで大きくないと思うので一気に持ってきてWebサーバ側でフィルタする感じでよさそう
    response = requests.get(
        "http://localhost:8000/search",
        params={"name": search_name, "type": search_type, "size": search_size},
    )
    """
    data = response.json()
    # todo: フロントエンドとバックエンドでlast_modyfied_time を上手に同期させる方法を考える。サーバ複数台や複数ユーザも考慮する

    df = pd.DataFrame(
        data,
        columns=[
            "uuid",
            "name",
            "type",
            "size",
            "submit_date",
            "update_date",
            "reference",
            "rate",
            "remarks",
            "registered",
        ],
    )

    return (df, last_modyfied_time)
