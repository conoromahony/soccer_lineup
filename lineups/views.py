import logging
import ast
import random

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
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
# The positions on the field.
# TODO: When we support other team sizes and team formations, this will need to evolve into a "library" of player
#  positions for each combination of team size and team formation.
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
                logging.info("RANDOM position: %s, player: %s", position_to_fill, each_present["name"])
                return each_present["name"]
    elif len(plays_there_and_present) == 1:
        logging.info("PLAYS_THERE position: %s, player: %s", position_to_fill, plays_there_and_present[0].name)
        return plays_there_and_present[0].name
    else:
        player_chosen = random.choice(plays_there_and_present).name
        logging.info("PLAYS_THERE position: %s, player: %s", position_to_fill, player_chosen)
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
        logging.info("PREFERRED position: %s, player: %s", position_to_fill, preferred_players[0])
        return preferred_players[0]
    else:
        player_chosen = random.choice(preferred_players)
        logging.info("PREFERRED position: %s, player: %s", position_to_fill, player_chosen)
        return player_chosen


def find_player_to_sub(last_lineup, playing_time):
    # This is not a "view" function. It is a supporting function. Call this function to randomly choose a player to
    # substitute from the current lineup. Choose a number between 2 and 11, as the index of the player to substitute.
    # Ignore index 0, which is the "minute of the lineup" and ignore index 1, which is the goalkeeper.
    position_to_sub = 2
    found_sub = False
    while not found_sub:
        position_to_sub = random.randrange(2, 11)
        logging.info("SUBSTITUTE: %s", position_to_sub)
        player_to_sub = last_lineup[position_to_sub]
        logging.info("SUBSTITUTE: %s", player_to_sub)
        for player_time_check in playing_time:
            if player_time_check["name"] == player_to_sub:
                if player_time_check["sub_slots"] < player_time_check["total_sub_slots"]:
                    found_sub = True
    return position_to_sub


def get_possible_subs(players_present, existing_lineup):
    # This is not a "view" function. It is a supporting function. Call this function to identify the players present
    # who are not currently in the lineup. That is, use this function to identify possible players to substitute in.
    subs_list = []
    logging.info("GET SUBS LINEUP: %s", existing_lineup)
    currently_playing = existing_lineup[1:]
    for player in players_present:
        if player[0] not in currently_playing:
            subs_list.append(player[0])
    logging.info("POTENTIAL SUBS: %s", subs_list)
    return subs_list


def sort_lineup(e):
    # This is not a "view" function. It is a function that specifies how to sort the lineups, so we can get the most
    # recently-generated lineup (into the first position, and easily access that most recent lineup).
    return e[0]


