from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Event

class UserRegistrationForm(UserCreationForm):
    college = forms.CharField(max_length=100, required=True, help_text='Your current college or university.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create the associated UserProfile with the default 'Participant' role
            UserProfile.objects.create(
                user=user,
                college=self.cleaned_data.get('college'),
                role='Participant' 
            )
        return user

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'hero_section_details', 'registration_link', 'what_is_event', 'about_event', 'benefits',
            'registration_start', 'registration_end', 'event_start', 'event_end',
            'venue_name', 'venue_location', 'venue_google_map_link',
            'contact_email', 'contact_whatsapp', 'contact_instagram', 'contact_linkedin',
            'event_status'
        ]
        widgets = {
            'registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'event_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'event_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'hero_section_details': forms.Textarea(attrs={'rows': 3}),
            'what_is_event': forms.Textarea(attrs={'rows': 5}),
            'about_event': forms.Textarea(attrs={'rows': 5}),
            'benefits': forms.Textarea(attrs={'rows': 4}),
        }
