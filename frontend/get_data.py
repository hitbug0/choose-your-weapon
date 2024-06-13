import pandas as pd
import requests
import streamlit as st


# メインエリア上部に表示する表の中身の取得
@st.cache_data
def get_data(last_modified_time):
    response = requests.get("http://localhost:8000/fetch")
    """
    # デカいDBの場合は以下のようにするが、今回はそこまで大きくないと思うので一気に持ってきてWebサーバ側でフィルタする感じでよさそう
    response = requests.get(
        "http://localhost:8000/search",
        params={"name": search_name, "type": search_type, "size": search_size},
    )
    """
    data = response.json()["data"]
    last_modified_time = response.json()["last_update"]
    print(last_modified_time)

    # todo: フロントエンドとバックエンドでlast_modyfied_time を上手に同期させる方法を考える。サーバ複数台や複数ユーザも考慮する

    df = pd.DataFrame(
        data,
        columns=[
            "uuid",
            "id_by_user",
            "name",
            "type",
            "size_x",
            "size_y",
            "size_z",
            "remarks",
            "first_upload_date",
            "update_date",
            "reference",
            "rate",
            "status",
        ],
    )
    # print(df)
    print("get_data: " + str(response))

    return (df, last_modified_time)
