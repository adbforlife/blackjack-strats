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
dealer_states = [(11, True), (10, True)] + [(i, False) for i in range(2,10)[::-1]]

# Step 1: Expected value when dealer hits till 17 or above
ev = {i : {s : 0 for s in states} for i in range(16, 22)}
for i in range(16, 22)[::-1]:
    for s in states:
        if s[0] > 21:
            ev[i][s] = 1
        elif s[0] >= 17:
            if s[0] > i:
                ev[i][s] = -1
            elif s[0] == i:
                ev[i][s] = 0
            else:
                ev[i][s] = 1
        else:
            for card in range(1, 14):
                new_s = transition(s, card)
                ev[i][s] += Fraction(1,13) * ev[i][new_s]

# Step 2: EV for player when player allowed to hit
ev2 = {s : {ds : 0 for ds in dealer_states} for s in states}
actions = {s : {ds : 0 for ds in dealer_states} for s in states} # 0 for hit

for s in states:
    for ds in dealer_states:
        if s[0] > 21:
            ev2[s][ds] = -1
            continue
        stay_ev = ev[16 if s[0] < 17 else s[0]][ds]
        hit_ev = 0
        for card in range(1, 14):
            new_s = transition(s, card)
            if new_s[0] > 21:
                new_ev = -1
            else:
                new_ev = ev2[new_s][ds]
            hit_ev += Fraction(1,13) * new_ev
        actions[s][ds] = 0 if hit_ev > stay_ev else 1
        ev2[s][ds] = max(hit_ev, stay_ev)

# Step 3: What is overall EV?
def state_of_card(card):
    card = 10 if card > 10 else card
    if card == 1:
        return (11, True)
    else:
        return (card, False)

total_ev = 0
for i in range(1, 14):
    for j in range(1, 14):
        for k in range(1, 14):
            if (j == 1 and k >= 10) or (j >= 10 and k == 1):
                if i == 1:
                    total_ev += Fraction(1, 13**3) * Fraction(9, 13) * bj_val
                elif i >= 10:
                    total_ev += Fraction(1, 13**3) * Fraction(12, 13) * bj_val
                else:
                    total_ev += Fraction(1, 13**3) * bj_val
                continue
            ds = state_of_card(i)
            s = state_of_card(j)
            s = transition(s, k)
            if i == 1:
                for l in range(1, 14):
                    ds2 = transition(ds, l)
                    if ds2[0] == 21:
            total_ev += Fraction(1, 13**3) * ev2[s][ds]

# Step 4: Display what we found
from prettytable import PrettyTable
def string_of_state(s):
    if not s[1]:
        return str(s[0])
    else:
        return f'{s[0]-10}/{s[0]}'

t = PrettyTable(['EV'] + list(map(str, range(2, 12)[::-1])))
for s in sorted(states)[::-1][1:]:
    t.add_row([string_of_state(s)] + [round(float(ev2[s][ds]), 3) for ds in dealer_states])
print(t)
print()

t = PrettyTable(['Action'] + list(map(str, range(2, 12)[::-1])))
for s in sorted(states)[::-1][1:]:
    t.add_row([string_of_state(s)] + ['S' if actions[s][ds] else 'H' for ds in dealer_states])
print(t)

print(f'Overal EV: {float(total_ev)}')
