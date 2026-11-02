from app.core.infrastructure.persistence.tortoise.models import EventOutboxModel


class IamEventOutboxModel(EventOutboxModel):
    """iam 的事件 outbox（生产方自持，表随 iam 迁移）。"""

    class Meta:
        table = 'iam_event_outbox'
