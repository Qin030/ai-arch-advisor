"""Three-document summary and expandable citations."""

import streamlit as st

from ui.client import ApiError, client


def render_sections(title: str, data: dict) -> None:
    st.subheader(title)
    sections = data.get("sections", [])
    if not sections:
        st.caption("目前沒有可確認的內容。")
    for section in sections:
        st.markdown(f"**{section.get('title', '未命名段落')}**")
        st.write(section.get("content", ""))
        refs = section.get("citations") or []
        if refs:
            st.caption("來源代碼：" + "、".join(refs))


st.markdown('<div class="advisor-kicker">Decision brief</div>', unsafe_allow_html=True)
st.title("需求摘要與來源")
st.markdown('<div class="advisor-rule"></div>', unsafe_allow_html=True)

session_id = st.session_state.get("session_id")
if not session_id:
    st.info("請先到「智慧追問」開始一輪需求盤點。")
    st.stop()

try:
    if "summary" not in st.session_state:
        with st.spinner("正在產出摘要……"):
            st.session_state.summary = client.summary(session_id)
    summary = st.session_state.summary
except ApiError as exc:
    st.error(str(exc))
    st.stop()

scan = summary.get("scan", {})
metric_cols = st.columns(3)
metric_cols[0].metric("已填", len(scan.get("filled", [])))
metric_cols[1].metric("可推定未確認", len(scan.get("assumed", [])))
metric_cols[2].metric("缺漏", len(scan.get("missing", [])))

building_tab, digital_tab, confirm_tab = st.tabs(["建築需求摘要", "家庭數位生活需求", "待專業人員確認"])
with building_tab:
    render_sections("建築需求摘要", summary.get("building_summary", {}))
with digital_tab:
    render_sections("家庭數位生活需求摘要", summary.get("digital_summary", {}))
with confirm_tab:
    confirmations = summary.get("confirmations", [])
    if not confirmations:
        st.success("目前沒有待確認事項。")
    for item in confirmations:
        missing_field = item.get("missing_field", "未指定欄位")
        confirm_with = item.get("confirm_with", "專業人員")
        st.markdown(f"**{missing_field}｜請洽 {confirm_with}**")
        st.write(item.get("reason", ""))
        st.caption("影響範圍：" + item.get("impact", "待確認"))

st.divider()
st.subheader("資料來源")
citations = summary.get("citations", [])
if not citations:
    st.caption("目前摘要沒有引用外部資料。")
for citation in citations:
    label = f"{citation.get('source_org', '來源未標示')}｜{citation.get('slice_id', '未編號')}"
    with st.expander(label):
        if citation.get("stale"):
            st.warning("此資料版本可能已過期，採用前請向專業人員確認。")
        st.write(f"發布機關：{citation.get('source_org', '未標示')}")
        st.write(f"版本日期：{citation.get('version_date', '未標示')}")
        st.write(f"適用地區：{citation.get('region', '未標示')}")
        if citation.get("source_url"):
            st.link_button("前往原始資料", citation["source_url"])
