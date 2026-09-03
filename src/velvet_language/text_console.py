"""Tiny local terminal surface for Velvet's shared conversation path."""

from __future__ import annotations

from .conversation_gateway import ConversationGateway, ConversationModality


def main() -> None:
    gateway = ConversationGateway(conversation_id="local-text-console")
    debug = False

    print("Velvet written conversation")
    print("Commands: /debug toggles turn details, /quit exits")

    while True:
        try:
            text = input("You> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        command = text.strip().lower()
        if command in {"/quit", "/exit"}:
            break
        if command == "/debug":
            debug = not debug
            print(f"Debug {'on' if debug else 'off'}.")
            continue
        if not text.strip():
            continue

        try:
            exchange = gateway.submit(text, modality=ConversationModality.TEXT)
        except (TypeError, ValueError) as exc:
            print(f"Velvet> I couldn't accept that turn: {exc}")
            continue

        print(f"Velvet> {exchange.reply.text}")

        if debug:
            request = exchange.request
            print(
                "[turn "
                f"{request.turn_number} | act={request.act.value} | "
                f"strategy={request.strategy.value} | "
                f"authority_check={request.requires_authority_check}]"
            )


if __name__ == "__main__":
    main()
