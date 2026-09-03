"""Streamlit entry point."""

from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="築意｜建築前期決策助理",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

stylesheet = Path(__file__).with_name("style.css").read_text(encoding="utf-8")
st.markdown(f"<style>{stylesheet}</style>", unsafe_allow_html=True)

pages = {
    "開始規劃": [st.Page("views/questions.py", title="智慧追問")],
    "檢視成果": [
        st.Page("views/compare.py", title="多方案比較"),
        st.Page("views/summary.py", title="需求摘要與來源"),
    ],
}
st.navigation(pages).run()
