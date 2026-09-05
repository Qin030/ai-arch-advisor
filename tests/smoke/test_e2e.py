"""What `make demo` runs. Must be green before anyone stops for the day.

This file grows one step per day. Day 1 only checked the service starts and
the contract fixtures still parse. D2 walks the fixture flow end to end:
start -> turn through every x-ask-order group -> summary. The walk ignores
answer content on purpose — D2 has no decision tree yet, only a positional
walk through x-ask-order; by D6 it walks the real flow:
utterance -> questions -> requirement -> retrieval -> refusal -> three documents.
"""

from app.core.question_tree import ASK_ORDER


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    # A region outside the allowlist must never be answerable.
    assert body["region_allowlist"] == ["tainan"]


def test_turn_unknown_session_is_404_not_500(client):
    r = client.post("/turn", json={"session_id": "does-not-exist"})
    assert r.status_code == 404


def test_turn_rejects_leaf_style_value_with_400_and_no_progress(client):
    # docs/CONTRACT.md's Question/turn are group-level: `value` is an object
    # bundling that group's leaf fields, not a bare scalar. A leaf-style
    # request (the shape the old contract example used) must not validate.
    #
    # 400, not FastAPI's default 422: docs/CONTRACT.md 〈錯誤〉 gives exactly one
    # code for a request that does not match the schema.
    start = client.post("/session/start", json={"utterance": "test"})
    session_id = start.json()["session_id"]
    rejected = client.post(
        "/turn", json={"session_id": session_id, "field": "lighting", "value": "warm"}
    )
    assert rejected.status_code == 400

    # And it must not have consumed a group. docs/specs/translation-tree.md 二
    # step 3: a type error is not a "processed" turn — the client resends the
    # same group, it does not lose one. Asserted through observable state,
    # since D2 has no endpoint that reports progress on its own.
    accepted = client.post(
        "/turn",
        json={"session_id": session_id, "field": ASK_ORDER[0], "value": {"answer": "x"}},
    )
    assert accepted.status_code == 200
    assert accepted.json()["progress"] == {"answered": 1, "total": len(ASK_ORDER)}
    assert accepted.json()["next_question"]["field"] == ASK_ORDER[1]


def test_fixture_flow_walks_ask_order_to_summary(client):
    start = client.post("/session/start", json={"utterance": "我想蓋一棟兩層樓的透天厝"})
    assert start.status_code == 200
    body = start.json()
    session_id = body["session_id"]
    assert body["next_question"]["field"] == ASK_ORDER[0]
    assert body["progress"] == {"answered": 0, "total": len(ASK_ORDER)}

    # Walk every remaining group. `value` must at least be shaped like the
    # contract's group-level object even though D2's fixture ignores its
    # content by design — this is what PR review caught: a bare string
    # only proves D2 ignores input, not that it holds the request shape.
    for expected_answered in range(1, len(ASK_ORDER)):
        turn = client.post(
            "/turn",
            json={"session_id": session_id, "field": "x", "value": {"answer": "x"}},
        )
        assert turn.status_code == 200
        turn_body = turn.json()
        assert turn_body["progress"]["answered"] == expected_answered
        assert turn_body["next_question"]["field"] == ASK_ORDER[expected_answered]
        assert turn_body["done"] is False

    final = client.post(
        "/turn", json={"session_id": session_id, "field": "x", "value": {"answer": "x"}}
    )
    assert final.status_code == 200
    final_body = final.json()
    assert final_body["done"] is True
    assert final_body["next_question"] is None
    assert final_body["progress"] == {"answered": len(ASK_ORDER), "total": len(ASK_ORDER)}

    summary = client.post("/summary", json={"session_id": session_id})
    assert summary.status_code == 200
    summary_body = summary.json()
    # 拒答是回傳值，不是錯誤：四欄位必須都在。
    for confirmation in summary_body["confirmations"]:
        for field in ("missing_field", "confirm_with", "impact", "reason"):
            assert field in confirmation and confirmation[field]
