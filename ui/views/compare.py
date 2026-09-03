"""Side-by-side plan comparison page."""

import streamlit as st

from ui.client import ApiError, client

st.markdown('<div class="advisor-kicker">Plan comparison</div>', unsafe_allow_html=True)
st.title("多方案比較")
st.markdown('<div class="advisor-rule"></div>', unsafe_allow_html=True)
st.write("用一致欄位並列比較；費用與熱環境僅呈現資料能支持的相對資訊。")

session_id = st.session_state.get("session_id")
if not session_id:
    st.info("請先到「智慧追問」開始一輪需求盤點。")
    st.stop()

try:
    if "summary" not in st.session_state:
        with st.spinner("正在整理比較方案……"):
            st.session_state.summary = client.summary(session_id)
    plans = st.session_state.summary.get("plans", [])
except ApiError as exc:
    st.error(str(exc))
    st.stop()

if not plans:
    st.info("目前沒有可比較的方案；請先補齊必要資訊。")
else:
    columns = st.columns(len(plans))
    for column, plan in zip(columns, plans, strict=True):
        with column:
            st.subheader(f"方案 {plan.get('label', '—')}")
            st.caption("構造與外牆策略")
            st.write(plan.get("structure", "待確認"))
            st.caption("工程費區間")
            st.write(plan.get("cost_range", "待確認"))
            st.caption("夏季熱環境（相對）")
            st.write(plan.get("thermal_relative", "待確認"))
            st.caption("待確認事項")
            pending = plan.get("pending") or ["無"]
            for item in pending:
                st.write(f"— {item}")
