from .models import Occurrence
import django_tables2 as tables


class ApptTable(tables.Table):
    timeline = tables.Column(accessor=tables.utils.A('milestone.timeline'),
                             order_by="milestone.timeline")
    connection = tables.Column(accessor=tables.utils.A('subscription.connection'),
                               order_by="subscription.connection")
    subscription = tables.Column(accessor=tables.utils.A('subscription.pin'),
                                 order_by="subscription.pin")
    milestone = tables.Column(orderable=False)
    message = tables.Column(accessor=tables.utils.A('milestone.message'),
                                 order_by="milestone.message")
    class Meta:
        model = Occurrence
        exclude = ('id', 'notes')
        sequence = ("timeline", "...", "connection", "subscription")
        attrs = {'id': 'timelines-table', 'class': 'table-striped'}
