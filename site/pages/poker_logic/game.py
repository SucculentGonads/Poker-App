#game.py
import random
from collections import Counter
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.sessions.models import Session
from django.utils.timezone import now as timezone_now
from datetime import timedelta

class PokerGame:
    def __init__(self, usernames):
        self.players = usernames  # ✅ Set the actual usernames
        self.player_count = len(usernames)  # ✅ Count from usernames

        self.dealer_position = 0
        self.small_blind_pot = 500
        self.big_blind_pot = 1000
        self.pot = 0
        self.deck = self._generate_shuffled_deck()
        self.player_hands = {}
        self.player_coins = {p: 100000 for p in self.players}
        self.current_round_bets = {p: 0 for p in self.players}
        self.community_cards = []
        self.player_scores = {}
        self.all_in_players = {}
        self.call_amount = self.big_blind_pot
        self.folded_players = set()
        self.ui_log = []
        from django.utils.timezone import now as timezone_now
        self.last_active = {p: timezone_now() for p in self.players}
        self.hand_started = False
        self.seat_assignments = {}  # Stores username: seat_number
        self.next_seat_number = 1   # Tracks the next available seat (1-9)

        if len(self.players) >= 2:
            self._assign_blinds()
            self.deal_hands(self.players)
        else:
            self.ui_log.append("⏳ Waiting for at least 2 players to start dealing.")
        #self._deal_flop()

        #this shit should take care of players that leave and get them off the table
    def mark_active(self, player):
        from django.utils.timezone import now as timezone_now
        self.last_active[player] = timezone_now()

    def assign_seat(self, username):
        """Assign the lowest‐numbered available seat (1–9)."""
        if username in self.seat_assignments:
            return
        taken = set(self.seat_assignments.values())
        for seat in range(1, 10):
            if seat not in taken:
                self.seat_assignments[username] = seat
                return


    def remove_inactive_players(self):
        threshold_time = timezone_now() - timedelta(seconds=30)

        active_sessions = Session.objects.filter(expire_date__gte=timezone_now())
        active_user_ids_in_room = []

        for session in active_sessions:
            data = session.get_decoded()
            if data.get("_auth_user_id") and data.get("in_room") == True:
                active_user_ids_in_room.append(data["_auth_user_id"])

        # Convert IDs to usernames
        active_users = User.objects.filter(id__in=active_user_ids_in_room)
        active_usernames = [user.username for user in active_users]

        # Find players who are still active
        active_recent_players = [
            p for p in self.players
            if p in active_usernames and self.last_active.get(p, timezone_now()) >= threshold_time
        ]

        # Find players to remove
        players_to_remove = set(self.players) - set(active_recent_players)

        # Cleanup all their data
        for p in players_to_remove:
            self.player_hands.pop(p, None)
            self.player_coins.pop(p, None)
            self.current_round_bets.pop(p, None)
            self.last_active.pop(p, None)
            self.all_in_players.pop(p, None)

        # Update player list
        self.players = [p for p in self.players if p not in players_to_remove]

        for p in players_to_remove:
           self.seat_assignments.pop(p, None)
        #this shit should take care of players that leave and get them off the table


    def _generate_shuffled_deck(self):
        deck = [
            "Ace_Spades", "King_Spades", "Queen_Spades", "Jack_Spades", "10_Spades", "9_Spades", "8_Spades", "7_Spades", "6_Spades", "5_Spades", "4_Spades", "3_Spades", "2_Spades",
            "Ace_Hearts", "King_Hearts", "Queen_Hearts", "Jack_Hearts", "10_Hearts", "9_Hearts", "8_Hearts", "7_Hearts", "6_Hearts", "5_Hearts", "4_Hearts", "3_Hearts", "2_Hearts",
            "Ace_Diamonds", "King_Diamonds", "Queen_Diamonds", "Jack_Diamonds", "10_Diamonds", "9_Diamonds", "8_Diamonds", "7_Diamonds", "6_Diamonds", "5_Diamonds", "4_Diamonds", "3_Diamonds", "2_Diamonds",
            "Ace_Clubs", "King_Clubs", "Queen_Clubs", "Jack_Clubs", "10_Clubs", "9_Clubs", "8_Clubs", "7_Clubs", "6_Clubs", "5_Clubs", "4_Clubs", "3_Clubs", "2_Clubs"
        ]
        random.shuffle(deck)
        return deck


    def _assign_blinds(self):
        if not self.players or len(self.players) < 2:
            return  # can't assign blinds with fewer than 2 players

        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self.small_blind = self.players[(self.dealer_position + 1) % len(self.players)]
        self.big_blind = self.players[(self.dealer_position + 2) % len(self.players)]

        self.player_coins[self.small_blind] -= self.small_blind_pot
        self.player_coins[self.big_blind] -= self.big_blind_pot

        self.current_round_bets[self.small_blind] = self.small_blind_pot
        self.current_round_bets[self.big_blind] = self.big_blind_pot


    def deal_hands(self, usernames):
        """Deals two hole cards to each username and stores them in player_hands."""
        for username in usernames:
            if username not in self.player_hands:
                if len(self.deck) < 2:
                    # You might want to start a new hand or reshuffle here
                    self.deck = self._generate_shuffled_deck()
                    self.community_cards = []
                    self.ui_log.append("🃏 Deck reshuffled to deal more cards.")

                self.player_hands[username] = [self.deck.pop(), self.deck.pop()]



    def _deal_flop(self):
        self.deck.pop()  # Burn one
        flop = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        self.community_cards.extend(flop)

    def start_betting_round(self, first_round=False):
        """Prepares the betting order and sets the call amount based on current bets."""
        if not self.players:
            return

        self.call_amount = max(self.current_round_bets.values(), default=0)

        # Determine where to start the action
        if first_round:
            start_index = (self.dealer_position + 3) % len(self.players)  # UTG (Under The Gun)
        else:
            start_index = (self.dealer_position + 1) % len(self.players)

        ordered_players = self.players[start_index:] + self.players[:start_index]

        # Only include players who haven't folded and still have coins
        self.betting_order = [
            p for p in ordered_players 
            if p not in self.folded_players and self.player_coins.get(p, 0) > 0
        ]

        self.current_player_index = 0
        self.waiting_for_action = True



    def apply_player_action(self, player, action, raise_amount=None):
        if not self.waiting_for_action:
            self.ui_log.append("⏳ No betting round in progress.")
            return {"status": "error", "message": "No betting round in progress."}

        expected_player = self.betting_order[self.current_player_index]
        if player != expected_player:
            self.ui_log.append(f"⛔ {player} tried to act out of turn.")
            return {"status": "error", "message": "It's not your turn."}

        current_bet = self.current_round_bets.get(player, 0)
        diff = self.call_amount - current_bet

        if action == "fold":
            self.folded_players.add(player)
            self.ui_log.append(f"🫣 {player} folded.")
            message = f"{player} folded."

        elif action == "call":
            call_amount = min(diff, self.player_coins[player])
            self.player_coins[player] -= call_amount
            self.current_round_bets[player] += call_amount
            self.pot += call_amount
            if self.player_coins[player] == 0:
                self.all_in_players[player] = self.current_round_bets[player]
            self.ui_log.append(f"📞 {player} called {call_amount}.")
            message = f"{player} called {call_amount}."

        elif action == "check":
            if diff > 0:
                self.ui_log.append(f"❌ {player} tried to check when a call is needed.")
                return {"status": "error", "message": "You can't check, you must call or fold."}
            self.ui_log.append(f"✅ {player} checked.")
            message = f"{player} checked."

        elif action == "raise":
            if raise_amount is None or raise_amount <= diff:
                self.ui_log.append(f"❌ {player} tried to raise with an invalid amount.")
                return {"status": "error", "message": "Invalid raise amount. Must be greater than the call."}

            total_amount = diff + raise_amount
            if self.player_coins[player] < total_amount:
                self.ui_log.append(f"❌ {player} tried to raise but doesn’t have enough coins.")
                return {"status": "error", "message": "Not enough coins to raise."}

            self.player_coins[player] -= total_amount
            self.current_round_bets[player] += total_amount
            self.pot += total_amount
            self.call_amount = self.current_round_bets[player]
            self.ui_log.append(f"💰 {player} raised to {self.call_amount}.")
            message = f"{player} raised to {self.call_amount}."

        elif action == "all-in":
            all_in_amount = self.player_coins[player]
            self.player_coins[player] = 0
            self.current_round_bets[player] += all_in_amount
            self.pot += all_in_amount
            self.all_in_players[player] = self.current_round_bets[player]
            if self.current_round_bets[player] > self.call_amount:
                self.call_amount = self.current_round_bets[player]
            self.ui_log.append(f"💀 {player} goes all-in with {all_in_amount}.")
            message = f"{player} goes all-in with {all_in_amount}."

        else:
            return {"status": "error", "message": f"Invalid action: {action}"}

        # Advance turn
        self.current_player_index += 1
        if self.current_player_index >= len(self.betting_order):
            self.waiting_for_action = False
            self.ui_log.append("✅ Betting round completed.")

            # If no community cards yet, deal flop next
            if not self.community_cards:
                self._deal_flop()
                self.ui_log.append("🃏 Flop dealt.")
                self.start_betting_round()

        return {"status": "ok", "message": message}




    def check_player_hands(self):
        rank_values = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
            "7": 7, "8": 8, "9": 9, "10": 10,
            "Jack": 11, "Queen": 12, "King": 13, "Ace": 14
        }

        for player, hand in self.player_hands.items():
            all_cards = hand + self.community_cards
            all_ranks = [card.split("_")[0] for card in all_cards]
            all_suits = [card.split("_")[1] for card in all_cards]
            rank_vals = [rank_values[rank] for rank in all_ranks]
            unique_vals = sorted(set(rank_vals))

            hand_rank = 1  # Default: High card
            highest_card = max(rank_vals)

            # Check for Straight Flush / Royal Flush
            suit_dict = {}
            for card in all_cards:
                rank, suit = card.split("_")
                value = rank_values[rank]
                suit_dict.setdefault(suit, []).append(value)

            for suit, vals in suit_dict.items():
                if len(vals) >= 5:
                    sorted_vals = sorted(set(vals))
                    if 14 in sorted_vals:
                        sorted_vals.append(1)
                        sorted_vals = sorted(set(sorted_vals))
                    for i in range(len(sorted_vals) - 4):
                        window = sorted_vals[i:i + 5]
                        if window == [10, 11, 12, 13, 14]:
                            hand_rank = 10  # Royal flush
                            highest_card = 14
                        elif window[-1] - window[0] == 4:
                            hand_rank = 9  # Straight flush
                            highest_card = window[-1]

            # Four of a kind
            if hand_rank < 8:
                for rank in set(all_ranks):
                    if all_ranks.count(rank) == 4:
                        hand_rank = 8
                        highest_card = rank_values[rank]
                        break

            # Full house
            pairs = [rank for rank in set(all_ranks) if all_ranks.count(rank) == 2]
            three_of_a_kind = [rank for rank in set(all_ranks) if all_ranks.count(rank) == 3]
            if hand_rank < 7 and three_of_a_kind and pairs:
                hand_rank = 7
                highest_card = max(rank_values[r] for r in three_of_a_kind)

            # Flush
            suit_counts = Counter(all_suits)
            for suit, count in suit_counts.items():
                if count >= 5:
                    hand_rank = max(hand_rank, 6)
                    break

            # Straight
            if hand_rank < 5:
                if set([14, 2, 3, 4, 5]).issubset(set(rank_vals)):
                    hand_rank = 5
                    highest_card = 5
                else:
                    for i in range(len(unique_vals) - 4):
                        if unique_vals[i + 4] - unique_vals[i] == 4:
                            hand_rank = 5
                            highest_card = unique_vals[i + 4]
                            break

            # Three of a kind
            if hand_rank < 4 and three_of_a_kind:
                hand_rank = 4
                highest_card = max(rank_values[r] for r in three_of_a_kind)

            # Two pair or One pair
            if hand_rank < 4:
                if len(pairs) >= 2:
                    hand_rank = 3
                    highest_card = max(rank_values[r] for r in pairs)
                elif len(pairs) == 1:
                    hand_rank = 2
                    highest_card = rank_values[pairs[0]]

            # High card fallback
            if hand_rank == 1:
                highest_card = max(rank_vals)

            self.player_scores[player] = (hand_rank, highest_card)

    def _deal_turn(self):
        self.deck.pop()  # Burn one
        self.community_cards.append(self.deck.pop())

    def proceed_after_flop(self):
        self.check_player_hands()
        self.start_betting_round()  # Use your updated betting round starter
        self._deal_turn()
        # You can log or return the card for debugging/UI
        self.ui_log.append(f"🃏 Turn card dealt: {self.community_cards[-1]}")

    def _deal_river(self):
        self.deck.pop()  # Burn one
        self.community_cards.append(self.deck.pop())

    def proceed_after_turn(self):
        self.check_player_hands()
        self.start_betting_round()  # Use the updated method name
        self._deal_river()
        print("River card dealt:", self.community_cards[-1])


    def proceed_after_river(self):
        self.check_player_hands()
        self.start_betting_round()  # Renamed from betting_round()
        self.resolve_side_pots()
        self.ui_log.append("✅ Round completed. Pot resolved.")


    def compare_hands(self, player1, player2):
        score1 = self.player_scores[player1]
        score2 = self.player_scores[player2]

        if score1[0] > score2[0]:
            return player1
        elif score2[0] > score1[0]:
            return player2
        else:
            # Same hand rank: compare kickers
            def get_sorted_values(player):
                rank_values = {
                    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
                    "7": 7, "8": 8, "9": 9, "10": 10,
                    "Jack": 11, "Queen": 12, "King": 13, "Ace": 14
                }
                cards = self.player_hands[player] + self.community_cards
                values = [rank_values[c.split("_")[0]] for c in cards]
                return sorted(values, reverse=True)

            kicker1 = get_sorted_values(player1)
            kicker2 = get_sorted_values(player2)

            for v1, v2 in zip(kicker1, kicker2):
                if v1 > v2:
                    return player1
                elif v2 > v1:
                    return player2

            return "tie"


    @property
    def active_players(self):
        return [
            p for p in self.players
            if p not in self.folded_players and
            (self.player_coins.get(p, 0) > 0 or self.current_round_bets.get(p, 0) > 0)
        ]




    def resolve_side_pots(self):
        self.ui_log.append("\n💰 Resolving Pots...")

        if self.all_in_players:
            side_pots = []
            unique_all_in_amounts = sorted(set(self.all_in_players.values()))
            previous = 0

            for amount in unique_all_in_amounts:
                pot_amount = 0
                eligible_players = []

                for player, bet in self.current_round_bets.items():
                    contrib = min(bet, amount - previous)
                    pot_amount += contrib
                    if bet >= amount:
                        eligible_players.append(player)

                side_pots.append((pot_amount, eligible_players))
                previous = amount

            for idx, (side_pot, eligibles) in enumerate(side_pots):
                self.ui_log.append(f"🪙 Side Pot {idx + 1} - {side_pot} coins between: {', '.join(eligibles)}")

                eligible_scores = {p: self.player_scores[p] for p in eligibles}
                best_rank = max(score[0] for score in eligible_scores.values())
                top_players = [p for p, score in eligible_scores.items() if score[0] == best_rank]
                best_card = max(self.player_scores[p][1] for p in top_players)
                winners = [p for p in top_players if self.player_scores[p][1] == best_card]

                if len(winners) == 1:
                    winner = winners[0]
                    self.ui_log.append(f"🏆 {winner} wins the pot of {self.pot} coins with the best hand!")
                    self.player_coins[winner] += side_pot
                else:
                    split = side_pot // len(winners)
                    self.ui_log.append(f"🤝 It's a tie! Pot is split between: {', '.join(winners)}")
                    for p in winners:
                        self.player_coins[p] += split

        else:
            # Single pot scenario (no all-ins)
            best_rank = max(score[0] for score in self.player_scores.values())
            candidates = [p for p, score in self.player_scores.items() if score[0] == best_rank]
            best_card = max(self.player_scores[p][1] for p in candidates)
            winners = [p for p in candidates if self.player_scores[p][1] == best_card]

            if len(winners) == 1:
                winner = winners[0]
                self.ui_log.append(f"\n🏆 {winner} wins the pot of {self.pot} coins with the best hand!")
                self.player_coins[winner] += self.pot
            else:
                split = self.pot // len(winners)
                self.ui_log.append(f"\n🤝 It's a tie! Pot is split between: {', '.join(winners)}")
                for p in winners:
                    self.player_coins[p] += split


    def start_new_hand(self):
        if len(self.players) < 2:
            self.ui_log.append("⚠️ Not enough players to start a new hand. Waiting for more players.")
            return
        self.hand_started = True

        # Remove players who are out of chips
        self.folded_players = set()
        self.players = [p for p in self.players if self.player_coins.get(p, 0) > 0]

        if self.is_game_over():
            self.hand_started = False
            self.ui_log.append("🛑 Game over! Not enough players with coins.")
            return

        self.ui_log.append("\n🔄 Starting a new hand...\n")

        self.deck = self._generate_shuffled_deck()
        self.pot = 0
        self.community_cards = []
        self.player_hands = {}
        self.player_scores = {}
        self.all_in_players = {}
        self.current_round_bets = {p: 0 for p in self.players}
        self.call_amount = self.big_blind_pot

        self._assign_blinds()

        # Use deal_hands() instead of _deal_cards()
        self.deal_hands(self.players)

        #self._deal_flop()

        self.ui_log.append(f"📍 Dealer is now {self.players[self.dealer_position]}")
        self.ui_log.append("🃏 Hole cards and flop dealt. Begin betting round.")


    def is_game_over(self):
        # Game ends if only one player has coins
        active_players = [p for p in self.players if self.player_coins.get(p, 0) > 0]
        if len(active_players) == 1:
            winner = active_players[0]
            self.ui_log.append(f"\n🏁 Game Over! {winner} is the last player standing with {self.player_coins[winner]} coins.")
            return True

        return False  # Game continues

    def is_hand_over_due_to_folds(self):
        # If only one player didn't fold, end the hand and give them the pot
        remaining = [p for p in self.players if p not in self.folded_players]
        if len(remaining) == 1:
            winner = remaining[0]
            self.ui_log.append(f"🏁 Everyone else folded. {winner} wins the hand uncontested!")
            self.player_coins[winner] += self.pot
            return True
        return False


    def play_hand(self):
        self.start_betting_round(first_round=True)
        if self.is_game_over() or self.is_hand_over_due_to_folds():
            return

        self.proceed_after_flop()
        if self.is_game_over() or self.is_hand_over_due_to_folds():
            return

        self.proceed_after_turn()
        if self.is_game_over() or self.is_hand_over_due_to_folds():
            return

        self.proceed_after_river()
        if self.is_game_over():
            self.hand_started = False
            return 

        self.start_new_hand()

