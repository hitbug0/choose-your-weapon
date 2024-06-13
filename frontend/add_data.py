import time
from datetime import datetime

import requests
import streamlit as st
from get_data import check_size_type  # type: ignore

count_row = 0  # アップロードの回ごとに更新される値
count_csv = 0  # アップロードの回ごとに更新される値
count_file = 0  # アップロードの回ごとに更新される値


def add_single_row(div):
    global count_row
    # DBへの行の追加
    div.subheader("Add Data")

    # テキストボックスの配置
    # keyを更新することで追加処理後に入力欄を空にできる
    cols_size = div.columns(3)
    id_ = cols_size[0].text_input(
        "ID (optional)", "", key=f"add_single_row_id_{count_row}"
    )
    name = cols_size[1].text_input("Name", "", key=f"add_single_row_name_{count_row}")
    type_ = cols_size[2].text_input("Type", "", key=f"add_single_row_type_{count_row}")
    cols_size = div.columns(3)
    size_x = cols_size[0].text_input(
        "Size 1", "", key=f"add_single_row_size_x_{count_row}"
    )
    size_y = cols_size[1].text_input(
        "Size 2", "", key=f"add_single_row_size_y_{count_row}"
    )
    size_z = cols_size[2].text_input(
        "Size 3", "", key=f"add_single_row_size_z_{count_row}"
    )
    remarks = div.text_input(
        "Remarks (optional)", "", key=f"add_single_row_remarks_{count_row}"
    )

    # ボタンが押されていない場合は終了
    if not div.button("Add Row"):
        return None

    # 以下はボタンが押された場合は以下を実行
    response = requests.post(
        "http://localhost:8000/add_row",
        json={
            "id_by_user": id_,
            "name": name,
            "type": type_,
            "size_x": check_size_type(size_x),
            "size_y": check_size_type(size_y),
            "size_z": check_size_type(size_z),
            "remarks": remarks,
        },
    )
    # div.write(response.json())  # デバッグ用
    # print(response.json())  # デバッグ用
    if response.json()["msg"] != "Row added":
        div.error(f"failed to add this record.")

    div.success(f"{name} is added.")

    count_row += 1
    count_row %= 10000  # 数字がでかくなりすぎないように10000の剰余にしている
    time.sleep(3)
    st.session_state["last_modified_time"] = datetime.now().isoformat()
    st.rerun()


def add_files(div):
    global count_file
    # ファイル一括アップロード

    # コンテナの定義
    uploader_container = div.empty()
    button_container = div.empty()
    upload_log_container = div.empty()

    # 処理
    uploaded_files = uploader_container.file_uploader(
        "Files", accept_multiple_files=True, key=f"add_files_uploader{count_file}"
    )

    upload_log = []

    # アップロードファイルが未選択の場合ははじく
    if not uploaded_files:
        return None

    # ボタンが押されていない場合ははじく
    if not button_container.button("Upload Files"):
        return None

    error_files = []
    for file in uploaded_files:
        response = requests.post(
            "http://localhost:8000/upload_files", files={"file": file}
        )
        # アップロード結果を表示
        if response.status_code == 200:
            filename = response.json()["filename"]
            upload_log += [[div.success(f"{filename} uploaded successfully!"), 1]]
        else:
            upload_log += [[div.error(f"Error uploading {file.name}"), 0]]
            error_files += [file.name]

        # print(response.json())  # デバッグ用

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
    count_file += 1
    count_file %= 10000  # でかくなりすぎないように10000の剰余にする
    uploader_container.empty()
    button_container.empty()
    uploaded_files = uploader_container.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        key=f"add_files_uploader{count_file}",
    )
    time.sleep(3)
    upload_log_container.empty()
    st.session_state["last_modified_time"] = datetime.now().isoformat()
    st.rerun()


def add_csv(div):
    global count_csv
    # ファイル一括アップロード

    # コンテナの定義
    uploader_container = div.empty()
    button_container = div.empty()
    upload_log_container = div.empty()

    # 処理
    uploaded_file = uploader_container.file_uploader(
        "CSV",
        accept_multiple_files=False,
        key=f"add_csv_uploader{count_csv}",
        type="csv",
    )

    # アップロードファイルが未選択の場合ははじく
    if not uploaded_file:
        return None

    # ボタンが押されていない場合ははじく
    if not button_container.button("Upload CSV"):
        return None

    response = requests.post(
        "http://localhost:8000/upload_csv", files={"file": uploaded_file}
    )

    # アップロード結果を表示

    if response.status_code == 200:
        filename = response.json()["filename"]
        div.success(f"{filename} uploaded successfully!")
        print(response.json()["msg"])
    else:
        div.error("Error uploading csv")

    # 一連の処理が終わったらアップローダの中身やボタンを掃除する
    count_csv += 1
    count_csv %= 10000  # でかくなりすぎないように10000の剰余にする
    uploader_container.empty()
    button_container.empty()
    uploaded_file = uploader_container.file_uploader(
        "Upload files", accept_multiple_files=True, key=f"add_csv_uploader{count_csv}"
    )
    time.sleep(3)
    upload_log_container.empty()
    st.session_state["last_modified_time"] = datetime.now().isoformat()
    st.rerun()
