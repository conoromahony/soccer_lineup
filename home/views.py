from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import NewFeedbackForm


# Create your views here.
@login_required
def home(request):
    return render(request, 'home/index.html',)


def faqs(request):
    return render(request, 'home/faqs.html',)


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


def thanks(request):
    return render(request, 'home/thanks.html',)
