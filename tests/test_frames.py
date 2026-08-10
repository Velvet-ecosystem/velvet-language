import pytest

from velvet_language.frames import (
    MissingSlotError,
    SentenceFrame,
    UnknownSlotError,
    choose_and_realize,
    infer_slots,
    realize_frame,
)


def test_infer_slots_preserves_order_and_deduplicates():
    assert infer_slots("The {subject} is {condition}; {subject} remains online.") == (
        "subject",
        "condition",
    )


def test_realize_mild_condition_frame():
    frame = SentenceFrame(
        frame_id="observation.condition.mild.01",
        template="The {subject} is {condition} a bit.",
        required_slots=("subject", "condition"),
    )
    result = realize_frame(frame, {"subject": "engine", "condition": "sputtering"})
    assert result.text == "The engine is sputtering a bit."
    assert result.frame_id == frame.frame_id
    assert result.generator == "sentence-frame"


def test_same_frame_can_describe_lan():
    frame = SentenceFrame(
        frame_id="observation.condition.mild.01",
        template="The {subject} is {condition} a bit.",
        required_slots=("subject", "condition"),
    )
    result = realize_frame(frame, {"subject": "LAN", "condition": "lagging"})
    assert result.text == "The LAN is lagging a bit."


def test_missing_verified_slot_refuses_to_render():
    frame = SentenceFrame(
        frame_id="comparison",
        template="Mister, the {subject} is {condition} more than {reference}.",
        required_slots=("subject", "condition", "reference"),
    )
    with pytest.raises(MissingSlotError):
        realize_frame(frame, {"subject": "engine", "condition": "vibrating"})


def test_unknown_slots_are_rejected():
    frame = SentenceFrame(
        frame_id="simple",
        template="The {subject} is stable.",
        required_slots=("subject",),
    )
    with pytest.raises(UnknownSlotError):
        realize_frame(frame, {"subject": "CAN", "invented": "probably fine"})


def test_choose_first_compatible_frame():
    frames = [
        SentenceFrame(
            frame_id="needs_reference",
            template="The {subject} is {condition} more than {reference}.",
            required_slots=("subject", "condition", "reference"),
        ),
        SentenceFrame(
            frame_id="basic",
            template="The {subject} is {condition} a bit.",
            required_slots=("subject", "condition"),
        ),
    ]
    result = choose_and_realize(frames, {"subject": "engine", "condition": "sputtering"})
    assert result.frame_id == "basic"
    assert result.text == "The engine is sputtering a bit."
