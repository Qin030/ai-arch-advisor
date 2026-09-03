"""Pydantic models. The code-side twin of schema/requirement.schema.json.

The two MUST stay in sync — tests/smoke/test_contract_sync.py enforces it, and
the D10 proposal audit checks that the appendix in the proposal matches this too.
When you change a required field here, change it in the JSON schema in the same PR.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

ColorTemp = Literal["warm", "neutral", "cool"]
ControlMode = Literal["voice", "app", "both"]
Scene = Literal["arrive_home", "leave_home", "sleep", "security", "lighting"]


# --- requirement field groups -------------------------------------------------


class Site(BaseModel):
    land_number: str | None = None
    zoning: str | None = None
    district: str | None = None

    @model_validator(mode="after")
    def _need_one(self):
        # Mirrors the schema's anyOf. Either identifies the plot well enough to
        # look up zoning rules; neither means regulation fields get refused.
        if not (self.land_number or self.zoning):
            raise ValueError("site requires land_number or zoning")
        return self


class Project(BaseModel):
    building_type: Literal["detached_house"] | None = None
    # Fixed at 2, not a 1-2 range: MVP scenario in docs/SCOPE.md is locked to
    # "二層透天". A range would silently accept 1 floor, which issue #1's
    # review caught as inconsistent with that lock.
    floors: Literal[2] | None = None
    planned_floor_area_ping: float | None = None


class Household(BaseModel):
    members: int = Field(ge=1)
    has_elderly: bool | None = None
    has_children: bool | None = None
    routines: list[Literal["remote_work", "cooking_often", "entertaining", "pets"]] = []


class Budget(BaseModel):
    total_twd: int | None = None
    includes: list[Literal["land", "structure", "interior", "landscape"]] = []


class Lighting(BaseModel):
    color_temp: ColorTemp
    brightness_preference: Literal["bright", "soft"] | None = None
    dimmable: bool | None = None
    scene_control: bool | None = None


class Circulation(BaseModel):
    priorities: list[Literal["short_path", "storage", "automation", "accessibility"]] = []
    storage_locations: list[Literal["entrance", "kitchen", "bedroom", "utility"]] = []


class Smart(BaseModel):
    control_mode: ControlMode
    scenes: list[Scene] = Field(min_length=1)
    devices: list[
        Literal["smart_lighting", "camera", "smart_lock", "av_system", "smart_appliance"]
    ] = []


class Network(BaseModel):
    ap_points: int | None = Field(default=None, ge=0)


class Power(BaseModel):
    reserved_outlets: int | None = Field(default=None, ge=0)


class Requirement(BaseModel):
    session_id: str
    # Plain str, not Literal["tainan"]: a Literal would make pydantic reject an
    # out-of-allowlist region at deserialization (422), but CONTRACT.md requires
    # refusal to be a 200. The allowlist check happens in the rules layer against
    # app.core.config.settings.region_allowlist instead.
    region: str
    site: Site | None = None
    project: Project | None = None
    household: Household | None = None
    budget: Budget | None = None
    lighting: Lighting | None = None
    circulation: Circulation | None = None
    smart: Smart | None = None
    network: Network | None = None
    power: Power | None = None


# --- refusal ------------------------------------------------------------------


class Refusal(BaseModel):
    """One row of the 待專業人員確認清單.

    All four descriptive fields are required. A refusal without confirm_with or
    impact is useless to the user standing in front of an architect.
    """

    missing_field: str
    confirm_with: str
    impact: str
    reason: str
    blocks: list[str] = []


# --- questions & citations ----------------------------------------------------


class QuestionOption(BaseModel):
    value: str
    label: str


class Question(BaseModel):
    field: str
    text: str
    reason: str  # Required by design: every question states why it is asked.
    options: list[QuestionOption] = []
    multi: bool = False


class Citation(BaseModel):
    slice_id: str
    source_org: str
    source_url: str
    version_date: str
    region: str
    stale: bool = False


# --- request bodies -----------------------------------------------------------


class StartRequest(BaseModel):
    utterance: str


class TurnRequest(BaseModel):
    session_id: str
    field: str | None = None
    # A group answer bundles that group's leaf fields in one object (see
    # docs/CONTRACT.md's Question section) — not a bare scalar like a
    # leaf-field turn would use.
    value: dict[str, object] | None = None
    skip: bool = False


class SummaryRequest(BaseModel):
    session_id: str


# --- response envelopes --------------------------------------------------------


class Progress(BaseModel):
    answered: int
    total: int


class StartResponse(BaseModel):
    session_id: str
    requirement: Requirement
    detected_aspects: list[str] = []
    next_question: Question
    progress: Progress


class TurnResponse(BaseModel):
    requirement: Requirement
    next_question: Question | None
    progress: Progress
    done: bool


class DocumentSection(BaseModel):
    title: str
    content: str
    citations: list[str] = []


class DocumentSummary(BaseModel):
    sections: list[DocumentSection] = []


class ScanResult(BaseModel):
    filled: list[str] = []
    assumed: list[str] = []
    missing: list[str] = []


class PlanOption(BaseModel):
    label: str
    structure: str
    cost_range: str
    thermal_relative: str
    pending: list[str] = []
    citations: list[str] = []


class SummaryResponse(BaseModel):
    session_id: str
    scan: ScanResult
    building_summary: DocumentSummary
    digital_summary: DocumentSummary
    confirmations: list[Refusal] = []
    plans: list[PlanOption] = []
    citations: list[Citation] = []
