import logging
import ast
import random

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from math import floor

from .models import Lineup
from team.models import Team, Player
from .forms import NewLineupForm

# When we have sufficient substitutes, we will not have less than this many substitution cycles (to ensure players
# are not continuously playing for too long).
MIN_SUB_CYCLES = 4
# When we have sufficient substitutes, we will try to not have more than this many substitution cycles (to ensure
# players are on the field long enough to get involved in the game).
# TODO: Do we really want this many substitutes? It would mean playing less than 8 minutes a cycle.
MAX_SUB_CYCLES = 9
# The number slots in a game for goalies. There will be one goalie slot for the first half, and another goalie slot
# for the second half. The same player can play in both goalie slots. A future optimization is to provide more
# flexibility with goalie substitutions.
NUM_GOALIES = 2
# The positions on the field. When we support other team sizes and team formations, this will need to evolve into
# a "library" of player positions for each combination of team size and team formation.
PLAYER_POSITIONS = ["left_full", "center_back", "sweeper", "right_full", "left_mid", "stopper", "attacking_mid",
                    "right_mid", "left_striker", "right_striker"]


def get_plays_there(request, players_present, positions, position_to_fill, players, playing_time):
    # This is not a "view" function. It is a supporting helper function. Call this function when you want to find a
    # player who plays in a particular position of the field (but it is not their preferred position). This function
    # is called when there is no player present whose preferred position is the position in question. This function
    # goes through all players for whom this position is checked as one in which they will play. If there are no such
    # players, this function chooses the first available remaining player (even if they don't play in the position).
    boolean_check = "is_" + position_to_fill
    # Remember that the column in the Player database table that tracks if someone plays the position is named "is_"
    # followed by the position name.
    plays_there = [player for player in players if getattr(player, boolean_check)]

    plays_there_and_present = []
    for each_player in plays_there:
        valid_player = False
        for each_present in players_present:
            if each_player.name in each_present:
                valid_player = True

        # Check to make sure the player is not already assigned to a position in the current lineup.
        if each_player.name in positions:
            valid_player = False

        # Check to make sure the player has not exceeded their number of playing slots.
        for player_time_check in playing_time:
            if player_time_check["name"] == each_player.name:
                if player_time_check["playing_slots"] >= player_time_check["total_playing_slots"]:
                    valid_player = False

        if valid_player:
            plays_there_and_present.append(each_player)

    if len(plays_there_and_present) == 0:
        # If there are no players who play in that position and are present, then go get another player.
        # TODO: This is quite a crude algorithm, which essentially takes the first player who hasn't used up all of
        #  their playing slots. This can be improved.
        for each_present in playing_time:
            if (each_present["name"] not in positions) and \
                    (each_present["playing_slots"] < each_present["total_playing_slots"]):
                logging.info("5555 position: %s, player: %s", position_to_fill, each_present["name"])
                return each_present["name"]
                break
    elif len(plays_there_and_present) == 1:
        logging.info("6666 position: %s, player: %s", position_to_fill, plays_there_and_present[0].name)
        return plays_there_and_present[0].name
    else:
        player_chosen = random.choice(plays_there_and_present).name
        logging.info("7777 position: %s, player: %s", position_to_fill, player_chosen)
        return player_chosen


def get_player(request, players_present, positions, position_to_fill, players, playing_time):
    # This is not a "view" function. It is a supporting helper function. Call this function to return the players for
    # whom the requested position is their preferred position. If there are no players for whom the requested position
    # is their preferred position, call a function to get a player who plays in that position.
    # TODO: Update the algorithm to minimize the number of positional switches each time there's a substitution.
    preferred_players = []
    for player in players_present:
        player_object = Player.objects.get(name=player[0])
        if (player_object.preferred_position == position_to_fill) and (player_object.name not in positions):
            for player_time_check in playing_time:
                if player_time_check["name"] == player_object.name:
                    if player_time_check["playing_slots"] < player_time_check["total_playing_slots"]:
                        preferred_players.append(player_object.name)

    if len(preferred_players) == 0:
        get_someone = get_plays_there(request, players_present, positions, position_to_fill, players, playing_time)
        return get_someone
    elif len(preferred_players) == 1:
        logging.info("0000 position: %s, player: %s", position_to_fill, preferred_players[0])
        return preferred_players[0]
    else:
        player_chosen = random.choice(preferred_players)
        logging.info("1111 position: %s, player: %s", position_to_fill, player_chosen)
        return player_chosen


