import matplotlib.pyplot as plt
import streamlit as st

# 以下のimportにおける type: ignore は、誤判定を消すために記した
from modules.constants import DF_CONFIG  # type: ignore
from modules.utils import count_status  # type: ignore


def metrics_and_register(df, filtered_df):
    # todo チェックボックスで登録するかどうかを選べるようにする
    df_container = st.dataframe(
        filtered_df,
        width=DF_CONFIG.DF_WIDTH,
        height=DF_CONFIG.DF_HEIGHT[0],
        hide_index=True,
        column_order=DF_CONFIG.COLUMN_ORDER,
    )
    cols = st.columns(3)
    cols[0].scatter_chart(data=filtered_df, x="size_x", y="rate")
    cols[1].bar_chart(
        filtered_df.sort_values("rate", ascending=False),
        x="name",
        y="rate",
    )
    df_count = count_status(df, "status")
    fig, ax = plt.subplots()
    ax.pie(list(df_count.values), labels=list(df_count.index))
    cols[2].pyplot(fig)


@st.experimental_dialog("Request Register")
def register(df):
    st.write("Are you sure you want to request register?")
    message = st.text_input("Any Comments:")
    if st.button("Request"):
        registered_data = json.loads(df.to_json(orient="records"))
        response = requests.post(
            "http://localhost:8000/register",
            json={"data": registered_data, "message": message},
        )
        print(response)
        st.session_state["last_modified_time"] = datetime.now().isoformat()
        st.rerun()
