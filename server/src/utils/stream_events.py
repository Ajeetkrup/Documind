from langgraph.config import get_stream_writer


def emit_stream_event(event_type: str, name: str | None = None, payload: dict | None = None) -> None:
    """Emit a custom LangGraph stream event when streaming is enabled."""
    try:
        writer = get_stream_writer()
    except RuntimeError:
        return

    event = {"type": event_type}
    if name:
        event["name"] = name
    if payload is not None:
        event["payload"] = payload

    writer(event)
