from django.contrib import admin
from .models import UserProfile, Team, ProjectSubmission

# Register your models here to make them accessible in the Django admin panel.
admin.site.register(UserProfile)
admin.site.register(Team)
admin.site.register(ProjectSubmission)
