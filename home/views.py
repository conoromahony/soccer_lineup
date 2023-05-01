from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .forms import NewFeedbackForm


# This is the Home page.
@login_required
def home(request):
    return render(request, 'home/index.html',)


# This is the FAQs page.
def faqs(request):
    return render(request, 'home/faqs.html',)


# This is the About page.
@csrf_protect
def about(request):
    if request.method == 'POST':
        form = NewFeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'home/thanks.html')
    else:
        form = NewFeedbackForm()
    return render(request, 'home/about.html', {'form': form})


# This is a version of the About page that is display after someone provides feedback. In place of the feedback form,
# it displays a message thanking the user for their feedback.
def thanks(request):
    return render(request, 'home/thanks.html',)
