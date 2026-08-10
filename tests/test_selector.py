from velvet_language.models import MeaningPacket, ResponseVariant
from velvet_language.selector import SelectionContext, select_response


def test_selector_avoids_recent_variant_when_possible():
    meaning = MeaningPacket(event="can.connection_lost", severity="warning", audience="owner")
    variants = [
        ResponseVariant("can.owner.1", "Mister, CAN has disconnected.", "owner", "normal"),
        ResponseVariant("can.owner.2", "I've lost CAN communication, Mister.", "owner", "normal"),
    ]

    rendered = select_response(
        meaning,
        variants,
        SelectionContext(recent_response_ids=("can.owner.1",)),
    )

    assert rendered.response_id == "can.owner.2"
    assert rendered.generator == "catalog"


def test_emergency_catalog_is_deterministic_and_interrupts():
    meaning = MeaningPacket(event="runtime.emergency", severity="emergency", audience="owner")
    variants = [
        ResponseVariant("emergency.1", "Emergency condition detected.", "owner", "normal")
    ]

    rendered = select_response(meaning, variants)

    assert rendered.generator == "catalog-deterministic"
    assert rendered.interrupt is True


def test_missing_catalog_falls_back_truthfully():
    meaning = MeaningPacket(
        event="gnss.unavailable",
        severity="warning",
        audience="owner",
        subsystem="gnss",
    )

    rendered = select_response(meaning, [])

    assert rendered.generator == "deterministic-fallback"
    assert "Gnss" in rendered.text