def get_team(request, players_present, players, positions, playing_time):
    # This is not a "view" function. It is a supporting function. Call this function to get a single lineup (for a
    # portion of a game). This function iterates through each outfield position, and calls other functions to assign
    # a player for that position.
    for position_to_fill in PLAYER_POSITIONS:
        positions.append(get_player(request, players_present, positions, position_to_fill, players, playing_time))
    return positions


def get_lineups(request, num_outfield, on_sideline, num_minutes, players_present, first_goalie, second_goalie):
    # This is not a "view" function. It is a supporting function. Call this function to get all lineups for a game.
    # At each substitution point in the game, this function calls the get_team function to get the team for that time.
    team = Team.objects.get(owner=request.user)
    players = Player.objects.filter(team_name=team.team_name)
    lineup = []

    # Create a list to keep track of each player's playing time. Each item in the list is a dictionary that keeps
    # track of information for a single player.
    # TODO: Incorporate more information into playing_time, so we don't have to pass so many arguments to functions.
    playing_time = []

    # If we have no subs, we will have one lineup for the first half (with the first half goalie in goal), and
    # another lineup for the second half (with the second half goalie in goal).
    if on_sideline == 0:
        num_lineups = 2
        num_playing_slots = num_lineups
        num_sub_slots = 0

    # If we have one sub, each player will sit out for one slot during the game. It will likely make for more
    # frequent substitutions that you would normally make.
    elif on_sideline == 1:
        num_lineups = num_outfield
        num_playing_slots = num_lineups - 1
        num_sub_slots = 1

    # If we have two or more subs...
    else:
        found_answer = False
        for sub_rounds in range(MIN_SUB_CYCLES, MAX_SUB_CYCLES):
            # If we have sub_rounds rounds of substitutes, this is the total number of playing slots that a substitute
            # has filled (across all rounds of substitution).
            total_sub_slots = (sub_rounds + 1) * on_sideline
            # This is the total number of players that are to be considered for substitution (i.e. it doesn't include
            # the goalie)
            total_players = num_outfield + on_sideline
            # If sub_slots MOD the players available for substitution is zero, then each player available for
            # substitution ends up with the same number of substitution slots.
            if (total_sub_slots % total_players) == 0:
                found_answer = True
                # The total number of lineups we need is equal to the number of substitution rounds plus one (for the
                # starting lineup.
                num_lineups = sub_rounds + 1
                num_sub_slots = int(total_sub_slots / total_players)
                num_playing_slots = num_lineups - num_sub_slots
                break
            # TODO: When there's no "mod zero" answer, we just choose last value. We should choose a more elegant
            #  solution. Perhaps choose the "lowest" modulo value answer? This happens for: 14 players, 18 players.
            if found_answer == False:
                num_lineups = 8
                num_sub_slots = int((8 * on_sideline) / total_players)
                num_playing_slots = num_lineups - num_sub_slots

    # Populate the data structure that keeps track of each player's playing time. Cater for the fact that goalies are
    # treated differently when it comes to substitutions.  Each item in the list is a dictionary that keeps track of
    # information for a single player. The dictionary has three elements: the player name (name), the number of playing
    # slots they have currently used up (slots), and the total number of playing slots they should fill in the game
    # (total_slots).
    for player in players_present:
        # TODO: This formula seems to work for the different combination of subs for 11 players (see the spreadsheet I
        #  created. However, I need to test this more rigorously.
        goalie_slots = floor((num_lineups / 2) + (num_playing_slots / 2))
        goalie_sub_slots = num_lineups - goalie_slots
        if (player[0] == first_goalie) or (player[0] == second_goalie):
            individual_player = dict(name=player[0], total_playing_slots=goalie_slots, playing_slots=0,
                                     total_sub_slots=goalie_sub_slots, sub_slots=0)
        else:
            individual_player = dict(name=player[0], total_playing_slots=num_playing_slots, playing_slots=0,
                                     total_sub_slots=num_sub_slots, sub_slots=0)
        playing_time.append(individual_player)

    # If there are no substitutes, generate the lineup for each half.
    if on_sideline == 0:
        # This is the lineup for the first half.
        minute = 0
        positions = [minute]
        goalie = first_goalie
        positions.append(goalie)
        lineup.append(get_team(request, players_present, players, positions, playing_time))

        # This is the lineup for the second half.
        minute = team.half_duration
        positions = [minute]
        goalie = second_goalie
        positions.append(goalie)
        lineup.append(get_team(request, players_present, players, positions, playing_time))

    # If we have one or more subs...
    else:
        for i in range(num_lineups):
            minute = int(i * (num_minutes / num_lineups))
            positions = [minute]
            if minute < int(num_minutes / 2):
                goalie = first_goalie
            else:
                goalie = second_goalie
            positions.append(goalie)
            positions = get_team(request, players_present, players, positions, playing_time)
            logging.info(positions)

            for each_player in playing_time:
                if each_player["name"] in positions:
                    each_player["playing_slots"] += 1
                else:
                    each_player["sub_slots"] += 1
            logging.info(playing_time)
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
        # Dynamically determine the players on this team who play in goal, and use that information to populate the
        # drop-down lists for choosing goalies in a game.
        possible_goalies = []
        goalies = Player.objects.filter(team_name=team.team_name).filter(is_goalie=True)
        for player in goalies:
            possible_goalies = possible_goalies + [(player.name, player.name)]
        form = NewLineupForm(request.POST, choices=possible_goalies)

        if form.is_valid():
            # Create a unique identifier for this game to ensure we don't create multiple lineup strategies for the
            # same game.
            lineup_id = form.cleaned_data['opponent'] + str(form.cleaned_data['game_date'])

            if not Lineup.objects.filter(game_id=lineup_id).exists():
                instance = form.save(commit=False)
                instance.game_id = lineup_id
                instance.team_name = my_team_name
                instance.owner = request.user

                # Determine which players were indicated as being prest for this game (via the checkboxes on the form)
                # and put them in a list called players_present.
                for player in players:
                    if request.POST.get(player.name):
                        players_present.append([player.name, player.is_goalie, player.is_left_full,
                                                player.is_right_full, player.is_center_back, player.is_sweeper,
                                                player.is_stopper, player.is_left_mid, player.is_right_mid,
                                                player.is_attacking_mid, player.is_left_striker,
                                                player.is_right_striker])
                num_minutes = 2 * int(team.half_duration)
                num_players = len(players_present)
                instance.num_players = num_players
                on_sideline = num_players - int(team.team_size)
                num_outfield = int(team.team_size) - 1
                subs_determined = False

                # If there are no substitutes available for this game, generate the lineups for each half.
                if on_sideline <= 0:
                    lineups = get_lineups(request, num_outfield, on_sideline, num_minutes, players_present,
                                          instance.first_goalie, instance.second_goalie)
                    subs_determined = True

                # If there is one substitute available for this game, generate the lineups.
                elif on_sideline == 1:
                    lineups = get_lineups(request, num_outfield, on_sideline, num_minutes, players_present,
                                          instance.first_goalie, instance.second_goalie)
                    subs_determined = True

                else:
                    lineups = get_lineups(request, num_outfield, on_sideline, num_minutes, players_present,
                                          instance.first_goalie, instance.second_goalie)
                    subs_determined = True

                logging.info("Mins:%s Players:%s Outfield:%s Subs:%s", num_minutes, num_players, num_outfield, on_sideline)
                instance.number_subs = 0
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
