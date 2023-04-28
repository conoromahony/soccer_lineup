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
# A future optimization will be to provide more flexibility with goalie substitutions.
NUM_GOALIES = 2
# When we support other team sizes and team formations, this will need to evolve into a "library" of player
# positions for each combination.
PLAYER_POSITIONS = ["left_full", "center_back", "sweeper", "right_full", "left_mid", "stopper", "attacking_mid",
                    "right_mid", "left_striker", "right_striker"]


def get_plays_there(request, players_present, positions, position_to_fill, players):
    # This is not a "view" function. It is a supporting helper function. Call this function when you want to find a
    # player who plays in a particular position of the field (but it is not their preferred position). If there are
    # no players left who play in the position, this function chooses the first available remaining player (even if
    # they don't play in the position.
    boolean_check = "is_" + position_to_fill
    logging.info("boolean_check: " + boolean_check)
    plays_there = [player for player in players if getattr(player, boolean_check)]

    plays_there_and_present = []
    for each_player in plays_there:
        valid_player = False
        for each_present in players_present:
            if each_player.name in each_present:
                valid_player = True
        if each_player.name in positions:
            valid_player = False
        if valid_player:
            plays_there_and_present.append(each_player)

    logging.info(plays_there_and_present)
    if len(plays_there_and_present) == 0:
        for each_present in players_present:
            if each_present[0] not in positions:
                return each_present[0]
                break
    elif len(plays_there_and_present) == 1:
        return plays_there_and_present[0].name
    else:
        return random.choice(plays_there_and_present).name


def get_player(request, players_present, positions, position_to_fill, players):
    # This is not a "view" function. It is a supporting helper function. Call this function to return the players for
    # whom the requested position is their preferred position. If there are no players for whom the requested position
    # is their preferred position, call a function to get a player who plays in that position.
    preferred_players = []
    for player in players_present:
        player_object = Player.objects.get(name=player[0])
        if (player_object.preferred_position == position_to_fill) and (player_object.name not in positions):
            preferred_players.append(player_object.name)
    logging.info(preferred_players)

    if len(preferred_players) == 0:
        get_someone = get_plays_there(request, players_present, positions, position_to_fill, players)
        return get_someone
    elif len(preferred_players) == 1:
        logging.info('1111111111')
        return preferred_players[0]
    else:
        return random.choice(preferred_players)


def get_team(request, players_present, players, positions):
    # This is not a "view" function. It is a supporting function. Call this function to get a single lineup (for a
    # portion of a game). This function iterates through each outfield position, and calls other functions to assign
    # a player for that position.
    for position_to_fill in PLAYER_POSITIONS:
        logging.info(position_to_fill)
        positions.append(get_player(request, players_present, positions, position_to_fill, players))
    return positions


def get_lineups(request, slots_to_fill, players_present, first_goalie, second_goalie):
    # This is not a "view" function. It is a supporting function. Call this function to get all lineups for a game.
    # At each substitution point in the game, this function calls the get_team function to get the team for that time.
    logging.info(players_present)
    team = Team.objects.get(owner=request.user)
    players = Player.objects.filter(team_name=team.team_name)
    lineup = []
    if slots_to_fill == 0:
        minute = 0
        positions = [minute]
        goalie = first_goalie
        positions.append(goalie)
        lineup.append(get_team(request, players_present, players, positions))

        minute = team.half_duration
        positions = [minute]
        goalie = second_goalie
        positions.append(goalie)
        lineup.append(get_team(request, players_present, players, positions))

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
                    lineups = get_lineups(request, slots_to_fill, players_present, instance.first_goalie, instance.second_goalie)
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
