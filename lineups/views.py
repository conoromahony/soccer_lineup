from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Lineup
from team.models import Team
from .forms import NewLineupForm


# Create your views here.
@login_required
def lineup_list(request):
    lineups = Lineup.objects.filter(owner=request.user)
    return render(request, 'lineups/list.html', {'lineups': lineups})


@login_required
@csrf_protect
def view_lineup(request, lineup_id):
    lineup = get_object_or_404(Lineup, lineup_id=lineup_id)
    lineups = Lineup.objects.get(owner=request.user)
    # If the lineup is not in the lineups that are available to you???
    if player.team_name != my_team_name:
        raise Http404
    if request.method == 'POST':
        if 'update_submit' in request.POST:
            form = ChoosePositionsForm(request.POST, instance=player)
            if form.is_valid():
                form.save()
        elif 'update_delete' in request.POST:
            player.delete()
        players = Player.objects.filter(team_name=my_team_name)
        return render(request, 'team/player/list.html', {'players': players})
    else:
        form = ChoosePositionsForm(instance=player)
    return render(request, 'team/player/update.html', {'form': form, 'player': player})


@login_required
@csrf_protect
def new_lineup(request):
    team = Team.objects.get(owner=request.user)
    my_team_name = team.team_name
    number_of_minutes = 2 * team.half_duration
    number_players = 15
    number_subs = number_players - int(team.team_size)
    number_outfield = int(team.team_size) - 1
    if request.method == 'POST':
        form = NewLineupForm(request.POST)
        if form.is_valid():
            lineup_id = form.cleaned_data['opponent'] + str(form.cleaned_data['game_date'])
            if not Lineup.objects.filter(game_id=lineup_id).exists():
                instance = form.save(commit=False)
                instance.game_id = lineup_id
                instance.owner = request.user
                instance.save()
            else:
                messages.error(request, 'Lineup already exists.')
                return render(request, 'lineups/list.html')
        return render(request, 'lineups/list.html')
    else:
        form = NewLineupForm()
    return render(request, 'lineups/new_lineup.html', {'form': form, 'team': team})
