import requests
import streamlit as st
from streamlit import session_state as sts


def add_single_row(div):
    # 行の追加
    div.subheader("Add Data")

    sts.type_ = sts.get("type", "")
    sts.name = sts.get("name", "")
    sts.size = sts.get("size", "")

    sts.name = div.text_input("Name", value=sts.name)
    sts.type_ = div.text_input("Type", value=sts.type_)
    sts.size = div.text_input("Size", value=sts.size)

    # ボタンが押されていない場合ははじく
    if not div.button("Add Row"):
        return None

    # 以下はボタンが押された場合
    response = requests.post(
        "http://localhost:8000/add_row",
        json={"name": sts.name, "type": sts.type_, "size": sts.size},
    )

    div.write(response.json())  # デバッグ用
    div.success(f"{sts.name} is added.")  # エラーハンドリングする

    sts.type_ = ""
    sts.name = ""
    sts.size = ""
    st.rerun()


count = 0  # add_files の upload回ごとに更新される


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
        "Upload files", accept_multiple_files=True, key=str(count)
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
        filename = response.json()["filename"]
        if response.status_code == 200:
            upload_log += [[div.success(f"{filename} uploaded successfully!"), 1]]
            # div.write(response.json())
        else:
            upload_log += [[div.error(f"Error uploading {filename}"), 0]]
            error_files += [filename]

        div.write(response.json())  # デバッグ用

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
    count %= 100  # でかくなりすぎないように100の剰余にする
    uploader_container.empty()
    button_container.empty()
    uploaded_files = uploader_container.file_uploader(
        "Upload files", accept_multiple_files=True, key=str(count)
    )
