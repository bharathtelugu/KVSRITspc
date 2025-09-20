from django.db import models
from django.contrib.auth.models import User

# --- USER AND TEAM MODELS (Updated with Event Link) ---

class UserProfile(models.Model):
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

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

# --- CORE EVENT MANAGEMENT MODELS ---

class Event(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('completed', 'Completed'), ('canceled', 'Canceled')]
    
    # Core Details
    title = models.CharField(max_length=200)
    hero_section_details = models.TextField(help_text="Short, catchy description for the main page.")
    registration_link = models.URLField(blank=True, null=True)
    what_is_event = models.TextField(verbose_name="What is the Event?")
    about_event = models.TextField(verbose_name="About the Event")
    benefits = models.TextField(help_text="List the key benefits for participants.")
    
    # Timing
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()

    # Venue
    venue_name = models.CharField(max_length=200)
    venue_location = models.CharField(max_length=300)
    venue_google_map_link = models.URLField(blank=True, null=True)

    # Contact
    contact_email = models.EmailField()
    contact_whatsapp = models.CharField(max_length=20, blank=True, help_text="e.g., +91XXXXXXXXXX")
    contact_instagram = models.URLField(blank=True)
    contact_linkedin = models.URLField(blank=True)

    # Management Fields
    event_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# --- RELATED MODELS (Linked to Event) ---

class ProblemStatement(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='problem_statements')
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

class Schedule(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='schedules')
    day_number = models.PositiveIntegerField()
    date = models.DateField()
    
    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number} ({self.date}) - {self.event.title}"

class SubSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='sub_schedules')
    start_time = models.TimeField()
    end_time = models.TimeField()
    activity = models.CharField(max_length=255)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.activity}"

class Eligibility(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='eligibility_criteria')
    description = models.CharField(max_length=300, help_text="e.g., 'Open to all undergraduate students.'")

    def __str__(self):
        return self.description

class HowToParticipateStep(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participation_steps')
    step_number = models.PositiveIntegerField()
    description = models.TextField()

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number} for {self.event.title}"

class Organizer(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='organizers')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text="e.g., 'Event Coordinator'")
    contact_info = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.name

class FAQ(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()

    def __str__(self):
        return self.question

class Sponsor(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sponsors')
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='sponsor_logos/', blank=True, null=True)
    website_link = models.URLField(blank=True)
    sponsor_type = models.CharField(max_length=50, help_text="e.g., 'Gold', 'Silver', 'Media Partner'")

    def __str__(self):
        return self.name

# --- LEGACY MODELS TO BE PHASED OUT OR INTEGRATED ---
# For now, these are kept separate but should ideally be linked to an Event.

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    team_leader = models.OneToOneField(User, on_delete=models.CASCADE, related_name='led_team')
    members = models.ManyToManyField(User, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProjectSubmission(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    project_title = models.CharField(max_length=200)
    project_description = models.TextField()
    github_link = models.URLField(blank=True, null=True)
    demo_link = models.URLField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_title} by {self.team.name}"

