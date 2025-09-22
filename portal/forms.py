from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Team, Submission, Announcement

class ParticipantRegistrationForm(UserCreationForm):
    """A detailed registration form for new participants."""
    full_name = forms.CharField(max_length=100, required=True)
    student_roll_number = forms.CharField(max_length=20, required=True)
    branch = forms.CharField(max_length=50, required=True)
    year_of_study = forms.IntegerField(min_value=1, max_value=4, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    skills = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "full_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["full_name"]
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                user_role='Participant',
                student_roll_number=self.cleaned_data.get('student_roll_number'),
                branch=self.cleaned_data.get('branch'),
                year_of_study=self.cleaned_data.get('year_of_study'),
                phone_number=self.cleaned_data.get('phone_number'),
                skills=self.cleaned_data.get('skills')
            )
        return user

class UserProfileForm(forms.ModelForm):
    """Form for participants to edit their own profile."""
    class Meta:
        model = UserProfile
        fields = ['about', 'highlight', 'skills', 'technical_skills', 'github_link', 'linkedin_link', 'phone_number']

class TeamCreateForm(forms.ModelForm):
    """Form for a participant to create a new team."""
    class Meta:
        model = Team
        fields = ['team_name', 'max_size']

class TeamJoinForm(forms.Form):
    """Form for a participant to join a team using an invite code."""
    team_code = forms.CharField(label="Team Invitation Code", max_length=8)

class SubmissionForm(forms.ModelForm):
    """Form for a team leader to submit their project."""
    class Meta:
        model = Submission
        fields = ['project_title', 'project_description', 'repo_link', 'demo_link', 'image_upload']

class AnnouncementForm(forms.ModelForm):
    """Form for Event Managers to create announcements."""
    class Meta:
        model = Announcement
        fields = ['title', 'message']


# Form for judges to submit scores and feedback
from .models import JudgingScore, Event
class JudgingScoreForm(forms.ModelForm):
    class Meta:
        model = JudgingScore
        fields = ['score', 'feedback']

# Form for event creation/editing
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'