# Speech Expression Handoff

Velvet Language does not call Audio Studio directly.

When a `RenderedExpression` is approved for speech, Language converts it into a transport-neutral draft for the Event Protocol contract `velvet.speech-expression.v1` and event type `language.expression.speech_requested`.

## Boundary

```text
verified meaning
  -> language selection
  -> RenderedExpression
  -> SpeechExpressionDraft
  -> Runtime/Event Protocol publication
  -> Audio Studio
```

If `RenderedExpression.speak` is false, no speech draft is emitted.

The draft may carry wording and presentation context:

- response/expression identifier
- approved text
- severity
- audience
- driving load
- emergency context
- requested named delivery profile
- quiet/social presentation hints
- interrupt presentation intent
- generator and language policy version

It explicitly carries no command or actuation authority and declares that Language has not selected hardware or synthesis implementation.

## Delivery posture

Language may request a bounded delivery posture from existing conversational context:

- emergency context -> `emergency`
- warning/critical severity -> `warning`
- high driving load -> `high_driving_load`
- non-owner audience -> `guest_reserved`
- explicit quiet request -> `quiet_night`
- otherwise -> `owner_default`

`playful_social` requires explicit social permission. The request is still advisory: Audio Studio applies its own supported-profile and safety policy.

## Forbidden ownership

The handoff does not choose ALSA devices, speaker slots, output channels, TTS models, speaker IDs, gain, pitch, rate, Piper parameters, capabilities, tokens, Runtime authorization, or Court decisions.

Those responsibilities remain outside `velvet-language`.
