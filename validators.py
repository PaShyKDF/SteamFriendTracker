def validate_game_url(url: str) -> bool:
    if url:
        if url.startswith('https://store.steampowered.com/app/'):
            return url
    else:
        return False


def validate_profile_url(url: str) -> bool:
    if url:
        return (url.startswith('https://steamcommunity.com/id/')
                or url.startswith('https://steamcommunity.com/profiles/'))


d = {'730': 'Counter-Strike 2', '570': 'Dota 2'}

if __name__ == '__main__':
    print(validate_game_url(
        'https://store.steampowered.com/app/2784840/Egg/'))

    for i, j in d.items():
        print(i, j)
