from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Player, Team
from .forms import ChoosePositionsForm, NewPlayerForm, NewTeamForm


# Create your views here.
@login_required
@csrf_protect
def player_list(request):
    # Using .get because there can be only one team per user
    # If people can have more than one team, will need to change this to filter
    team = Team.objects.get(owner=request.user)
    my_team_name = team.team_name
    form = NewTeamForm(instance=team)
    players = Player.objects.filter(team_name=my_team_name)
    # Call the "render" function, passing the original request object, the template used to build the page,
    # and the data needed to build the page.
    return render(request, 'team/player/list.html', {'team': team, 'form': form, 'players': players})


@login_required
@csrf_protect
def player_update(request, name):
    player = get_object_or_404(Player, name=name)
    team = Team.objects.get(owner=request.user)
    my_team_name = team.team_name
    if player.team_name != my_team_name:
        raise Http404
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
        players = Player.objects.filter(team_name=my_team_name)
        return render(request, 'team/player/list.html', {'players': players})
    # When the view is loaded initially with a GET request, display the form.
    else:
        form = ChoosePositionsForm(instance=player)
    return render(request, 'team/player/update.html', {'form': form, 'player': player})


@login_required
@csrf_protect
def player_add(request):
    if request.method == 'POST':
        form = NewPlayerForm(request.POST)
        # Validate the submitted data using the form's is_valid() method.
        if form.is_valid():
            player_name = form.cleaned_data.get("name")
            team = Team.objects.get(owner=request.user)
            my_team_name = team.team_name
            if not Player.objects.filter(name=player_name).exists():
                form.save()
                new_player = Player.objects.get(name=player_name)
                new_player.team_name = my_team_name
                new_player.save()
            else:
                messages.error(request, 'Player already exists.')
                return render(request, 'team/player/add.html', {'form': form})
        players = Player.objects.filter(team_name=my_team_name)
        return render(request, 'team/player/list.html', {'players': players})
    # When the view is loaded initially with a GET request, display the form.
    else:
        form = NewPlayerForm()
    return render(request, 'team/player/add.html', {'form': form})
