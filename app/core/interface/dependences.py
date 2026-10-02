from app.core.infrastructure.adapters.id_provider_adapter import EventIdProviderUUID7Adapter


def get_event_id_provider():
    return EventIdProviderUUID7Adapter()