def get_team(request, players_present, players, positions, playing_time, lineup, num_minutes):
    # This is not a "view" function. It is a supporting function. Call this function to get a single lineup (for a
    # portion of a game). For the first lineup, iterate through each outfield position, and call other functions to
    # assign a player to that position. For subsequent lineups, choose players to substitute out from that team.
    # This approach ensures minimal switching of positions for players over the course of a game.
    if positions[0] == 0:
        for position_to_fill in PLAYER_POSITIONS:
            positions.append(get_player(request, players_present, positions, position_to_fill, players, playing_time))

    else:
        # Choose random players to substitute out.
        # Need to know previous lineup.
        logging.info("ALL LINEUPS: %s", lineup)
        lineup.sort(key=sort_lineup, reverse=True)
        last_lineup = list(lineup[0])
        logging.info("LAST LINEUP: %s", last_lineup)

        this_lineup = last_lineup[2:]

        # If we get to the second half, make sure to change out the goalies before we determine the available subs.
        if positions[0] >= int(num_minutes / 2):
            old_goalie = last_lineup[1]
            new_goalie = positions[1]
            if new_goalie in last_lineup:
                new_goalie_index = last_lineup.index(new_goalie)
                last_lineup[new_goalie_index] = old_goalie
            last_lineup[1] = new_goalie

        possible_subs = get_possible_subs(players_present, last_lineup)

        for each_player in possible_subs:
            logging.info("PLAYER IN: %s", each_player)
            player_object = Player.objects.get(name=each_player)
            bring_player_in = False

            # Make sure the substitute coming in has not fulfilled all of their playing slots.
            for player_time_check in playing_time:
                if player_time_check["name"] == player_object.name:
                    if player_time_check["playing_slots"] < player_time_check["total_playing_slots"]:
                        bring_player_in = True
            logging.info("%s PLAYING SLOTS: %s of %s", player_object.name, player_time_check["playing_slots"], player_time_check["total_playing_slots"])

            if bring_player_in:
                # First, let's try to sub them into their preferred position.
                sub_found = False
                position_to_try = player_object.preferred_position
                index_to_try = PLAYER_POSITIONS.index(position_to_try) + 2
                player_to_try = last_lineup[index_to_try]
                logging.info("POSITION TO TRY: %s", position_to_try)
                logging.info("PLAYER TO TRY: %s", player_to_try)
                player_object_to_try = Player.objects.get(name=player_to_try)

                for player_time_check in playing_time:
                    if player_time_check["name"] == player_object_to_try.name:
                        if player_time_check["sub_slots"] < player_time_check["total_sub_slots"]:
                            sub_found = True
                            player_out = player_to_try
                            player_time_check["sub_slots"] += 1
                            this_lineup[index_to_try - 2] = each_player
                            logging.info("PLAYER OUT: %s", player_out)

                # If the player in their preferred position has reached their maximum number of substitutions,
                # let's try the other positions they play.
                if not sub_found:
                    # Determine the positions the player coming in can play.
                    player_positions = []
                    for check_position in PLAYER_POSITIONS:
                        boolean_check = "is_" + check_position
                        if getattr(player_object, boolean_check):
                            player_positions.append(check_position)
                    logging.info("POSSIBLE POSITIONS: %s", player_positions)

                    for check_position in player_positions:
                        index_to_try = PLAYER_POSITIONS.index(check_position) + 2
                        player_to_try = last_lineup[index_to_try]
                        logging.info("POSITION TO TRY: %s", check_position)
                        logging.info("PLAYER TO TRY: %s", player_to_try)
                        player_object_to_try = Player.objects.get(name=player_to_try)

                        for player_time_check in playing_time:
                            if player_time_check["name"] == player_object_to_try.name:
                                if player_time_check["sub_slots"] < player_time_check["total_sub_slots"]:
                                    sub_found = True
                                    player_out = player_to_try
                                    player_time_check["sub_slots"] += 1
                                    this_lineup[index_to_try - 2] = each_player
                                    logging.info("PLAYER OUT: %s, PLAYER IN: %s", player_out, each_player)
                                    break
                        else:
                            continue
                        break

                # If we have tried their preferred position and the positions they play, and we still haven't found
                # someone to substitute try players at random. But make sure we don't try to substitute the goalie (with
                # the last_lineup[1] check.)
                if not sub_found:
                    for player_time_check in playing_time:
                        if player_time_check["sub_slots"] < player_time_check["total_sub_slots"] and \
                                player_time_check["name"] != last_lineup[1]:
                            sub_found = True
                            player_out = player_time_check["name"]
                            player_time_check["sub_slots"] += 1
                            index_to_switch = this_lineup.index(player_out)
                            this_lineup[index_to_switch] = each_player
                            logging.info("PLAYER IN: %s, PLAYER OUT: %s", each_player, player_out)
                            break

        logging.info("NEW LINEUP: %s", this_lineup)
        for new_player_position in this_lineup:
            positions.append(new_player_position)

    # STATUS:
    # =======
    # The playing_slots and sub_slots appears to be working for 13 players.
    # However, it does not appear to be working for 14 players. It looks like the setting for number of sub_slots is
    # wrong because all players get 1 sub_slot, but they need to be substituted more than once.
    # We need to test playing_slots and sub_slots for other team sizes.
    # We are replacing the goalie in the substitutes immediately before halftime. It looks like we are "losing" the
    # minute count, and adopting the minute count from the previous lineup.
    # We may need to cater for situations where the substitutions don't happen at halftime, and the goalies need to
    # be switched.
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
        lineup.append(get_team(request, players_present, players, positions, playing_time, lineup, num_minutes))

        # This is the lineup for the second half.
        minute = team.half_duration
        positions = [minute]
        goalie = second_goalie
        positions.append(goalie)
        lineup.append(get_team(request, players_present, players, positions, playing_time, lineup, num_minutes))

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
            positions = get_team(request, players_present, players, positions, playing_time, lineup, num_minutes)
            logging.info("GOT TEAM: %s", positions)

            for each_player in playing_time:
                if each_player["name"] in positions:
                    each_player["playing_slots"] += 1
                else:
                    if i == 0:
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
    positions.sort(key=sort_lineup)
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

