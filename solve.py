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
allow_double = True

# Step 0: Set up all states and transition function
def state_of_card(card):
    card = min(card, 10)
    if card == 1:
        return (11, True)
    else:
        return (card, True)

def transition(state, card):
    card = min(card, 10)
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

# Step 1: Expected value when dealer hits till 17 or above, and player stays on s
ev = {s : {ds : 0 for ds in states} for s in states}
for s in states:
    for ds in states:
        if s[0] > 21:
            ev[s][ds] = -1
            continue

        if ds == (21, True) and s == (21, True):
            ev[s][ds] = 0
        elif ds == (21, True):
            ev[s][ds] = -1
        elif s == (21, True):
            ev[s][ds] = bj_val
        else:
            if ds[0] > 21:
                ev[s][ds] = 1
            elif ds[0] >= 17:
                if ds[0] > s[0]:
                    ev[s][ds] = -1
                elif ds[0] < s[0]:
                    ev[s][ds] = 1
                else:
                    ev[s][ds] = 0
            else:
                if ds == (10, True):
                    # Assume dealer bj is known before
                    cards = range(2, 14)
                elif ds == (11, True):
                    # Assume dealer bj is known before
                    cards = range(1, 10)
                else:
                    cards = range(1, 14)

                for card in cards:
                    new_s = transition(ds, card)
                    ev[s][ds] += Fraction(1, len(cards)) * ev[s][new_s]

# Step 2: Doubles
dev = {s : {ds : 0 for ds in states} for s in states}
for s in states:
    for ds in states:
        for card in range(1, 14):
            new_s = transition(s, card)
            dev[s][ds] += Fraction(2, 13) * ev[new_s][ds]

# Step 3: EV for player when player allowed to hit
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
                    if allow_double:
                        no_split_ev = hit_ev + Fraction(1, 13) * max(dev[new_s][ds], ev2[new_s][ds])
                    else:
                        no_split_ev = hit_ev + Fraction(1, 13) * ev2[new_s][ds]
                else:
                    split_ev = hit_ev * Fraction(13, 5)
                    if allow_double:
                        no_split_ev = hit_ev + Fraction(4, 13) * max(dev[new_s][ds], ev2[new_s][ds])
                    else:
                        no_split_ev = hit_ev + Fraction(4, 13) * ev2[new_s][ds]

                if split_ev > no_split_ev:
                    splits[card][ds] = 0
                    hit_ev = split_ev
                else:
                    splits[card][ds] = 1
                    hit_ev = no_split_ev
                break
            else:
                if allow_double and s[1] and s[0] <= 11:
                    hit_ev += Fraction(1,13) * max(dev[new_s][ds], ev2[new_s][ds])
                else:
                    hit_ev += Fraction(1,13) * ev2[new_s][ds]
        actions[s][ds] = 0 if hit_ev > stay_ev else 1
        ev2[s][ds] = max(hit_ev, stay_ev)

# Step 4: What is overall EV?
total_ev = 0
for i in range(1, 14):
    for j in range(1, 14):
        # i face up and j face down
        for k in range(1, 14):
            for l in range(1, 14):
                k = min(10, k)
                l = min(10, l)

                ds1 = state_of_card(i)
                ds2 = transition(ds1, j)
                s1 = state_of_card(k)
                s2 = transition(s1, l)
                if ds2 == (21, True) and s2 == (21, True):
                    pass
                elif ds2 == (21, True):
                    total_ev += Fraction(1, 13**4) * (-1)
                elif s2 == (21, True):
                    total_ev += Fraction(1, 13**4) * bj_val
                else:
                    if allow_split and k == l and splits[k][ds1] == 0:
                        total_ev += 2 * Fraction(1, 13**4) * ev2[s1][ds1]
                    else:
                        if allow_double:
                            total_ev += Fraction(1, 13**4) * ev2[s2][ds1]
                        else:
                            total_ev += Fraction(1, 13**4) * max(dev[s2][ds1], ev2[s2][ds1])

# Step 5: Display what we found
from prettytable import PrettyTable
def string_of_state(s):
    if s[0] > 21:
        return 'BUST'
    elif s == (21, True):
        return 'BJ'
    elif s[1] == 1 and s[0] >= 11:
        return f'{s[0]-10}/{s[0]}'
    elif s[1] == 1:
        return '(' + str(s[0]) + ')'
    else:
        return str(s[0])

dealer_states = [(i, True) for i in range(2,12)[::-1]]
player_states = [(i, False) for i in range(3,22)[::-1]] + [(i, True) for i in range(12, 21)[::-1]]
#dealer_states = states
#player_states = states
# EV stand table
t = PrettyTable(['EV stand'] + list(map(string_of_state, dealer_states)))
for s in [(i, False) for i in range(16, 22)[::-1]]:
    t.add_row([string_of_state(s)] + [round(float(ev[s][ds]), 3) for ds in dealer_states])
print(t)
print()

# EV table
t = PrettyTable(['EV'] + list(map(string_of_state, dealer_states)))
for s in player_states:
    t.add_row([string_of_state(s)] + [round(float(ev2[s][ds]), 3) for ds in dealer_states])
print(t)
print()

# Action table
t = PrettyTable(['Action'] + list(map(string_of_state, dealer_states)))
for s in player_states:
    vals = []
    for ds in dealer_states:
        if max(dev[s][ds], ev2[s][ds]) < -0.5:
            vals.append('R')
        elif allow_double and dev[s][ds] > ev2[s][ds]:
            vals.append('D')
        elif actions[s][ds]:
            vals.append('S')
        else:
            vals.append('H')
    t.add_row([string_of_state(s)] + vals)
print(t)
print()

# Split table
t = PrettyTable(['Split'] + list(map(string_of_state, dealer_states)))
for i in range(1, 11)[::-1]:
    s = state_of_card(i)
    t.add_row([f'{i}+{i}'] + ['N' if splits[i][ds] else 'S' for ds in dealer_states])
if allow_split:
    print(t)
    print()

print(f'Overal EV: {float(total_ev)}')

# Step 6: Have a policy
def policy(dc, pcs):
    ds = state_of_card(dc)
    s = (0, False)
    for card in pcs:
        s = transition(s, card)
    if len(pcs) == 2 and pcs[0] == pcs[1]:
        if pcs[0] < 10 and not splits[pcs[0]][ds]:
            return 'P'
    if len(pcs) == 2 and max(dev[s][ds], ev2[s][ds]) < -0.5:
        return 'R'
    if len(pcs) == 2 and dev[s][ds] > ev2[s][ds]:
        return 'D'
    if actions[s][ds]:
        return 'S'
    else:
        return 'H'
