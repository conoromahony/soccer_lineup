from django.contrib import admin
from .models import Feedback


# Register your models here.
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('from_email', 'feedback_text')
