from django.db import models
from django.contrib.auth.models import User
import uuid

# --- USER AND TEAM MODELS (Updated with Roles & Skills) ---
class UserProfile(models.Model):
    # This is the corrected ROLE_CHOICES definition
    ROLE_CHOICES = [
        ('Participant', 'Participant'),
        ('Volunteer', 'Volunteer'),
        ('Technical Support', 'Technical Support'),
        ('Technical Lead', 'Technical Lead'),
        ('Lead Organizer', 'Lead Organizer'),
        ('Event Manager', 'Event Manager'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Participant')
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills, e.g., Python, UI/UX, Data Analysis")
    role_preference = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Developer, Designer, Researcher")

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

# --- CORE EVENT MANAGEMENT MODELS (Remains the same) ---
class Event(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('completed', 'Completed'), ('canceled', 'Canceled')]
    
    title = models.CharField(max_length=200)
    hero_section_details = models.TextField(help_text="Short, catchy description for the main page.")
    registration_link = models.URLField(blank=True, null=True)
    what_is_event = models.TextField(verbose_name="What is the Event?")
    about_event = models.TextField(verbose_name="About the Event")
    benefits = models.TextField(help_text="List the key benefits for participants.")
    
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()

    venue_name = models.CharField(max_length=200)
    venue_location = models.CharField(max_length=300)
    venue_google_map_link = models.URLField(blank=True, null=True)

    contact_email = models.EmailField()
    contact_whatsapp = models.CharField(max_length=20, blank=True, help_text="e.g., +91XXXXXXXXXX")
    contact_instagram = models.URLField(blank=True)
    contact_linkedin = models.URLField(blank=True)

    event_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# --- NEW TEAM MANAGEMENT MODELS ---
class Team(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    team_code = models.CharField(max_length=8, unique=True, default=uuid.uuid4().hex.upper()[0:8])
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    max_size = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'name')

    def __str__(self):
        return f"{self.name} ({self.event.title})"

class TeamMember(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted')]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=50, default='Member') # e.g., Developer, Designer
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.team.name}"

class TeamSubmission(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='submission')
    project_title = models.CharField(max_length=200)
    project_description = models.TextField()
    repo_link = models.URLField(blank=True, null=True)
    demo_link = models.URLField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Submission for {self.team.name}"


# --- RELATED EVENT MODELS (Remains the same) ---
class FAQ(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()

class Schedule(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='schedules')
    day_number = models.PositiveIntegerField()
    date = models.DateField()
    
    class Meta:
        ordering = ['day_number']

class SubSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='sub_schedules')
    start_time = models.TimeField()
    end_time = models.TimeField()
    activity = models.CharField(max_length=255)

    class Meta:
        ordering = ['start_time']

