# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .poker_logic.game import PokerGame
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from django.views.decorators.http import require_GET
from datetime import datetime
from django.utils.timezone import now as timezone_now
import json


# Create your views here.


def get_users_in_room():
    active_sessions = Session.objects.filter(expire_date__gte=now()) # gets all the active sessions in /room
    user_ids = []

    for session in active_sessions:
        data = session.get_decoded()
        if data.get("_auth_user_id") and data.get("in_room") == True:
            user_ids.append(data["_auth_user_id"])

    return User.objects.filter(id__in=user_ids)

def get_ui_log(request):
    return JsonResponse({"log": game.ui_log})

def home_view(request):
    return render(request, "pages/home.html", {})

game = None

def room_view(request):
    global game

    request.session['in_room'] = True
    username = request.user.username

    # Get all users currently in the room based on sessions
    active_users = get_users_in_room()
    active_usernames = [user.username for user in active_users]


    if game:
        # Sync game.players with all currently active usernames
        active_users = get_users_in_room()
        active_usernames = [u.username for u in active_users]
        game.players = [p for p in game.players if p in active_usernames]
        for old in list(game.seat_assignments.keys()):
           if old not in game.players:
               game.seat_assignments.pop(old)

    if game is None:
        # First-ever player: start the game and seat them in spot 1
        game = PokerGame([username])
        game.seat_assignments[username] = 1
        game.next_seat_number = 2
    else:
        if username not in game.players:
            game.players.append(username)

            # Force viewer to seat 1 if open, otherwise assign next available
            if 1 not in game.seat_assignments.values():
                game.seat_assignments[username] = 1
            else:
                game.assign_seat(username)

            if username not in game.player_coins:
                game.player_coins[username] = 1000000

        if username not in game.player_hands:
            game.deal_hands([username])

        if len(game.players) >= 2 and not game.hand_started:
            game.start_new_hand()

    # Validate player is in the game
    if username not in game.players:
        return render(request, 'pages/room.html', {"error_message": "You're not seated."})

    # Prepare context
    player_hand       = game.player_hands.get(username, [])
    community_cards   = game.community_cards
    seat_map          = build_seat_map(request)
    all_seated        = list(seat_map.values())
    coin_map          = { p: game.player_coins.get(p, 0) for p in all_seated }
    coin_map[username] = game.player_coins.get(username, 0)

    current_turn_player = None
    if getattr(game, 'waiting_for_action', False) and getattr(game, 'betting_order', []):
        current_turn_player = game.betting_order[game.current_player_index]

    return render(request, 'pages/room.html', {
        "player_hand":       player_hand,
        "community_cards":   community_cards,
        "log":               game.ui_log if hasattr(game, "ui_log") else [],
        "seat_map":          seat_map,
        "coin_map":          coin_map,
        "current_turn_player": current_turn_player
    })

def build_seat_map(request):
    """
    Returns a dict mapping *display* seats ("1"–"9") to usernames,
    rotated so that the current user is always on display seat "1".
    """
    total_seats = 9
    viewer = request.user.username
    abs_map = game.seat_assignments          # e.g. {'alice': 3, 'bob': 7, ...}

    # 1) Figure out which absolute seat the viewer has
    viewer_abs = abs_map.get(viewer, None)
    if viewer_abs is None:
        return {}  # viewer not seated yet

    display_map = {}
    for player, abs_seat in abs_map.items():
        # compute relative seat:
        #   shift so that abs_seat == viewer_abs becomes 1,
        #   the next clockwise seat abs_seat==viewer_abs+1 → 2, etc.
        rel = ((abs_seat - viewer_abs) % total_seats) + 1
        display_map[str(rel)] = player
    return display_map

@csrf_exempt
def submit_action(request):
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action")
        username = request.user.username

        result = game.apply_player_action(username, action)

        return JsonResponse(result)  # This returns the message dictionary

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def logout_view(request):
    logout(request)
    request.session['in_room'] = False
    return redirect("home")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")  # or "home"
    return render(request, "pages/login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("home")
    return render(request, "pages/register.html")



@require_GET
def get_seat_map(request):
    global game
    if not game:
        return JsonResponse({"seat_map": {}, "coin_map": {}})

    # ✅ Run cleanup to remove any disconnected or inactive players
    game.remove_inactive_players()

    # ✅ Make sure the current player is marked as active
    username = request.user.username
    game.mark_active(username)

    # ✅ Build updated seat map and coin map based on truly active players
    seat_map = build_seat_map(request)
    all_seated_players = list(seat_map.values())
    coin_map = {p: game.player_coins.get(p, 0) for p in all_seated_players}

    return JsonResponse({"seat_map": seat_map, "coin_map": coin_map})


@csrf_exempt
def leave_room(request):
    username = request.user.username
    request.session['in_room'] = False
    # return JsonResponse({"status": "ok"})

    global game
    if game:
        if username in game.players:
            game.players.remove(username)

           # *also* remove their seat assignment
            game.seat_assignments.pop(username, None)
            game.folded_players.add(username) 
        if username in game.player_hands:
            del game.player_hands[username]
        if username in game.player_coins:
            del game.player_coins[username]
        if username in game.current_round_bets:
            del game.current_round_bets[username]
        if username in game.last_active:
            del game.last_active[username]

    return JsonResponse({"status": "ok"})

@require_GET
def get_turn_status(request):
    global game
    if not game or not getattr(game, 'waiting_for_action', False):
        return JsonResponse({"current_turn_player": None})
    return JsonResponse({
        "current_turn_player": game.betting_order[game.current_player_index]
    })

@require_GET
def get_game_state(request):
    """Return exactly what the front-end needs to update hands & community cards."""
    username = request.user.username
    return JsonResponse({
        "player_hand": game.player_hands.get(username, []),
        "community_cards": game.community_cards,
        "current_turn_player": getattr(game, 'betting_order', [None])[game.current_player_index]
                                   if getattr(game, 'waiting_for_action', False) else None,
    })

