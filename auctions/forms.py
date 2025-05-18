from django import forms
from .models import CATEGORY_CHOICES

class AuctionForm(forms.Form):
    image = forms.ImageField(
        label="Upload Image",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
        })
    )
    image_url = forms.URLField(
        label="Or Provide Image URL",
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'https://example.com/image.jpg',
            'autocomplete': 'off'
        })
    )
    title = forms.CharField(
        label="Title",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Enter a descriptive title',
            'autocomplete': 'off',
            'required': True
        })
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Describe your item in detail including condition, features, etc.',
            'rows': 5,
            'required': True
        })
    )
    price = forms.FloatField(
        label="Price",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': '0.00',
            'min': '0.01',
            'step': '0.01',
            'required': True
        })
    )
    category = forms.ChoiceField(
        label="Category",
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'required': True
        })
    )
    amount = forms.FloatField(
        label="Starting Bid",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': '0.00',
            'min': '0.01',
            'step': '0.01',
            'required': True
        })
    )


class BidForm(forms.Form):
    bid = forms.FloatField(
        label="",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 pl-10 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Enter your bid amount',
            'min': '0.01',
            'step': '0.01',
            'required': True,
            'autocomplete': 'off'
        })
    )


class CommentForm(forms.Form):
    comment = forms.CharField(
        label="",
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded text-gray-700 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Write your comment here...',
            'rows': 3,
            'required': True
        })
    )
