from velvet_language import render_fallback


def test_warning_fallback_names_subsystem_and_degrades_cleanly():
    expression = render_fallback(
        {
            "event": "vehicle.can.connection_lost",
            "severity": "warning",
            "subsystem": "vehicle_can",
        }
    )

    assert expression.text == (
        "Vehicle can is unavailable. I'm continuing with reduced capability."
    )
    assert expression.interrupt is True
    assert expression.speak is True
    assert expression.display is True
    assert expression.generator == "deterministic-fallback"


def test_unknown_severity_does_not_invent_criticality():
    expression = render_fallback(
        {
            "event": "sensor.unknown",
            "severity": "mystery",
        }
    )

    assert expression.severity == "informational"
    assert expression.text == "That information is currently unavailable."
    assert expression.interrupt is False


def test_emergency_fallback_is_deterministic():
    expression = render_fallback(
        {
            "event": "guardian.emergency_language_failure",
            "severity": "emergency",
        }
    )

    assert expression.text == (
        "Critical system unavailable. Follow the emergency procedure now."
    )
    assert expression.interrupt is True
