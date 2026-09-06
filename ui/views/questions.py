"""Guided requirement discovery page."""

import streamlit as st

from ui.client import ApiError, client

PRIMARY_FIELDS = {
    "site": "land_number",
    "household": "routines",
    "budget": "includes",
    "lighting": "color_temp",
    "circulation": "priorities",
    "smart": "scenes",
}

ASPECT_LABELS = {
    "site": "基地",
    "household": "家庭成員與作息",
    "budget": "預算",
    "lighting": "光線氛圍",
    "circulation": "動線與收納",
    "smart": "數位設備",
    "climate": "氣候與熱環境",
}


def heading() -> None:
    st.markdown('<div class="advisor-kicker">Guided briefing</div>', unsafe_allow_html=True)
    st.title("把家的感受，變成可討論的條件")
    st.markdown('<div class="advisor-rule"></div>', unsafe_allow_html=True)
    st.write("先說說你想要的生活。系統會逐步釐清，資料不足時會明確列為待確認事項。")


def save_response(response: dict) -> None:
    st.session_state.session_id = response.get("session_id", st.session_state.get("session_id"))
    st.session_state.question = response.get("next_question")
    st.session_state.progress = response.get("progress", {})
    if "detected_aspects" in response:
        st.session_state.detected_aspects = response["detected_aspects"]
    if response.get("done"):
        st.session_state.question = None
        st.session_state.finished = True


def question_input(question: dict):
    group = question["field"]
    key = f"answer-{group}-{PRIMARY_FIELDS[group]}"
    options = question.get("options") or []
    if options:
        labels = {item["label"]: item["value"] for item in options}
        if question.get("multi"):
            chosen = st.multiselect("請選擇適合的項目", labels, key=key)
            return [labels[label] for label in chosen]
        chosen = st.radio("請選擇一項", labels, index=None, key=key)
        return labels.get(chosen)
    return st.text_input("地號", placeholder="請輸入你目前知道的資訊", key=key)


def extra_inputs(group: str) -> dict:
    """Render the fixed companion fields defined by the frozen contract."""

    def text(label, leaf):
        return st.text_input(label, key=f"answer-{group}-{leaf}").strip()

    def single(label, leaf, options):
        return st.radio(
            label,
            list(options),
            format_func=options.get,
            index=None,
            key=f"answer-{group}-{leaf}",
        )

    def multiple(label, leaf, options):
        return st.multiselect(
            label,
            list(options),
            format_func=options.get,
            key=f"answer-{group}-{leaf}",
        )

    def boolean(label, leaf):
        return single(label, leaf, {True: "是", False: "否"})

    if group == "site":
        return {
            "zoning": text("使用分區", "zoning"),
            "district": text("行政區（選填）", "district"),
        }
    if group == "household":
        return {
            "members": st.number_input(
                "居住人數（至少 1 人；尚不確定可留白）",
                min_value=1,
                value=None,
                step=1,
                key="answer-household-members",
            ),
            "has_elderly": boolean("有長輩一起住嗎？（選填）", "has_elderly"),
            "has_children": boolean("有幼童一起住嗎？（選填）", "has_children"),
        }
    if group == "budget":
        return {
            "total_twd": st.number_input(
                "總預算（新臺幣元，選填）",
                value=None,
                step=10000,
                key="answer-budget-total_twd",
            )
        }
    if group == "lighting":
        return {
            "brightness_preference": single(
                "亮度偏好（選填）",
                "brightness_preference",
                {"bright": "明亮", "soft": "柔和"},
            ),
            "dimmable": boolean("需要可調光嗎？（選填）", "dimmable"),
            "scene_control": boolean("需要情境控制嗎？（選填）", "scene_control"),
        }
    if group == "circulation":
        return {
            "storage_locations": multiple(
                "收納位置（選填）",
                "storage_locations",
                {
                    "entrance": "玄關",
                    "kitchen": "廚房",
                    "bedroom": "臥室",
                    "utility": "工作陽台／儲藏室",
                },
            )
        }
    if group == "smart":
        return {
            "control_mode": single(
                "操作方式",
                "control_mode",
                {
                    "voice": "語音",
                    "app": "手機",
                    "both": "語音與手機都要",
                },
            ),
            "devices": multiple(
                "智慧設備（選填）",
                "devices",
                {
                    "smart_lighting": "智慧照明設備",
                    "camera": "監視器",
                    "smart_lock": "智慧門鎖",
                    "av_system": "影音系統",
                    "smart_appliance": "智慧家電",
                },
            ),
        }
    raise ApiError("服務回傳了無法辨識的問題欄位。")


def answer_payload(question: dict, value, extra: dict):
    """Send the complete group without inventing values for unanswered inputs."""
    group = question.get("field")
    leaf = PRIMARY_FIELDS.get(group)
    if leaf is None:
        raise ApiError("服務回傳了無法辨識的問題欄位。")
    values = {leaf: value, **extra}
    return {key: item for key, item in values.items() if item is not None and item != ""}


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
    aspects = st.session_state.get("detected_aspects", [])
    if aspects:
        st.info("已辨識面向：" + "、".join(ASPECT_LABELS.get(item, item) for item in aspects))
    else:
        st.caption("目前尚未辨識出明確面向，接下來會逐組釐清需求。")
    progress = st.session_state.get("progress", {})
    answered, total = progress.get("answered", 0), progress.get("total", 1)
    st.progress(min(answered / max(total, 1), 1.0), text=f"需求盤點 {answered} / {total}")
    question = st.session_state.get("question")
    if question:
        if question.get("field") not in PRIMARY_FIELDS:
            st.error("服務回傳了無法辨識的問題欄位，請稍後再試。")
            st.stop()
        st.subheader(question.get("text", "請補充以下資訊"))
        reason = question.get("reason", "有助於釐清設計條件。")
        reason_html = (
            f'<div class="question-reason"><strong>為什麼問這題</strong><br>{reason}</div>'
        )
        st.markdown(reason_html, unsafe_allow_html=True)
        st.caption("尚不確定的欄位可留白，之後會列為待確認事項。")
        with st.form(f"question-form-{question['field']}"):
            value = question_input(question)
            extra = extra_inputs(question["field"])
            answer_col, skip_col = st.columns([3, 1])
            answer = answer_col.form_submit_button(
                "送出回答", type="primary", use_container_width=True
            )
            skip = skip_col.form_submit_button("暫時跳過", use_container_width=True)
        try:
            if answer:
                payload = answer_payload(question, value, extra)
                save_response(
                    client.answer(st.session_state.session_id, question["field"], payload)
                )
                st.rerun()
            if skip:
                save_response(client.skip(st.session_state.session_id, question["field"]))
                st.rerun()
        except ApiError as exc:
            st.error(str(exc))
    else:
        st.success("需求盤點已完成，可以前往「需求摘要與來源」查看結果。")

if st.session_state.get("session_id") and st.button("重新開始"):
    for key in list(st.session_state):
        if key.startswith("answer-"):
            st.session_state.pop(key, None)
    for key in ("session_id", "question", "progress", "finished", "summary", "detected_aspects"):
        st.session_state.pop(key, None)
    st.rerun()
