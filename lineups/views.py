import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse

from .models import Lineup
from team.models import Team, Player
from .forms import NewLineupForm


MIN_SUB_CYCLES = 4
MAX_SUB_CYCLES = 7
NUM_GOALIES = 2


def get_lineup(players_present):
    lineup = []
    for player in players_present:
        lineup.append(player)
    return lineup


# Create your views here.
@login_required
def lineup_list(request):
    lineups = Lineup.objects.filter(owner=request.user)
    return render(request, 'lineups/list.html', {'lineups': lineups})


@login_required
@csrf_protect
def view_lineup(request, name):
    lineup = get_object_or_404(Lineup, game_id=name)
    lineups = Lineup.objects.filter(owner=request.user)
    # If the lineup is not in the lineups that are available to you???
    if lineup not in lineups:
        raise Http404
    return render(request, 'lineups/view_lineup.html', {'lineup': lineup})


@login_required
@csrf_protect
def new_lineup(request):
    team = Team.objects.get(owner=request.user)
    players = Player.objects.filter(team_name=team.team_name)
    players_present = []
    lineups = []
    my_team_name = team.team_name
    if request.method == 'POST':
        logging.info('11111111111')
        possible_goalies = []
        goalies = Player.objects.filter(team_name=team.team_name).filter(is_goalie=True)
        for player in goalies:
            possible_goalies = possible_goalies + [(player.name, player.name)]
        form = NewLineupForm(request.POST, choices=possible_goalies)
        if form.is_valid():
            logging.info('22222222222')
            lineup_id = form.cleaned_data['opponent'] + str(form.cleaned_data['game_date'])
            if not Lineup.objects.filter(game_id=lineup_id).exists():
                instance = form.save(commit=False)
                instance.game_id = lineup_id
                instance.team_name = my_team_name
                instance.owner = request.user
                for player in players:
                    if request.POST.get(player.name):
                        players_present.append([player.name, player.is_goalie, player.is_left_full,
                                                player.is_right_full, player.is_center_back, player.is_sweeper,
                                                player.is_stopper, player.is_left_mid, player.is_right_mid,
                                                player.is_attacking_mid, player.is_left_striker, player.is_right_striker])
                        logging.info(player.name)
                num_minutes = 2 * int(team.half_duration)
                num_players = len(players_present)
                on_sideline = num_players - int(team.team_size)
                num_outfield = int(team.team_size) - 1
                subs_determined = False
                if on_sideline <= 0:
                    slots_to_fill = 0
                    lineups.append(get_lineup(players_present))
                    subs_determined = True
                elif on_sideline == 1:
                    slots_to_fill = num_outfield
                    subs_determined = True
                else:
                    slots_to_fill = MAX_SUB_CYCLES
                    for sub_cycles in range(MIN_SUB_CYCLES, MAX_SUB_CYCLES):
                        cycle_slots = sub_cycles * num_outfield
                        if num_outfield == (on_sideline * sub_cycles):
                            slots_to_fill = sub_cycles
                            subs_determined = True
                            break
                        elif cycle_slots % (on_sideline * sub_cycles):
                            slots_to_fill = sub_cycles
                            break

                logging.info("Mins:%s Players:%s Outfield:%s Subs:%s Sub_cycles:%s", num_minutes, num_players, num_outfield, on_sideline, slots_to_fill)
                instance.number_subs = slots_to_fill
                instance.save()

            else:
                messages.error(request, 'Lineup already exists.')
                return render(request, 'lineups/list.html')

        view_lineup_url = lineup_id + '/view_lineup.html'
        lineup = get_object_or_404(Lineup, game_id=lineup_id)
        return redirect(view_lineup_url, {'lineup': lineup})
    else:
        possible_goalies = []
        goalies = Player.objects.filter(team_name=team.team_name).filter(is_goalie=True)
        for player in goalies:
            possible_goalies = possible_goalies + [(player.name, player.name)]
        logging.info(possible_goalies)
        form = NewLineupForm(choices=possible_goalies)
    return render(request, 'lineups/new_lineup.html', {'form': form, 'team': team, 'players': players})
