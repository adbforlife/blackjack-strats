from fractions import Fraction

# states: (value, is_soft)
# (22, False) is BUST state
# (21, True) is BLACKJACK
# (11, True) is single A
# (10, True) is single 10
bj_val = 1.5

def transition(state, card):
    card = 10 if card > 10 else card
    val, is_soft = state
    res = val + card
    if val >= 21:
        return 22, False
    elif (val, is_soft) == (10, True):
        if card == 1:
            return 21, True
        else:
            return res, False
    elif (val, is_soft) == (11, True):
        return res, True
    elif is_soft:
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
    states += [(i+11, True), (i, False)]
states += [(12, True), (11, True), (10, True)]

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
            if ds[0] > s[0]:
                ev[s][ds] = -1
            elif ds[0] < s[0]:
                ev[s][ds] = 1
            elif ds[0] != 21:
                ev[s][ds] = 0
            elif ds[1] and not s[1]:
                ev[s][ds] = -1
            elif not ds[1] and s[1]:
                ev[s][ds] = bj_val
            else:
                ev[s][ds] = 0
        else:
            for card in range(1, 14):
                new_s = transition(ds, card)
                ev[s][ds] += Fraction(1,13) * ev[s][new_s]
print(ev)

# Step 2: EV for player when player allowed to hit
ev2 = {s : {ds : 0 for ds in states} for s in states}
actions = {s : {ds : 0 for ds in states} for s in states} # 0 for hit

for s in states:
    for ds in states:
        if s[0] > 21:
            ev2[s][ds] = -1
            continue
        stay_ev = ev[s][ds]
        hit_ev = 0
        for card in range(1, 14):
            new_s = transition(s, card)
            hit_ev += Fraction(1,13) * ev2[new_s][ds]
        actions[s][ds] = 0 if hit_ev > stay_ev else 1
        ev2[s][ds] = max(hit_ev, stay_ev)

# Step 3: What is overall EV?
def state_of_card(card):
    card = 10 if card > 10 else card
    if card == 1:
        return (11, True)
    elif card == 10:
        return (10, True)
    else:
        return (card, False)

total_ev = 0
for i in range(1, 14):
    for j in range(1, 14):
        for k in range(1, 14):
            ds = state_of_card(i)
            s = state_of_card(j)
            s = transition(s, k)
            total_ev += Fraction(1, 13**3) * ev2[s][ds]

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

dealer_states = [(11, True), (10, True)] + [(i, False) for i in range(2,10)[::-1]]
player_states = [(i, False) for i in range(3, 22)[::-1]] + [(i, True) for i in range(12, 21)[::-1]]
t = PrettyTable(['EV'] + list(map(string_of_state, dealer_states)))
for s in player_states:
    t.add_row([string_of_state(s)] + [round(float(ev2[s][ds]), 3) for ds in dealer_states])
print(t)
print()

t = PrettyTable(['Action'] + list(map(string_of_state, dealer_states)))
for s in player_states:
    t.add_row([string_of_state(s)] + ['S' if actions[s][ds] else 'H' for ds in dealer_states])
print(t)

print(f'Overal EV: {float(total_ev)}')