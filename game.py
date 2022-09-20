from random import randint

def value(cards):
    cards = list(map(lambda x: 10 if x > 10 else x, cards))
    s = sum(cards)
    if 1 in cards:
        if s + 10 <= 21:
            return s + 10
        else:
            return s
    return s

def to_string(card):
    if card == 1:
        return 'A'
    elif card == 11:
        return 'J'
    elif card == 12:
        return 'Q'
    elif card == 13:
        return 'K'
    else:
        return str(card)

def describe(cards):
    return f'{list(map(to_string, cards))}, {value(cards)}'

if __name__ == '__main__':
    print('Welcome to a game of blackjack .')
    while 1:
        print('------------------')
        dealer = [randint(1, 13)]
        player = [randint(1, 13), randint(1, 13)]
        print(f'Dealer: {describe(dealer)}')
        print(f'Player: {describe(player)}')
        while 1:
            i = input('Hit? (y/n) ')
            if i == 'y':
                player.append(randint(1,13))
                print(f'Player: {describe(player)}')
                if value(player) > 21:
                    break
            elif i == 'n':
                break
            else:
                print('Please specify y/n.')
        if value(player) > 21:
            print('Player BUST')
            continue
        while value(dealer) < 17:
            dealer.append(randint(1,13))
            print(f'Dealer: {describe(dealer)}')
        d = value(dealer)
        if d > 21:
            print('Dealer BUST')
            continue
        p = value(player)
        if p > d:
            print('Player wins')
        elif p == d:
            print('Push')
        else:
            print('Dealer wins')

