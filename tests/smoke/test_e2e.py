"""What `make demo` runs. Must be green before anyone stops for the day.

This file grows one step per day. Day 1 only checks the service starts and the
contract fixtures still parse; by D6 it walks the whole flow:
utterance -> questions -> requirement -> retrieval -> refusal -> three documents.
"""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    # A region outside the allowlist must never be answerable.
    assert body["region_allowlist"] == ["tainan"]


def test_unimplemented_endpoints_say_so(client):
    # D1: 501, not 500. A crash and "not built yet" are different signals.
    for path in ("/session/start", "/turn", "/summary"):
        r = client.post(path, json={"utterance": "x", "session_id": "x"})
        assert r.status_code in (501, 422), f"{path} -> {r.status_code}"
