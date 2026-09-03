"""Guided requirement discovery page."""

import streamlit as st

from ui.client import ApiError, client


def heading() -> None:
    st.markdown('<div class="advisor-kicker">Guided briefing</div>', unsafe_allow_html=True)
    st.title("把家的感受，變成可討論的條件")
    st.markdown('<div class="advisor-rule"></div>', unsafe_allow_html=True)
    st.write("先說說你想要的生活。系統會逐步釐清，資料不足時會明確列為待確認事項。")


def save_response(response: dict) -> None:
    st.session_state.session_id = response.get("session_id", st.session_state.get("session_id"))
    st.session_state.question = response.get("next_question")
    st.session_state.progress = response.get("progress", {})
    if response.get("done"):
        st.session_state.question = None
        st.session_state.finished = True


def question_input(question: dict):
    options = question.get("options") or []
    if options:
        labels = {item["label"]: item["value"] for item in options}
        if question.get("multi"):
            chosen = st.multiselect("請選擇適合的項目", labels)
            return [labels[label] for label in chosen]
        chosen = st.radio("請選擇一項", labels, index=None)
        return labels.get(chosen)
    return st.text_input("你的回答", placeholder="請輸入你目前知道的資訊")


heading()

if "session_id" not in st.session_state:
    with st.form("start-form"):
        utterance = st.text_area(
            "你對家的初步想像",
            height=140,
            placeholder="例如：想蓋兩層樓的家，採光要好，夏天不要太熱……",
        )
        submitted = st.form_submit_button("開始整理需求", type="primary", use_container_width=True)
    if submitted:
        if not utterance.strip():
            st.warning("請先寫下一些想法，再開始整理。")
        else:
            try:
                with st.spinner("正在整理你提到的面向……"):
                    save_response(client.start(utterance.strip()))
                st.rerun()
            except ApiError as exc:
                st.error(str(exc))
else:
    progress = st.session_state.get("progress", {})
    answered, total = progress.get("answered", 0), progress.get("total", 1)
    st.progress(min(answered / max(total, 1), 1.0), text=f"需求盤點 {answered} / {total}")
    question = st.session_state.get("question")
    if question:
        st.subheader(question.get("text", "請補充以下資訊"))
        reason = question.get("reason", "有助於釐清設計條件。")
        reason_html = (
            '<div class="question-reason"><strong>為什麼問這題</strong><br>'
            f"{reason}</div>"
        )
        st.markdown(reason_html, unsafe_allow_html=True)
        with st.form("question-form"):
            value = question_input(question)
            answer_col, skip_col = st.columns([3, 1])
            answer = answer_col.form_submit_button("送出回答", type="primary", use_container_width=True)
            skip = skip_col.form_submit_button("暫時跳過", use_container_width=True)
        try:
            if answer:
                save_response(client.answer(st.session_state.session_id, question["field"], value))
                st.rerun()
            if skip:
                save_response(client.skip(st.session_state.session_id, question["field"]))
                st.rerun()
        except ApiError as exc:
            st.error(str(exc))
    else:
        st.success("需求盤點已完成，可以前往「需求摘要與來源」查看結果。")

if st.session_state.get("session_id") and st.button("重新開始"):
    for key in ("session_id", "question", "progress", "finished", "summary"):
        st.session_state.pop(key, None)
    st.rerun()
