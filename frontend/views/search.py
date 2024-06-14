import streamlit as st

# 以下のimportにおける type: ignore は、誤判定を消すために記した
from modules.constants import CONTENTS_CONFIG  # type: ignore
from modules.utils import filter_data

# from api.input_validation import str2float


# 検索
def search(div, df):
    div.title("Search Commands")
    # with div.expander("search condition"):
    search_status = div.multiselect(
        "Status",
        options=CONTENTS_CONFIG.STATUS_OPTIONS,
        default=CONTENTS_CONFIG.DEFAULT_STATUS,
    )
    search_name = div.text_input("Name")
    search_type = div.text_input("Type")
    search_size_max = div.number_input("Max Size", value=None)
    search_size_min = div.number_input("Min Size", value=None)  # minの検索いらんか?
    filtered_df = filter_data(
        df,
        name=search_name,
        size_min=search_size_min,
        size_max=search_size_max,
        type_=search_type,
        status=search_status,
    )

    div.title("Reload")
    if div.button("Reload Data"):
        st.cache_data.clear()
        st.rerun()

    # print(filtered_df)
    return filtered_df
