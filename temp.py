a = {'a': 'cjjfjb'}

if 'cjjfjb' in a.values():
    b = {val: key for key, val in a.items()}
    print(b)
    print('true')
else:
    print('false')
