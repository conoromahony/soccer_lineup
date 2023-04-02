from django.shortcuts import render, get_object_or_404
from .models import Player

# Create your views here.
def player_list(request):
    # This view displays the roster of players.
    # The player_list view takes the request object as the only parameter.
    # We retrieve the list of players using the "all_players" manager defined in models.py.
    players = Player.all_players.all()
    # Call the "render" function, passing the original request object, the template used to build the page,
    # and the data needed to build the page.
    return render(request, 'team/player/list.html', {'players': players})

def player_detail(request, name):
    player = get_object_or_404(Player, name=name)
    return render(request, 'team/player/detail.html', {'player': player})

