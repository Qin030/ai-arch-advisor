"""D3 HTTP acceptance tests from CONTRACT.md and translation-tree.md.

No implementation imports or mocks: exercise the public API via the existing
client fixture. D5 refusal/summary assertions require their own specification.
"""

import pytest

GROUPS = ("site", "household", "budget", "lighting", "circulation", "smart")
ASPECTS = {"lighting", "circulation", "smart"}
PRIMARY = {
    "site": None,
    "household": "routines",
    "budget": "includes",
    "lighting": "color_temp",
    "circulation": "priorities",
    "smart": "scenes",
}
ANSWERS = {
    "site": {"land_number": "測試地號", "district": "東區"},
    "household": {"members": 3, "has_elderly": False, "routines": ["remote_work"]},
    "budget": {"total_twd": 19000000, "includes": ["structure", "interior"]},
    "lighting": {"color_temp": "cool", "brightness_preference": "bright", "dimmable": False},
    "circulation": {"priorities": ["short_path"], "storage_locations": ["entrance"]},
    "smart": {"control_mode": "app", "scenes": ["sleep"], "devices": ["smart_lock"]},
}


def start(client, utterance="我想在臺南蓋房子"):
    response = client.post("/session/start", json={"utterance": utterance})
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body["session_id"], str) and body["session_id"]
    assert body["requirement"]["session_id"] == body["session_id"]
    assert body["progress"] == {"answered": 0, "total": 6}
    assert body["next_question"]["field"] == "site"
    return body


def turn(client, session_id, field, **answer):
    response = client.post(
        "/turn", json={"session_id": session_id, "field": field, **answer}
    )
    assert response.status_code == 200, response.text
    return response.json()


def assert_progress(body, answered):
    assert body["progress"] == {"answered": answered, "total": 6}
    assert body["done"] is (answered == 6)
    if answered == 6:
        assert body["next_question"] is None
    else:
        assert body["next_question"]["field"] == GROUPS[answered]


def reach(client, group):
    session_id = start(client)["session_id"]
    for index, preceding in enumerate(GROUPS[:GROUPS.index(group)], 1):
        assert_progress(turn(client, session_id, preceding, skip=True), index)
    return session_id


# PLAN.md Day 3: fifteen sentence -> aspect/first-question cases.
@pytest.mark.parametrize(
    ("utterance", "expected"),
    [
        ("希望家裡溫暖", {"lighting"}),
        ("希望家裡溫馨", {"lighting"}),
        ("希望家裡明亮", {"lighting"}),
        ("希望光線柔和", {"lighting"}),
        ("住起來要方便", {"circulation"}),
        ("空間要好用", {"circulation"}),
        ("東西拿起來順手", {"circulation"}),
        ("我要智慧家電", {"smart"}),
        ("想用手機控制", {"smart"}),
        ("要有監視器", {"smart"}),
        ("溫馨又方便", {"lighting", "circulation"}),
        ("智慧家電，光線柔和", {"lighting", "smart"}),
        ("好用、明亮，想用手機控制", ASPECTS),
        ("我想蓋房子", set()),
        ("基地在臺南東區，家裡三個人，預算一千九百萬元", set()),
    ],
)
def test_vocabulary_and_first_question(client, utterance, expected):
    body = start(client, utterance)
    detected = body["detected_aspects"]
    assert isinstance(detected, list)
    assert all(isinstance(aspect, str) for aspect in detected)
    # Other aspects (e.g. climate) are explicitly outside D3's detection spec.
    assert set(detected) & ASPECTS == expected
    # These groups are collected through questions, never prefilled from prose.
    for group in ("site", "household", "budget"):
        assert not body["requirement"].get(group)


@pytest.mark.parametrize("utterance", ["我想蓋房子", "溫馨、方便、智慧家電"])
def test_six_group_forms_and_server_side_answers(client, schema, utterance):
    body = start(client, utterance)
    session_id = body["session_id"]
    for index, group in enumerate(GROUPS):
        question = body["next_question"]
        definition = schema["properties"][group]
        assert question["field"] == group
        assert question["text"] == definition["x-question"]
        assert question["reason"] == definition["x-question-reason"]
        primary = PRIMARY[group]
        options = question["options"]
        if primary is None:
            assert options == []
            assert question["multi"] is False
        else:
            leaf = definition["properties"][primary]
            multi = leaf["type"] == "array"
            allowed = leaf["items"]["enum"] if multi else leaf["enum"]
            assert question["multi"] is multi
            values = [option["value"] for option in options]
            assert set(values) == set(allowed)
            assert len(values) == len(allowed)
            assert all(isinstance(o["label"], str) and o["label"].strip() for o in options)
        body = turn(client, session_id, group, value=ANSWERS[group])
        assert_progress(body, index + 1)
        assert body["requirement"]["session_id"] == session_id
        for answered_group in GROUPS[:index + 1]:
            for key, value in ANSWERS[answered_group].items():
                assert body["requirement"][answered_group][key] == value


def test_skips_advance_once_and_finished_session_is_idempotent(client):
    session_id = start(client)["session_id"]
    for index, group in enumerate(GROUPS, 1):
        final = turn(client, session_id, group, skip=True)
        assert_progress(final, index)
    for _ in range(2):
        repeated = turn(client, session_id, "smart", skip=True)
        assert_progress(repeated, 6)
        assert repeated["requirement"] == final["requirement"]


@pytest.mark.parametrize(
    ("group", "value"),
    [
        ("site", {"land_number": ""}),
        ("site", {}),
        ("household", {}),
        ("household", {"members": 2}),
        ("budget", {}),
        ("lighting", {}),
        ("circulation", {}),
        ("smart", {"control_mode": "app", "scenes": []}),
        ("smart", {}),
    ],
)
def test_incomplete_typed_answers_advance_without_reasking(client, group, value):
    session_id = reach(client, group)
    body = turn(client, session_id, group, value=value)
    assert_progress(body, GROUPS.index(group) + 1)


@pytest.mark.parametrize(
    ("group", "invalid"),
    [
        ("site", "bare string"),
        ("site", []),
        ("site", 42),
        ("site", {"land_number": []}),
        ("household", {"members": []}),
        ("budget", {"total_twd": {}}),
        ("lighting", {"color_temp": []}),
        ("smart", {"scenes": "sleep"}),
    ],
)
def test_bad_types_return_400_without_consuming_a_group(client, group, invalid):
    session_id = reach(client, group)
    for _ in range(2):
        response = client.post(
            "/turn", json={"session_id": session_id, "field": group, "value": invalid}
        )
        assert response.status_code == 400, response.text
    # Observable state check: a corrected request still advances exactly once.
    body = turn(client, session_id, group, value=ANSWERS[group])
    assert_progress(body, GROUPS.index(group) + 1)
    for key, value in ANSWERS[group].items():
        assert body["requirement"][group][key] == value


def test_sessions_do_not_share_answers_or_progress(client):
    first = start(client)["session_id"]
    second = start(client)["session_id"]
    assert first != second
    one = turn(client, first, "site", value={"land_number": "測試甲"})
    assert_progress(one, 1)
    two = turn(client, second, "site", value={"land_number": "測試乙"})
    assert_progress(two, 1)
    one = turn(client, first, "household", value={"members": 2})
    assert_progress(one, 2)
    assert one["requirement"]["site"]["land_number"] == "測試甲"
    two = turn(client, second, "household", value={"members": 4})
    assert_progress(two, 2)
    assert two["requirement"]["site"]["land_number"] == "測試乙"
    assert one["requirement"]["household"]["members"] == 2
    assert two["requirement"]["household"]["members"] == 4
