from django.db import models


# Create your models here.
class Feedback(models.Model):
    from_email = models.EmailField(verbose_name='Your email address:')
    feedback_text = models.TextField(verbose_name='And your feedback:')

    def __str__(self):
        # Returns a string representation of the model.
        return self.from_email
