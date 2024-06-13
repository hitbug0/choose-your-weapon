import time

import requests
import streamlit as st
from streamlit import session_state as sts


def add_single_row(div):
    global count
    # 行の追加
    div.subheader("Add Data")

    # テキストボックスの配置
    name = div.text_input("Name", "", key=f"add_single_row_name{count}")
    type_ = div.text_input("Type", "", key=f"add_single_row_type{count}")
    cols_size = div.columns(3)
    size_x = cols_size[0].text_input("Size 1", "", key=f"add_single_row_size_x{count}")
    size_y = cols_size[1].text_input("Size 2", "", key=f"add_single_row_size_y{count}")
    size_z = cols_size[2].text_input("Size 3", "", key=f"add_single_row_size_z{count}")

    # ボタンが押されていない場合ははじく
    if not div.button("Add Row"):
        return None

    # 以下はボタンが押された場合
    response = requests.post(
        "http://localhost:8000/add_row",
        json={
            "name": name,
            "type": type_,
            "size_x": size_x,
            "size_y": size_y,
            "size_z": size_z,
        },
    )

    # div.write(response.json())  # デバッグ用
    print(response.json())  # デバッグ用
    div.success(f"{name} is added.")  # エラーハンドリングする

    count += 1
    count %= 10000  # でかくなりすぎないように10000の剰余にする
    time.sleep(3)
    st.rerun()


count = 0  # add_files によるアップロードの回ごとに更新される


def add_files(div):
    global count
    # ファイル一括アップロード
    div.subheader("Add Files")

    # コンテナの定義
    uploader_container = div.empty()
    button_container = div.empty()
    upload_log_container = div.empty()

    # 処理
    uploaded_files = uploader_container.file_uploader(
        "Upload files", accept_multiple_files=True, key=f"add_files_uploader{count}"
    )

    upload_log = []

    # アップロードファイルが未選択の場合ははじく
    if not uploaded_files:
        return None

    # ボタンが押されていない場合ははじく
    if not button_container.button("Upload"):
        return None

    error_files = []
    for file in uploaded_files:
        response = requests.post(
            "http://localhost:8000/upload_files", files={"file": file}
        )
        # アップロード結果を表示
        print(response)
        filename = response.json()["filename"]  # todo エラーハンドリングする
        if response.status_code == 200:
            upload_log += [[div.success(f"{filename} uploaded successfully!"), 1]]
        else:
            upload_log += [[div.error(f"Error uploading {filename}"), 0]]
            error_files += [filename]

        # div.write(response.json())  # デバッグ用
        print(response.json())  # デバッグ用

        # アップロード数が少ないときはそのまま
        # アップロード数が多く、かつ全部成功しているときはメッセージを短くする
        # アップロード数が多く、かつ失敗しているものがあるときは失敗しているものだけを表示する
        if len(upload_log) < 3:
            pass
        elif sum([m[1] for m in upload_log]) == len(upload_log):
            [m[0].empty() for m in upload_log]
            upload_log_container.success("all files uploaded successfully!")
        else:
            upload_log_container.error(
                f"Error uploading {error_files}. The other files uploaded successfully."
            )

    # 一連の処理が終わったらアップローダの中身やボタンを掃除する
    count += 1
    count %= 10000  # でかくなりすぎないように10000の剰余にする
    uploader_container.empty()
    button_container.empty()
    uploaded_files = uploader_container.file_uploader(
        "Upload files", accept_multiple_files=True, key=f"add_files_uploader{count}"
    )
    time.sleep(3)
    upload_log_container.empty()
