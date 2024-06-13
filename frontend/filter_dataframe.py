import pandas as pd


def filter_dataframe(
    df0, name=None, size_min=None, size_max=None, type_=None, status=None
):
    """
    条件に基づいてDataFrameを検索します。

    Parameters:
    df0 (pd.DataFrame): 入力DataFrame
    name (str, optional): カラム'name'に対する部分一致検索文字列
    size_min (float, optional): カラム'size'の最小値
    size_max (float, optional): カラム'size'の最大値
    type_ (str, optional): カラム'type'に対する部分一致検索文字列
    status (List[str]): カラムに対する完全一致＆複数検索のリスト

    Returns:
    pd.DataFrame: フィルタリングされたDataFrame
    """
    # DataFrameをコピー
    df1 = df0.copy()

    print(status)
    print(size_min)
    print(size_max)

    # 'name'カラムに対する部分一致検索
    if name:
        df1 = df1[df1["name"].str.contains(name, na=False)]

    # 'type'カラムに対する部分一致検索
    if type_:
        df1 = df1[df1["type"].str.contains(type_, na=False)]

    # 'size'カラムに対する範囲検索
    if size_min is not None:
        df1 = df1[df1["size_x"] >= size_min]
        df1 = df1[df1["size_y"] >= size_min]
        df1 = df1[df1["size_z"] >= size_min]
    if size_max is not None:
        df1 = df1[df1["size_x"] <= size_max]
        df1 = df1[df1["size_y"] <= size_max]
        df1 = df1[df1["size_z"] <= size_max]

    # print(df1)
    # statusカラムに対する完全一致＆複数検索
    # 何も選択されていない場合、全てのデータを表示
    # 複数じゃなくてもよいかもしれない
    if status:
        df1 = df1[df1["status"].isin(status)]

    # print(
    #     f"[filtered] name: {name}, type: {type}, status: {status}, size_min: {size_min}"
    # )

    return df1
