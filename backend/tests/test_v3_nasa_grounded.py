from app.sources.synthetic import SyntheticSource
from app.sources.ares_adapter import AresCampaignAdapter
from app.baseline.baseline_service import PersonalBaselineService
from app.risk.engine import RiskEngine

def test_scenario_a_seed_4101_osd684_orange():
    src = SyntheticSource(scenario="scenario_a", days=10)
    assert src.seed == 4101
    evt = RiskEngine(PersonalBaselineService()).evaluate(list(src.stream()))
    assert evt.state == "ORANGE"
    assert "OSD-684" in evt.osdr_studies_cited
    assert evt.playbook.id == "PB-MSK"
    assert "ILLUSTRATIVE DEMO VALUE" in evt.explanation.what_changed

def test_scenario_b_seed_939_osd939_and_osd1010_red():
    src = SyntheticSource(scenario="scenario_b", days=5)
    assert src.seed == 939
    evt = RiskEngine(PersonalBaselineService()).evaluate(list(src.stream()))
    assert evt.state == "RED"
    assert "OSD-939" in evt.osdr_studies_cited
    assert "OSD-1010" in evt.osdr_studies_cited
    assert evt.playbook.id == "PB-RAD"

def test_scenario_c_seed_816_osd816_and_missing_visual_gray():
    src = SyntheticSource(scenario="scenario_c", days=5)
    assert src.seed == 816
    evt = RiskEngine(PersonalBaselineService()).evaluate(list(src.stream()))
    assert evt.state == "RED"
    assert "OSD-816" in evt.osdr_studies_cited

    # Fault: missing visual input -> GRAY, never GREEN
    src_gray = SyntheticSource(scenario="normal", days=5, faults={"missing_metric": "visual_change", "missing_day": 5})
    evt_gray = RiskEngine(PersonalBaselineService()).evaluate(list(src_gray.stream()))
    assert evt_gray.state == "GRAY"

def test_source_unit_required_sentinel_quarantined_to_gray():
    src = SyntheticSource(scenario="normal", days=5, faults={"unmapped_unit_metric": "radiation_dose", "unmapped_day": 5})
    evt = RiskEngine(PersonalBaselineService()).evaluate(list(src.stream()))
    assert evt.state == "GRAY"
    assert evt.data_quality.mapping_status == "quarantined_to_gray"

def test_ares_campaign_adapter_streams_sustained_attention():
    adapter = AresCampaignAdapter(subject_id="Subject_1", days=5, radiation_lag=True)
    obs = list(adapter.stream())
    assert len(obs) == 5
    assert obs[-1].metric == "sustained_attention_task"
    assert obs[-1].unit == "task_score"
