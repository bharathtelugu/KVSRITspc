from django.db import models
from django.contrib.auth.models import User

# It's good practice to extend the User model if you need extra fields.
class UserProfile(models.Model):
    # This line is the key. It creates a one-to-one link to Django's built-in User model.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Add any extra fields you want for a user here
    college_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    members = models.ManyToManyField(User, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProjectSubmission(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE) # A team can only submit one project
    title = models.CharField(max_length=200)
    description = models.TextField()
    github_link = models.URLField()
    demo_link = models.URLField(blank=True, null=True) # This link is optional
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} by {self.team.name}'
