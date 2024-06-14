import functools

import pandas as pd

__LENGTH_LOG = 50


# ロギング用のデコレータ関数
def logging_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        n = (__LENGTH_LOG - len(f" start {func.__name__} ")) // 2
        print("=" * n + f" start {func.__name__} " + "=" * n)
        result = func(*args, **kwargs)
        print("=" * (n + 1) + f" end {func.__name__} " + "=" * (n + 1))
        return result

    return wrapper


def str2float(num_str: str) -> float | None:
    try:
        num = float(num_str)
    except ValueError:
        # print(e)
        num = None
    return num


def diff_rows(df1, df2):
    # 2つのデータフレームが値のみが異なる行をdf2から抽出する
    # df1とdf2を比較し、異なる場所をTrue、同じ場所をFalseとするマスクを作成する
    mask = df1.ne(df2)

    # df2からマスクがTrueの行を抽出する
    diff_rows = df2[mask.any(axis=1)]
    return diff_rows


def str2each_type(df, type_str):
    if type_str == "str":
        return df.astype(str)
    elif type_str == "int":
        return df.astype(int)
    elif type_str == "float":
        return df.astype(float)
    elif type_str == "datetime":
        return pd.to_datetime(df)
    else:
        print("unknown type")
        return False


def count_status(df, column_name):
    if column_name not in df.columns:
        raise ValueError(f"Column {column_name} does not exist in the DataFrame")

    return df[column_name].value_counts()


def filter_data(df0, name=None, size_min=None, size_max=None, type_=None, status=None):
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

    # print(status)
    # print(size_min)
    # print(size_max)

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
