from django.contrib import admin
admin.site.site_header = 'CampusInnovate administration'
admin.site.site_title = 'CampusInnovate administration'
admin.site.index_title = 'CampusInnovate Dashboard'
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Event, FAQ, Schedule, SubSchedule, Team, TeamMember, 
    Submission, TeamInvite, Eligibility, HowToParticipateStep, Organizer, 
    ProblemStatement, JudgingScore, Announcement, Notification, 
    Certificate, Resource, Feedback, EventMedia, InviteCode
)

# --- User Profile Management ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_user_role', 'is_staff')
    list_select_related = ('userprofile',)

    def get_user_role(self, instance):
        if hasattr(instance, 'userprofile'):
            return instance.userprofile.get_user_role_display()
        return 'No Profile'
    get_user_role.short_description = 'Role'

# --- Event Management Inlines ---
class SubScheduleInline(admin.TabularInline): model = SubSchedule; extra = 1
class ScheduleInline(admin.StackedInline): model = Schedule; inlines = [SubScheduleInline]; extra = 1
class FAQInline(admin.TabularInline): model = FAQ; extra = 1
class EligibilityInline(admin.TabularInline): model = Eligibility; extra = 1
class HowToParticipateStepInline(admin.TabularInline): model = HowToParticipateStep; extra = 1
class OrganizerInline(admin.TabularInline): model = Organizer; extra = 1
class ProblemStatementInline(admin.TabularInline): model = ProblemStatement; extra = 1
class EventMediaInline(admin.StackedInline): model = EventMedia; can_delete = False

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'title', 'registration_link', 'about_item_name', 'what_item_name')
    inlines = [
        EventMediaInline, ScheduleInline, ProblemStatementInline, EligibilityInline,
        HowToParticipateStepInline, OrganizerInline, FAQInline,
    ]

# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Submission)
admin.site.register(TeamInvite)
admin.site.register(JudgingScore)
admin.site.register(Announcement)
admin.site.register(Notification)
admin.site.register(Certificate)
admin.site.register(Resource)
admin.site.register(Feedback)
admin.site.register(InviteCode)