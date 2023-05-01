from django.db import models


# This model is for the form on the About page of the website. It stores input and feedback provided by people who use
# the website.
class Feedback(models.Model):
    from_email = models.EmailField(verbose_name='Your email address:')
    feedback_text = models.TextField(verbose_name='And your feedback:')

    def __str__(self):
        # Returns a string representation of the model.
        return self.from_email
