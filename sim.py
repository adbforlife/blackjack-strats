from random import randint

bj_val = 1.5

def value(cards):
    cards = list(map(lambda x: min(10, x), cards))
    s = sum(cards)
    if 1 in cards:
        if s + 10 <= 21:
            return s + 10
        else:
            return s
    return s

def compare(dcs, pcs):
    vd = value(dcs)
    vp = value(pcs)
    bjd = (vd == 21 and len(dcs) == 2)
    bjp = (vp == 21 and len(pcs) == 2)
    if bjd and bjp:
        return 0
    elif bjd:
        return -1
    elif bjp:
        return bj_val
    elif vp > 21:
        return -1
    elif vd > 21:
        return 1
    elif vp > vd:
        return 1
    elif vp == vd:
        return 0
    else:
        assert(vp < vd)
        return -1

# policy takes in a tuple of (dealer_card, player_cards) and output one of ('S', 'H', 'D', 'P')
def play(policy, dcs, pcs):
    bet = 1

    vd = value(dcs[:2])
    vp = value(pcs[:2])
    if vd == 21 and vp == 21:
        return 0
    elif vd == 21:
        return -1
    elif vp == 21:
        return bj_val

    while 1:
        action = policy(dcs[0], pcs)
        if action == 'S':
            break
        elif action == 'H':
            pcs.append(randint(1, 13))
            if value(pcs) > 21:
                break
        elif action == 'P':
            assert(len(pcs) == 2)
            assert((pcs[0] >= 10 and pcs[1] >= 10) or (pcs[0] == pcs[1]))
            return play(policy, dcs, pcs[:1]) + play(policy, dcs, pcs[:1])
        elif action == 'D':
            assert(len(pcs) == 2)
            bet *= 2
            pcs.append(randint(1, 13))
            break

    # compare hands
    return compare(dcs, pcs) * bet


from solve import policy
money = 0
n = 0
while 1:
    n += 1
    dcs = []
    while value(dcs) < 17:
        dcs.append(randint(1, 13))
    pcs = [randint(1, 13), randint(1, 13)]
    money += play(policy, dcs, pcs)
    ev = money / n
    if n % 1000 == 0:
        print(' ' * 80, end="\r", flush=True)
        print(f'round {n}\tmoney {money}\t\tev {ev}', end="\r", flush=True)

