from django.forms import ModelForm, EmailInput, Textarea
from .models import Feedback


# This is a form on the About page of the website. People who use the website can use this form to provide input and
# feedback.
class NewFeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ('from_email', 'feedback_text')
        widgets = {
            'from_email': EmailInput(attrs={
                'placeholder': 'Email address',
                'style': 'width: 300px;',
                'class': 'form-control'
                }),
            'feedback_text': Textarea(attrs={
                'placeholder': 'Feedback',
                'style': 'width: 700px; height: 120px;',
                'class': 'form-control'})
        }
