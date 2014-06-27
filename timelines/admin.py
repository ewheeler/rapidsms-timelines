from django.contrib import admin
from hvad.admin import TranslatableAdmin

from .models import Timeline
from .models import TimelineSubscription
from .models import Milestone
from .models import Occurrence
from .models import Notification
from .models import Reporter


class MilestoneAdmin(TranslatableAdmin):
    list_filter = ('timeline',)
    list_display = ('name', 'timeline', 'offset', 'all_translations')

admin.site.register(Timeline)
admin.site.register(TimelineSubscription)
admin.site.register(Milestone, MilestoneAdmin)
admin.site.register(Occurrence)
admin.site.register(Notification)
admin.site.register(Reporter)
