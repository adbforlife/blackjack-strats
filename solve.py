from fractions import Fraction

# states: (value, is_soft)
# (22, False) is BUST state
# (21, True) is BLACKJACK
# (11, True) is single A
# (10, True) is single 10
# (9, True) is single 9
# (0, False) is initial state
bj_val = 1.5
allow_split = True

# Step 0: Set up all states and transition function
def state_of_card(card):
    card = 10 if card > 10 else card
    if card == 1:
        return (11, True)
    else:
        return (card, True)

def transition(state, card):
    card = 10 if card > 10 else card
    if state == (0, False):
        return state_of_card(card)
    val, is_soft = state
    res = val + card
    if val >= 21:
        return 22, False
    elif is_soft:
        if val == 10:
            if card == 1:
                return 21, True
            else:
                return res, False
        elif val == 11:
            return res, True
        elif val < 10:
            if card == 1:
                return res + 10, True
            else:
                return res, False
        else:
            if res > 21:
                return res - 10, False
            elif res == 21:
                return 21, False
            else:
                return res, True
    else:
        if res > 21:
            return 22, False
        elif card != 1:
            return res, False
        elif res <= 10:
            return res + 10, True
        elif res == 11:
            return res + 10, False
        else:
            return res, False

states = [(i, False) for i in range(10, 23)[::-1]]
states += [(21, True)]
for i in range(2,10)[::-1]:
    states += [(i+11, True), (i, False), (i, True)]
states += [(12, True), (11, True), (10, True), (0, False)]

# Step 1: Expected value when dealer hits till 17 or above
ev = {s : {ds : 0 for ds in states} for s in states}
for s in states:
    for ds in states:
        if s[0] > 21:
            ev[s][ds] = -1
            continue
        if ds[0] > 21:
            ev[s][ds] = 1
        elif ds[0] >= 17:
            if ds == (21, True) and s == (21, True):
                ev[s][ds] = 0
            elif ds == (21, True):
                ev[s][ds] = -1
            elif s == (21, True):
                ev[s][ds] = bj_val
            elif ds[0] > s[0]:
                ev[s][ds] = -1
            elif ds[0] < s[0]:
                ev[s][ds] = 1
            else:
                ev[s][ds] = 0
        else:
            for card in range(1, 14):
                new_s = transition(ds, card)
                ev[s][ds] += Fraction(1,13) * ev[s][new_s]

# Step 2: EV for player when player allowed to hit
ev2 = {s : {ds : 0 for ds in states} for s in states}
actions = {s : {ds : 0 for ds in states} for s in states} # 0 for hit
splits = {i : {ds : 0 for ds in states} for i in range(1, 11)} # 0 for split

for s in states:
    for ds in states:
        if s[0] > 21:
            ev2[s][ds] = -1
            continue
        stay_ev = ev[s][ds]
        hit_ev = 0
        cards = sorted([10,10,10] + list(range(1, 11))[::-1], key=lambda x: x == s[0])
        for card in cards:
            new_s = transition(s, card)
            if allow_split and s[1] and (card == s[0] or (card == 1 and s[0] == 11)):
                # If split, then EV(s, ds) = 2/13 EV(s, ds) + ...
                # Or if face card EV(s, ds) = 8/13 EV(s, ds) + ...
                if card != 10:
                    split_ev = hit_ev * Fraction(13, 11)
                    no_split_ev = hit_ev + Fraction(1, 13) * ev2[new_s][ds]
                    if card == 8:
                        print(s, ds)
                        print(round(hit_ev, 3), round(split_ev, 3), round(no_split_ev, 3))
                else:
                    split_ev = hit_ev * Fraction(13, 5)
                    no_split_ev = hit_ev + Fraction(4, 13) * ev2[new_s][ds]

                if split_ev > no_split_ev:
                    splits[card][ds] = 0
                    hit_ev = split_ev
                else:
                    splits[card][ds] = 1
                    hit_ev = no_split_ev
                break
            else:
                hit_ev += Fraction(1,13) * ev2[new_s][ds]
        actions[s][ds] = 0 if hit_ev > stay_ev else 1
        ev2[s][ds] = max(hit_ev, stay_ev)

# Step 3: What is overall EV?
total_ev = 0
for i in range(1, 14):
    ds = state_of_card(i)
    total_ev += Fraction(1, 13) * ev2[(0, False)][ds]

# Step 4: Display what we found
from prettytable import PrettyTable
def string_of_state(s):
    if s[0] > 21:
        return 'BUST'
    elif s == (21, True):
        return 'BJ'
    elif s[1] == 1 and s[0] >= 11:
        return f'{s[0]-10}/{s[0]}'
    else:
        return str(s[0])

dealer_states = [(i, True) for i in range(2,12)[::-1]]
player_states = [(i, False) for i in range(3, 22)[::-1]] + [(i, True) for i in range(11, 21)[::-1]]
# EV table
t = PrettyTable(['EV'] + list(map(string_of_state, dealer_states)))
for s in player_states:
    t.add_row([string_of_state(s)] + [round(float(ev2[s][ds]), 3) for ds in dealer_states])
print(t)
print()

# Action table
t = PrettyTable(['Action'] + list(map(string_of_state, dealer_states)))
for s in player_states:
    t.add_row([string_of_state(s)] + ['S' if actions[s][ds] else 'H' for ds in dealer_states])
print(t)
print()

# Split table
t = PrettyTable(['Split'] + list(map(string_of_state, dealer_states)))
for i in range(1, 11)[::-1]:
    s = state_of_card(i)
    t.add_row([f'{i}+{i}'] + ['NS' if splits[i][ds] else 'SP' for ds in dealer_states])
if allow_split:
    print(t)
    print()

print(f'Overal EV: {float(total_ev)}')
