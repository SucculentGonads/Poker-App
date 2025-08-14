import time
import random

# Setup
game_on = "yes"
games_played = 0
dealer_position = 0

while game_on == "yes":  
    while True:
        try:
            player_count = int(input("How many players? "))
            if 2 <= player_count <= 9:
                break
            else:
                print("Players range is 2 - 9 chuttey.")
        except ValueError:
            print("Bro type a number between 2 and 9.")
    pot = 0

    # Setup the deck
    Deck = [
        "Ace Spades", "King Spades", "Queen Spades", "Jack Spades", "10 Spades", "9 Spades", "8 Spades", "7 Spades", "6 Spades", "5 Spades", "4 Spades", "3 Spades", "2 Spades",
        "Ace Hearts", "King Hearts", "Queen Hearts", "Jack Hearts", "10 Hearts", "9 Hearts", "8 Hearts", "7 Hearts", "6 Hearts", "5 Hearts", "4 Hearts", "3 Hearts", "2 Hearts",
        "Ace Diamonds", "King Diamonds", "Queen Diamonds", "Jack Diamonds", "10 Diamonds", "9 Diamonds", "8 Diamonds", "7 Diamonds", "6 Diamonds", "5 Diamonds", "4 Diamonds", 
        "3 Diamonds", "2 Diamonds", "Ace Clubs", "King Clubs", "Queen Clubs", "Jack Clubs", "10 Clubs", "9 Clubs", "8 Clubs", "7 Clubs", "6 Clubs", "5 Clubs", "4 Clubs", "3 Clubs", "2 Clubs"
    ]
    random.shuffle(Deck)

    dealt_card = 0
    players = list(range(1, player_count + 1))
    dealer_position = (dealer_position + 1) % player_count
    small_blind = (dealer_position + 1) % player_count
    big_blind = (dealer_position + 2) % player_count

    small_blind_pot = 500
    big_blind_pot = 1000

    print(f"\n🔄 Round {games_played + 1} - Dealer: Player {players[dealer_position]} 🔄\n")

    player_hands = {}
    player_pairs = {}
    player_coins = {}
    current_round_bets = {}

    # Deal cards
    for i in range(player_count):  
        player = f"Player {players[i]}"
        player_hands[player] = [Deck[dealt_card], Deck[dealt_card + 1]]
        player_coins[player] = 100000
        current_round_bets[player] = 0

        print(f"{player}", end=": ")

        if i == small_blind:
            print(f"|| Small Blind Bet: {small_blind_pot} ", end="|| ")
            player_coins[player] -= small_blind_pot
            current_round_bets[player] = small_blind_pot
        elif i == big_blind:
            print(f"|| Big Blind Bet: {big_blind_pot} ", end="|| ")
            player_coins[player] -= big_blind_pot
            current_round_bets[player] = big_blind_pot

        print(f"{Deck[dealt_card]}, {Deck[dealt_card + 1]}", end=" ")
        print(player_coins[player])

        if Deck[dealt_card].split()[0] == Deck[dealt_card + 1].split()[0]: 
            print("Hand: Pair\n")
            player_pairs[player] = 1
        else:
            player_pairs[player] = 0

        dealt_card += 2

    print("\n🃏 Players' Hands:")
    for player, hand in player_hands.items():
        print(f"{player}: {hand}")

    def betting_round(stage_name, call_amount, pot):
        print(f"\n🪙 {stage_name} Betting Round")
        last_raiser = None
        acted_players = set()
        global all_in_players

        for player in player_hands:
            current_round_bets[player] = 0

        while True:
            for offset in range(len(players)):
                if len(player_hands) <= 1:
                    return call_amount, pot

                player_index = (big_blind + 1 + offset) % len(players)
                player_num = players[player_index]
                player = f"Player {player_num}"

                if player not in player_hands:
                    continue

                if last_raiser and player == last_raiser and player in acted_players:
                    continue

                while True:
                    print(f"{player}, Coins: {player_coins[player]}, Current bet: {current_round_bets[player]}")
                    print(f"\nCurrent call amount: {call_amount}")
                    action = input("fold, check, call, raise, or all in? ").lower()

                    if action not in ["check", "call", "raise", "fold", "all in"]:
                        print("Invalid input.")
                        continue

                    if action == "check":
                        if current_round_bets[player] < call_amount:
                            print("You can't check. There's a bet to call.")
                            continue
                        print(f"{player}: {player_coins[player]} coins\n")
                        break

                    elif action == "call":
                        to_call = call_amount - current_round_bets[player]
                        if player_coins[player] <= to_call:
                            print(f"{player} doesn't have enough to call {call_amount}. Going all-in!")
                            all_in_amount = player_coins[player]
                            player_coins[player] = 0
                            current_round_bets[player] += all_in_amount
                            pot += all_in_amount
                            all_in_players[player] = current_round_bets[player]
                            break
                        else:
                            player_coins[player] -= to_call
                            current_round_bets[player] += to_call
                            pot += to_call
                            break

                    elif action == "raise":
                        raise_amt = int(input("How much do you want to raise? "))
                        new_call_amount = call_amount + raise_amt
                        to_call = new_call_amount - current_round_bets[player]

                        if raise_amt <= 0:
                            print("Raise must be a positive number.")
                            continue

                        if player_coins[player] < to_call:
                            print(f"{player} doesn't have enough coins to raise {raise_amt}.")
                            continue  # Ask again
                        else:
                            call_amount = new_call_amount
                            player_coins[player] -= to_call
                            current_round_bets[player] += to_call
                            pot += to_call
                            last_raiser = player
                            acted_players.clear()
                            print(f"{player}: {player_coins[player]} coins\n")
                            break


                    elif action == "all in":
                        if player_coins[player] <= 0:
                            print(f"{player} has no coins to go all-in.")
                            continue
                        all_in_amount = player_coins[player]
                        player_coins[player] = 0
                        current_round_bets[player] += all_in_amount
                        pot += all_in_amount
                        all_in_players[player] = current_round_bets[player]
                        print(f"{player} goes ALL-IN with {all_in_amount}!")
                        break

                    elif action == "fold":
                        print(f"{player} folded.")
                        player_hands.pop(player)
                        player_coins.pop(player)
                        current_round_bets.pop(player)
                        players.remove(player_num)
                        break

                acted_players.add(player)

            all_called = all(current_round_bets[player] == call_amount for player in player_hands)
            if all_called and len(acted_players) == len(player_hands):
                break

        return call_amount, pot


    from collections import Counter
    player_scores = {}
    def check_player_hands(community_cards):
        print("\n🃏 Checking Hands:")
        hand_ranks = {
            "High Card": 1, "One Pair": 2, "Two Pair": 3, "Three of a Kind": 4,
            "Straight": 5, "Flush": 6, "Full House": 7, "Four of a Kind": 8,
            "Straight Flush": 9, "Royal Flush": 10
        }

        for player, hand in player_hands.items():
            card1_rank, card1_suit = hand[0].split()
            card2_rank, card2_suit = hand[1].split()

            rank_values = {
                "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
                "7": 7, "8": 8, "9": 9, "10": 10,
                "Jack": 11, "Queen": 12, "King": 13, "Ace": 14
            }

            all_cards = hand + community_cards
            all_ranks = [card.split()[0] for card in all_cards]
            all_suits = [card.split()[1] for card in all_cards]
            rank_vals = [rank_values[rank] for rank in all_ranks]
            unique_vals = sorted(set(rank_vals))

            hand_rank = 1
            highest_card = max(rank_vals)

            # Straight Flush & Royal Flush
            suit_dict = {}
            for card in all_cards:
                rank, suit = card.split()
                value = rank_values[rank]
                suit_dict.setdefault(suit, []).append(value)

            for suit, vals in suit_dict.items():
                if len(vals) >= 5:
                    sorted_vals = sorted(set(vals))
                    # Add Ace as 1 if it's present for wheel detection
                    if 14 in sorted_vals:
                        sorted_vals.append(1)
                        sorted_vals = sorted(set(sorted_vals))
                    for i in range(len(sorted_vals) - 4):
                        window = sorted_vals[i:i+5]
                        if window == [10, 11, 12, 13, 14]:
                            print(f"{player} has a Royal Flush!")
                            hand_rank = 10
                            highest_card = 14
                            break
                        elif window == [1, 2, 3, 4, 5]:
                            print(f"{player} has a Wheel Straight Flush!")
                            hand_rank = 9
                            highest_card = 5
                            break
                        elif window[-1] - window[0] == 4:
                            print(f"{player} has a Straight Flush: {window[0]} to {window[-1]}")
                            hand_rank = 9
                            highest_card = window[-1]
                            break


            # Four of a Kind
            for rank in set(all_ranks):
                if all_ranks.count(rank) == 4:
                    print(f"{player} has Four of a Kind with {rank}s")
                    hand_rank = 8
                    break

            # Full House
            pairs = [rank for rank in set(all_ranks) if all_ranks.count(rank) == 2]
            three_of_a_kind = [rank for rank in set(all_ranks) if all_ranks.count(rank) == 3]
            if three_of_a_kind and pairs:
                print(f"{player} has a Full House: {three_of_a_kind[0]}s over {pairs[0]}s")
                hand_rank = 7

            # Flush
            suit_counts = Counter(all_suits)
            for suit, count in suit_counts.items():
                if count >= 5:
                    print(f"{player} has a Flush in {suit}")
                    hand_rank = 6
                    break

            # Straight
            if set([14, 2, 3, 4, 5]).issubset(set(rank_vals)):
                print(f"{player} has a Wheel Straight: A to 5")
                hand_rank = 5
                highest_card = 5
            else:
                for i in range(len(unique_vals) - 4):
                    if unique_vals[i + 4] - unique_vals[i] == 4:
                        print(f"{player} has a Straight: {unique_vals[i]} to {unique_vals[i + 4]}")
                        hand_rank = 5
                        highest_card = unique_vals[i + 4]
                        break

            # Two Pair / One Pair
            if hand_rank < 4:
                if len(pairs) == 2:
                    print(f"{player} has Two Pair: {pairs[0]}s and {pairs[1]}s")
                    hand_rank = 3
                elif len(pairs) == 1:
                    print(f"{player} has One Pair: {pairs[0]}s")
                    hand_rank = 2

            # High Card
            if hand_rank == 1:
                print(f"{player} has High Card: {max(rank_vals)}")

            # Save score for tiebreakers if needed later
            player_scores[player] = (hand_rank, highest_card)

    all_in_players = {}
    call_amount, pot = betting_round("Pre-Flop", big_blind_pot, pot)

    print("\n🃏 Flop:")
    time.sleep(1)
    flop_1 = Deck[dealt_card]
    flop_2 = Deck[dealt_card + 1]
    flop_3 = Deck[dealt_card + 2]
    community_cards = [flop_1, flop_2, flop_3]
    print(f"{flop_1}, {flop_2}, {flop_3}")
    dealt_card += 3


    check_player_hands([flop_1, flop_2, flop_3])

    call_amount, pot = betting_round("Post-Flop", 0, pot)

    print("\n🃏 Turn:")
    turn = Deck[dealt_card]
    community_cards.append(turn)
    dealt_card += 1
    print(f"{flop_1}, {flop_2}, {flop_3}, {turn}")

    check_player_hands([flop_1, flop_2, flop_3, turn])

    call_amount, pot = betting_round("Post-Turn", 0, pot)

    print("\n🃏 River")
    river = Deck [dealt_card]
    community_cards.append(river)
    dealt_card += 1
    print(f"{flop_1}, {flop_2}, {flop_3}, {turn}, {river}")

    check_player_hands([flop_1, flop_2, flop_3, turn, river])

    call_amount, pot = betting_round("Post-River", 0, pot)


    def resolve_side_pots(pot, all_in_players, current_round_bets, player_scores, player_coins):
        print("\n💰 Resolving Pots...")

        if all_in_players:
            side_pots = []
            unique_all_in_amounts = sorted(set(all_in_players.values()))
            previous = 0

            for amount in unique_all_in_amounts:
                pot_amount = 0
                eligible_players = []

                for player in current_round_bets:
                    bet = current_round_bets[player]
                    contrib = min(bet, amount - previous)
                    pot_amount += contrib
                    if bet >= amount:
                        eligible_players.append(player)

                side_pots.append((pot_amount, eligible_players))
                previous = amount

            for idx, (side_pot, eligibles) in enumerate(side_pots):
                print(f"\n🪙 Side Pot {idx+1} - {side_pot} coins between: {', '.join(eligibles)}")
                eligible_scores = {p: player_scores[p] for p in eligibles}
                best_rank = max(score[0] for score in eligible_scores.values())
                top_players = [p for p, score in eligible_scores.items() if score[0] == best_rank]
                best_card = max(player_scores[p][1] for p in top_players)
                winners = [p for p in top_players if player_scores[p][1] == best_card]

                if len(winners) == 1:
                    print(f"🏆 {winners[0]} wins Side Pot {idx+1}!")
                    player_coins[winners[0]] += side_pot
                else:
                    split = side_pot // len(winners)
                    print(f"🤝 Side Pot {idx+1} is split between: {', '.join(winners)}")
                    for p in winners:
                        player_coins[p] += split
        else:
            # No all-in players, resolve full pot
            best_rank = max(score[0] for score in player_scores.values())
            candidates = [p for p, score in player_scores.items() if score[0] == best_rank]
            best_card = max(player_scores[p][1] for p in candidates)
            winners = [p for p in candidates if player_scores[p][1] == best_card]

            if len(winners) == 1:
                print(f"\n🏆 {winners[0]} wins the pot of {pot} coins with the best hand!")
                player_coins[winners[0]] += pot
            else:
                split = pot // len(winners)
                print(f"\n🤝 It's a tie! Pot is split between: {', '.join(winners)}")
                for p in winners:
                    player_coins[p] += split
    
    def compare_hands(player1, player2, player_scores, player_hands, community_cards):
        rank1, high1 = player_scores[player1]
        rank2, high2 = player_scores[player2]

        if rank1 > rank2:
            return player1
        elif rank2 > rank1:
            return player2
        else:
            # Tie in hand_rank - need to go deeper
            if high1 > high2:
                return player1
            elif high2 > high1:
                return player2
            else:
                # They have the same rank AND same high card
                # Optional: check kickers or return 'tie'
                return "tie"





    # Determine the winner(s)
    resolve_side_pots(pot, all_in_players, current_round_bets, player_scores, player_coins)
    

    games_played += 1
    game_on = input("\nDo you want to play another round? (yes/no): ").lower()
