from django.shortcuts import render, get_object_or_404
from .models import Player
from .forms import ChoosePositionsForm, NewPlayerForm
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages


# Create your views here.
def player_list(request):
    # This view displays the roster of players.
    # We retrieve the list of players using the "all_players" manager defined in models.py.
    players = Player.all_players.all()
    # Call the "render" function, passing the original request object, the template used to build the page,
    # and the data needed to build the page.
    return render(request, 'team/player/list.html', {'players': players})


@csrf_protect
def player_update(request, name):
    player = get_object_or_404(Player, name=name)
    # We use the same view for both displaying the form and for processing the submitted data.
    # If we receive a GET request, we display the form.
    # If we receive a POST request, the form is submitted and processed.
    if request.method == 'POST':
        if 'update_submit' in request.POST:
            # Create a form instance using the submitted data that is contained in the request.POST.
            form = ChoosePositionsForm(request.POST, instance=player)
            # Validate the submitted data using the form's is_valid() method.
            if form.is_valid():
                form.save()
        elif 'update_delete' in request.POST:
            player.delete()
        players = Player.all_players.all()
        return render(request, 'team/player/list.html', {'players': players})
    # When the view is loaded initially with a GET request, display the form.
    else:
        form = ChoosePositionsForm(instance=player)
    return render(request, 'team/player/update.html', {'form': form, 'player': player})


@csrf_protect
def player_add(request):
    if request.method == 'POST':
        form = NewPlayerForm(request.POST)
        # Validate the submitted data using the form's is_valid() method.
        if form.is_valid():
            player_name = form.cleaned_data.get("name")
            if not Player.objects.filter(name=player_name).exists():
                form.save()
            else:
                messages.error(request, 'Player already exists.')
                return render(request, 'team/player/add.html', {'form': form})
        players = Player.all_players.all()
        return render(request, 'team/player/list.html', {'players': players})
    # When the view is loaded initially with a GET request, display the form.
    else:
        form = NewPlayerForm()
    return render(request, 'team/player/add.html', {'form': form})
