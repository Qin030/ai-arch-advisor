"""Guards the JSON schema and the Pydantic models against drifting apart.

They are two hand-maintained copies of one contract, so nothing stops someone
adding a required field to one and not the other. This test is that stop.
"""

from app.core.models import Requirement


def test_top_level_fields_match(schema):
    schema_fields = set(schema["properties"].keys())
    model_fields = set(Requirement.model_fields.keys())
    assert schema_fields == model_fields, (
        f"僅在 schema: {schema_fields - model_fields}｜"
        f"僅在 models.py: {model_fields - schema_fields}"
    )


def test_required_groups_match(schema):
    assert set(schema["required"]) == {"session_id", "region"}
    for name in ("session_id", "region"):
        assert Requirement.model_fields[name].is_required()


def test_ask_order_covers_every_prioritised_group(schema):
    order = schema["x-ask-order"]
    prioritised = {
        k for k, v in schema["properties"].items() if isinstance(v, dict) and "x-priority" in v
    }
    assert set(order) == prioritised, f"追問順序與 x-priority 不一致：{set(order) ^ prioritised}"


def test_every_refusal_has_all_four_fields(schema):
    required = {"confirm_with", "impact", "reason"}
    for name, prop in schema["properties"].items():
        if isinstance(prop, dict) and "x-refusal" in prop:
            missing = required - set(prop["x-refusal"])
            assert not missing, f"{name} 的 x-refusal 缺少 {missing}"


def test_examples_parse_as_requirements(example):
    for name in ("minimal", "complete", "refusal_triggered"):
        Requirement.model_validate(example(name))
