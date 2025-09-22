from django.db import models
from django.contrib.auth.models import User
import uuid

# Event mode and status choices (module level)
MODE_CHOICES = [
    ('physical', 'Physical'),
    ('virtual', 'Virtual'),
    ('hybrid', 'Hybrid'),
]
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
]

# ==============================================================================
# 1. USER & PROFILE MODELS
# ==============================================================================
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Judge', 'Judge'),
        ('Participant', 'Participant'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Participant')
    
    # Participant-specific profile details
    student_roll_number = models.CharField(max_length=20, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    highlight = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., 'AI Enthusiast | Web Developer'")
    branch = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 'CSE', 'EEE'")
    year_of_study = models.PositiveSmallIntegerField(blank=True, null=True, help_text="e.g., 1, 2, 3, 4")
    skills = models.TextField(blank=True, null=True, help_text="General skills, comma-separated")
    technical_skills = models.TextField(blank=True, null=True, help_text="Programming languages, tools, etc.")
    github_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_user_role_display()})"

# ==============================================================================
# 2. CORE EVENT MODELS
# ==============================================================================
class Event(models.Model):
    MODE_CHOICES = [('physical', 'Physical'), ('virtual', 'Virtual'), ('hybrid', 'Hybrid')]
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('completed', 'Completed'), ('canceled', 'Canceled')]

    event_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, help_text="A shorter title for headers")
    hero_section_details = models.TextField()
    registration_link = models.URLField(blank=True, null=True)
    # About Event
    about_item_name = models.CharField(max_length=255, blank=True, null=True)
    about_description = models.TextField(blank=True, null=True)
    # Why Participate (multiple items)
    # See EventBenefit model below
    # What is Event
    what_item_name = models.CharField(max_length=255, blank=True, null=True)
    what_description = models.TextField(blank=True, null=True)

    # Venue fields
    venue_name = models.CharField(max_length=200, blank=True, null=True)
    venue_location = models.CharField(max_length=300, blank=True, null=True)
    venue_google_map_link = models.URLField(blank=True, null=True)

    # Connect with Us fields
    contact_email = models.EmailField(blank=True, null=True)
    contact_whatsapp = models.CharField(max_length=20, blank=True, null=True)
    contact_instagram = models.URLField(blank=True, null=True)
    contact_linkedin = models.URLField(blank=True, null=True)
    event_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    event_start = models.DateTimeField(null=True, blank=True)
    event_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
class EventBenefit(models.Model):
    event = models.ForeignKey(Event, related_name='benefits', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    description = models.TextField()

    
    registration_start = models.DateTimeField()
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    event_mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='physical')
    benefits = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event_name

# ==============================================================================
# 3. EVENT DETAIL MODELS (Linked to Event)
# ==============================================================================
class ProblemStatement(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='problem_statements')
    title = models.CharField(max_length=255)
    description = models.TextField()
    time_to_unlock = models.DateTimeField(help_text="The problem statement will be visible after this time.")

class Schedule(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='schedules')
    schedule_id = models.AutoField(primary_key=True)
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    class Meta:
        ordering = ['day_number']

class SubSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='sub_schedules')
    title = models.CharField(max_length=255)
    time = models.TimeField()
    description = models.TextField()
    class Meta:
        ordering = ['time']

class Eligibility(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='eligibility')
    description = models.TextField()

class HowToParticipateStep(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveIntegerField()
    step_description = models.TextField()
    class Meta: ordering = ['step_number']

class FAQ(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()

class EventMedia(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='media')
    banner_image = models.ImageField(upload_to='event_media/')
    logo = models.ImageField(upload_to='event_media/')
    
class Organizer(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='organizers')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=200, blank=True, null=True)

class Certificate(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='certificates')
    template_link = models.URLField()
    eligibility_criteria = models.TextField()

class Resource(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    file_link = models.FileField(upload_to='event_resources/')

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedback')
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comments = models.TextField(blank=True, null=True)

# ==============================================================================
# 4. TEAM & SUBMISSION MODELS
# ==============================================================================
class Team(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='teams')
    team_name = models.CharField(max_length=100)
    team_code = models.CharField(max_length=8, unique=True, default=uuid.uuid4().hex.upper()[0:8])
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    max_size = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('event', 'team_name')

class TeamMember(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted')]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=50, default='Member')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('team', 'participant')

class Submission(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='submission')
    problem_statement = models.ForeignKey(ProblemStatement, on_delete=models.SET_NULL, null=True)
    project_title = models.CharField(max_length=200)
    project_description = models.TextField()
    repo_link = models.URLField(blank=True, null=True)
    demo_link = models.URLField(blank=True, null=True)
    image_upload = models.ImageField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class TeamInvite(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invites')
    invited_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    invited_at = models.DateTimeField(auto_now_add=True)

# ==============================================================================
# 5. JUDGING & NOTIFICATION MODELS
# ==============================================================================
class JudgingScore(models.Model):
    judge = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores_given')
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='scores')
    score = models.FloatField()
    feedback = models.TextField(blank=True, null=True)
    class Meta: unique_together = ('judge', 'submission')

class Announcement(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# ==============================================================================
# 6. INVITE CODE MODEL
# ==============================================================================
class InviteCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    uses_count = models.PositiveIntegerField(default=0)
    max_uses = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.code