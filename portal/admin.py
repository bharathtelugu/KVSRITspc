from django.contrib import admin
# Corrected the import from ProjectSubmission to TeamSubmission
from .models import UserProfile, Event, FAQ, Schedule, SubSchedule, Team, TeamMember, TeamSubmission 

# Register your models here
admin.site.register(UserProfile)
admin.site.register(Event)
admin.site.register(FAQ)
admin.site.register(Schedule)
admin.site.register(SubSchedule)
admin.site.register(Team)
admin.site.register(TeamMember)
# Register the correctly named model
admin.site.register(TeamSubmission)

