from app.core.infrastructure.adapters.id_provider_impl import EventIdProviderUUID7Impl


def get_event_id_provider():
    return EventIdProviderUUID7Impl()