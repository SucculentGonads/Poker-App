import time
import random

game_on = "yes"
games_played = 0
dealer_position = 0  # Keeps track of the dealer/button position

while game_on == "yes":  
    player_count = int(input("How many players? "))
    pot = 0

    Deck = [
        "Ace Spades", "King Spades", "Queen Spades", "Jack Spades", "10 Spades", "9 Spades", "8 Spades", "7 Spades", "6 Spades", "5 Spades", "4 Spades", "3 Spades", "2 Spades",
        "Ace Hearts", "King Hearts", "Queen Hearts", "Jack Hearts", "10 Hearts", "9 Hearts", "8 Hearts", "7 Hearts", "6 Hearts", "5 Hearts", "4 Hearts", "3 Hearts", "2 Hearts",
        "Ace Diamonds", "King Diamonds", "Queen Diamonds", "Jack Diamonds", "10 Diamonds", "9 Diamonds", "8 Diamonds", "7 Diamonds", "6 Diamonds", "5 Diamonds", "4 Diamonds", 
        "3 Diamonds", "2 Diamonds", "Ace Clubs", "King Clubs", "Queen Clubs", "Jack Clubs", "10 Clubs", "9 Clubs", "8 Clubs", "7 Clubs", "6 Clubs", "5 Clubs", "4 Clubs", "3 Clubs", "2 Clubs"
    ]
    random.shuffle(Deck)

    dealt_card = 0  # First card each player gets
    players = list(range(1, player_count + 1))  # List of players

    # Rotate dealer, small blind, and big blind
    dealer_position = (dealer_position + 1) % player_count  # Moves dealer to the next player
    small_blind = (dealer_position + 1) % player_count  # Small blind is next player
    big_blind = (dealer_position + 2) % player_count  # Big blind follows

    # Small blind and big blind pot
    small_blind_pot = 500
    big_blind_pot = 1000
    

    print(f"\n🔄 Round {games_played + 1} - Dealer: Player {players[dealer_position]} 🔄\n")

    # ✅ Create dictionaries for hands & pairs &
    player_hands = {}
    player_pairs = {}
    player_coins = {}
    current_round_bets = {} # remember this junt corresponds which each player's bet
    # Deal cards to each player
    current_player = 0 
    for i in range(player_count):  
        
        print(f"Player {players[current_player]}", end=": ")

        player_coins[f"Player {players[current_player]}"] = 10000 # new stuff, gives each player 10k coins 
        # players list has already been created
        # so this is players[0] meaing the first position in players list which is 1
        # current_player changes as the iterations continue
        current_round_bets[f"Player {players[current_player]}"] = 0

        if current_player == small_blind: # gets rid of small blind's coins
            print(f"|| Small Blind Bet: {small_blind_pot} ", end="|| ")
            player_coins[f"Player {players[current_player]}"] -= small_blind_pot 
            current_round_bets[f"Player{players[current_player]}"] = small_blind_pot
        if current_player == big_blind: # gets rid of big blind's coins
            print(f"|| Big Blind Bet: {big_blind_pot} ", end="|| ")
            player_coins[f"Player {players[current_player]}"] -= big_blind_pot
            current_round_bets[f"Player{players[current_player]}"] = big_blind_pot
        
        # ✅ Store player's hand inside the dictionary
        player_hands[f"Player {players[current_player]}"] = [Deck[dealt_card], Deck[dealt_card + 1]]

        print(f"{Deck[dealt_card]}, {Deck[dealt_card + 1]}", end = " ")
        print(player_coins[f"Player {players[current_player]}"])

        # ✅✅ Check for a pair in their hand before the flop
        if Deck[dealt_card].split()[0] == Deck[dealt_card + 1].split()[0]: 
            print("Hand: Pair\n")
            player_pairs[f"Player {players[current_player]}"] = 1
        else:
            player_pairs[f"Player {players[current_player]}"] = 0
        
        dealt_card += 2
        current_player += 1

    # ✅ Print all players' hands after dealing
    print("\n🃏 Players' Hands:")
    for player, hand in player_hands.items():
        print(f"{player}: {hand}")

    # before the flop this where the players will be asked to check, call, or fold 
    # put a pin in this, it'll be eaiser if you create a list that has all player coin value make it 10k for now keep it simple
    current_player = 0
    call_amount = big_blind_pot
    for current_player in range(player_count):
        player_action = input(f"Player {players[current_player]} fold, check, call, or raise... {player_coins[f'Player {players[current_player]}']}")
        while player_action != "check" and player_action != "call" and player_action != "raise" and player_action != "fold":
            player_action = input("Huh? ")
        while player_action == "check" and current_round_bets[f"Player {players[current_player]}"] != call_amount:
            player_action = input(f"checking is not an option for you chuttey, call or raise or fold: ")
            while player_action != "call" and player_action != "raise" and player_action != "fold":
                player_action = input("bro what? that's not an option either, check, raise, or fold: ")
            if player_action == "call":
                current_round_bets[f"Player {players[current_player]}"] = call_amount
                pot += call_amount
            if player_action == "raise":
                raise_ = int(input("How much you raising chuttey? "))
                call_amount += raise_
                pot += call_amount
        while player_action == "call" and current_player == big_blind and big_blind_pot == call_amount:# calling as not an option
            player_action = input("Calling is not an option for you chuttey, check, raise, or fold: ")
            while player_action != "check" and player_action != "raise" and player_action != "fold": # that's not an option either
                player_action = input("bro what? that's not an option either, check, raise, or fold: ")



        if player_action == "raise":
            raise_ = int(input("How much you raising chuttey: "))
            while raise_ <= 0:
                raise_ = int(input("bro what?, give me a real raise: "))
            call_amount += raise_
            pot += call_amount
            current_round_bets[f"Player {players[current_player]}"] = call_amount

        if player_action == "call": 
            if current_player == small_blind:
                call_amount -= 500
                player_coins[f'Player {players[current_player]}'] -= call_amount
                call_amount += 500
                pot += call_amount
                
            else:
                current_round_bets[f"Player {players[current_player]}"] = call_amount
                player_coins[f'Player {players[current_player]}'] -= call_amount
                pot += call_amount
                
        
        if player_action == "fold":
            del players[current_player]
            player_count -= 1
        print(f"Player {players[current_player]} you now have {player_coins[f'Player {players[current_player]}']}")
            

    # ✅✅ Flop (Community Cards)
    print("\n🃏 Flop:")
    time.sleep(1)
    print(f"{Deck[dealt_card]}, {Deck[dealt_card + 1]}, {Deck[dealt_card + 2]}")
    flop_1 = Deck[dealt_card]
    flop_2 = Deck[dealt_card + 1]
    flop_3 = Deck[dealt_card + 2]
    dealt_card += 3  # Move dealt_card forward


    # ✅✅ Check for One Pair, Two Pair, Three of a Kind, Four of a Kind, and Full House
    print("\n🃏 Checking Hands:")
    for player, hand in player_hands.items():
        card1_rank = hand[0].split()[0]
        card2_rank = hand[1].split()[0]
        flop_ranks = [flop_1.split()[0], flop_2.split()[0], flop_3.split()[0]]
        card1_suit = hand[0].split()[1] 
        card2_suit = hand[1].split()[1] 
        flop_suits = [flop_1.split()[1], flop_2.split()[1], flop_3.split()[1]]

        # This is a list that will take the string value of the rank and turn it into an integer respetivley
        rank_values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6,"7": 7, "8": 8, "9": 9, "10": 10,"Jack": 11, "Queen": 12, "King": 13, "Ace": 14}


        # ✅ Combine player's hand and flop ranks
        all_ranks = [card1_rank, card2_rank] + flop_ranks
        all_suits = [card1_suit, card2_suit] + flop_suits
        # this is a list that takes the ranks and turns them into integers respectively and stores it into the values list
        # ✅ Checks for a straight
        values = [rank_values[rank] for rank in all_ranks]
        unique_values = sorted(set(values))
        for i in range(len(unique_values) - 4):
            if unique_values[i + 4] - unique_values[i] == 4:
                 print(f"{player} has a Straight: {unique_values[i]} to {unique_values[i + 4]}")
                 break
        if  all(card == all_suits[0] for card in all_suits):
            print(f"{player} has a Flush: ")

        # ✅ Find all unique ranks that appear exactly twice (pairs)
        pairs = [rank for rank in set(all_ranks) if all_ranks.count(rank) == 2]
        """
        okay so the first "rank" in the loop is a placeholder for the set(all_ranks) to be stored 
        into and then the if statement, if all_ranks.count(rank) checks to see if the now rank
        shows up twice in the original list
        """

        # ✅ Find all unique ranks that appear exactly three times (Three of a Kind)
        three_of_a_kind = [rank for rank in set(all_ranks) if all_ranks.count(rank) == 3]
        """
        See top one to see how this one works
        """
        # ✅ Check for One Pair
        if len(pairs) == 1:
            print(f"{player} has One Pair: {pairs[0]}s")


        # ✅ Check for Two Pair (Two different ranks appear twice)
        if len(pairs) == 2:
            print(f"{player} has Two Pair: {pairs[0]}s and {pairs[1]}s!")

        # ✅ Check for Full House (Three of a Kind + One Pair)
        if three_of_a_kind and pairs:
            print(f"{player} has a Full House: {three_of_a_kind[0]}s over {pairs[0]}s!")

        # ✅ Check for Three of a Kind and Four of a Kind
        for rank in set(all_ranks):
            if all_ranks.count(rank) == 3:
                print(f"{player} has Three of a Kind with {rank}s!")
            elif all_ranks.count(rank) == 4:
                print(f"{player} has Four of a Kind with {rank}s!")
                break  # No need to check further
        """  
        the rank in the for loop runs through all the values in the list all_ranks
        except the duplicates because set() removes them and as it's running through each value 
        the if and elif check if they show up 3 times or 4 times respectivley
        """
    games_played += 1  # Increment the game counter

    # Ask if players want to continue playing
    game_on = input("\nDo you want to play another round? (yes/no): ").lower()
# can you fix up my code so that the player after the big blind goes first and it ends with the big blind before the first flop