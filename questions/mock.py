from core.mock import MEMBERS, TAGS, TEXT

VOTES = ['up', 'down', '']

QUESTIONS = []
for i in range(1, 30):
    QUESTIONS.append({
        'id': i,
        'title': 'Как это сделать? ' + str(i),
        'text': TEXT,
        'author': MEMBERS[i % 3],
        'date': '04-Дек-07 18:04',
        'rating': i % 7,
        'vote': VOTES[i % 3],
        'answers_count': 7,
        'tags': [TAGS[i % 4], TAGS[(i + 1) % 4]],
    })

ANSWERS = []
for i in range(1, 8):
    ANSWERS.append({
        'text': TEXT,
        'author': MEMBERS[i % 3],
        'date': '05-Дек-07 21:15',
        'rating': i % 5,
        'vote': VOTES[i % 3],
        'correct': i == 1,
    })
