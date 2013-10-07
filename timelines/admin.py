from django.contrib import admin

from .models import Timeline, TimelineSubscription, Milestone, Occurrence, Notification


class MilestoneAdmin(admin.ModelAdmin):
    list_filter = ('timeline',)
    list_display = ('name', 'timeline', 'offset')

admin.site.register(Timeline)
admin.site.register(TimelineSubscription)
admin.site.register(Milestone,  MilestoneAdmin)
admin.site.register(Occurrence)
admin.site.register(Notification)
