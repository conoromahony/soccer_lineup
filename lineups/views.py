import logging
import ast
import random

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect

from .models import Lineup
from team.models import Team, Player
from .forms import NewLineupForm


MIN_SUB_CYCLES = 4
MAX_SUB_CYCLES = 7
NUM_GOALIES = 2
PLAYER_POSITIONS = ["left_full", "center_back", "sweeper", "right_full", "left_mid", "stopper", "attacking_mid",
                    "right_mid", "left_striker", "right_striker"]

def get_position(request, player, position):
    logging.info("position:" + position)
    position_list = Player.objects.filter(preferred_position=position)
    logging.info(position_list)
    if len(position_list) == 0:
        boolean_check = "is_left_full"
        logging.info("boolean_check: " + boolean_check)
        new_list = Player.objects.filter(is_left_full=True)
        logging.info(new_list)
        choose_player = random.choice(new_list)
        player = choose_player.name
    elif len(position_list) == 1:
        player = left_back_list[0].name
    else:
        choose_player = random.choice(position_list)
        player = choose_player.name
    return player


def get_lineup(request, slots_to_fill, players_present, first_goalie, second_goalie):
    logging.info(players_present)
    team = Team.objects.get(owner=request.user)
    players = Player.objects.filter(team_name=team.team_name)
    lineup = []
    if slots_to_fill == 0:
        minute = 0
        positions = [minute]
        goalie = first_goalie
        positions.append(goalie)
        for position_to_fill in PLAYER_POSITIONS:
            logging.info(position_to_fill)
            preferred_players = []
            for player in players_present:
                player_object = Player.objects.get(name=player[0])
                if player_object.preferred_position == position_to_fill:
                    if player_object.name not in positions:
                        preferred_players.append(player_object.name)
            logging.info(preferred_players)

            if len(preferred_players) == 0:
                boolean_check = "is_" + position_to_fill
                logging.info("boolean_check: " + boolean_check)
                plays_there = [player for player in players if getattr(player, boolean_check)]
                logging.info(plays_there)
                for player in plays_there:
                    valid_player = False
                    for each_present in players_present:
                        if player.name in each_present:
                            valid_player = True
                    if player.name in positions:
                        valid_player = False
                    if not valid_player:
                        plays_there.remove(player)
                logging.info(plays_there)
                if len(plays_there) == 0:
                    positions.append("OOPS")
                elif len(plays_there) == 1:
                    positions.append(plays_there[0].name)
                else:
                    choose_player = random.choice(plays_there)
                    positions.append(choose_player.name)

            elif len(preferred_players) == 1:
                positions.append(preferred_players[0])
                logging.info('1111111111')
            else:
                choose_player = random.choice(preferred_players)
                positions.append(choose_player)
        lineup.append(positions)

        minute = team.half_duration
        positions = [minute]
        goalie = second_goalie
        positions.append(goalie)
        for player in players_present:
            player_name = player[0]
            player_object = Player.objects.get(name=player_name)
            if player_object.name != goalie:
                positions.append(player_name)
        lineup.append(positions)

    logging.info(lineup)
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
    positions = ast.literal_eval(lineup.positions)
    # If the lineup is not in the lineups that are available to you???
    if lineup not in lineups:
        raise Http404
    return render(request, 'lineups/view_lineup.html', {'lineup': lineup, 'positions': positions})


@login_required
@csrf_protect
def new_lineup(request):
    team = Team.objects.get(owner=request.user)
    players = Player.objects.filter(team_name=team.team_name)
    players_present = []
    lineups = []
    my_team_name = team.team_name

    if request.method == 'POST':
        possible_goalies = []
        goalies = Player.objects.filter(team_name=team.team_name).filter(is_goalie=True)
        for player in goalies:
            possible_goalies = possible_goalies + [(player.name, player.name)]
        form = NewLineupForm(request.POST, choices=possible_goalies)

        if form.is_valid():
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
                                                player.is_attacking_mid, player.is_left_striker,
                                                player.is_right_striker])
                num_minutes = 2 * int(team.half_duration)
                num_players = len(players_present)
                on_sideline = num_players - int(team.team_size)
                num_outfield = int(team.team_size) - 1
                subs_determined = False

                if on_sideline <= 0:
                    slots_to_fill = 0
                    lineups = get_lineup(request, slots_to_fill, players_present, instance.first_goalie, instance.second_goalie)
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
                instance.positions = lineups
                instance.save()

            else:
                messages.error(request, 'Lineup already exists.')
                return render(request, 'lineups/list.html')

        view_lineup_url = lineup_id + '/view_lineup.html'
        return redirect(view_lineup_url)

    else:
        possible_goalies = []
        goalies = Player.objects.filter(team_name=team.team_name).filter(is_goalie=True)
        for player in goalies:
            possible_goalies = possible_goalies + [(player.name, player.name)]
        logging.info(possible_goalies)
        form = NewLineupForm(choices=possible_goalies)

    return render(request, 'lineups/new_lineup.html', {'form': form, 'team': team, 'players': players})
