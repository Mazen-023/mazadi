from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from .models import UserProfile, SecurityQuestion, User


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with styled widgets and additional fields."""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Email Address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Email Address'
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'bio', 'phone_number',
            'address_line1', 'address_line2', 'city',
            'state', 'postal_code', 'country'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Phone Number'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Address Line 1'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Address Line 2'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'State/Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Postal/Zip Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Country'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, user=None, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)

        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()

        if commit:
            profile.save()

        return profile


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styled widgets."""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Current Password'
        }),
        label="Current Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'New Password'
        }),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Confirm New Password'
        }),
        label="Confirm New Password"
    )


class SecurityQuestionForm(forms.Form):
    """Form for setting up security questions."""
    security_question1 = forms.ModelChoiceField(
        queryset=SecurityQuestion.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
        }),
        label="Security Question 1"
    )
    security_answer1 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Answer'
        }),
        label="Answer"
    )
    security_question2 = forms.ModelChoiceField(
        queryset=SecurityQuestion.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
        }),
        label="Security Question 2"
    )
    security_answer2 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Answer'
        }),
        label="Answer"
    )

    def save(self, user_profile):
        user_profile.security_question1 = self.cleaned_data['security_question1'].question
        user_profile.security_answer1 = self.cleaned_data['security_answer1']
        user_profile.security_question2 = self.cleaned_data['security_question2'].question
        user_profile.security_answer2 = self.cleaned_data['security_answer2']
        user_profile.save()
        return user_profile
