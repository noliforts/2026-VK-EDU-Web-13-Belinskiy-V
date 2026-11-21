import random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag

RANKS = ['прохожий', 'завсегдатай', 'дед курилки', 'новичок', 'бывалый']


class Command(BaseCommand):
    help = 'Наполнение базы тестовыми данными через Faker и bulk_create'

    def add_arguments(self, parser):
        parser.add_argument(
            'ratio',
            nargs='?',
            type=int,
            default=10,
            help='Коэффициент заполнения сущностей (пользователи: ratio, вопросы: ratio*10, ответы: ratio*100, теги: ratio, оценки: ratio*200)',
        )

    def handle(self, *args, **options):
        ratio = options['ratio']
        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        self.stdout.write(
            f'Начало генерации данных (ratio={ratio}): '
            f'пользователей={num_users}, вопросов={num_questions}, ответов={num_answers}, '
            f'тегов={num_tags}, оценок={num_likes}...'
        )

        fake = Faker('ru_RU')
        # Предварительный пул фраз из Faker: в сотни раз ускоряет генерацию сотен тысяч объектов
        titles_pool = [fake.sentence(nb_words=6).rstrip('.') + '?' for _ in range(300)]
        texts_pool = [fake.paragraph(nb_sentences=4) for _ in range(300)]
        words_pool = list({fake.word() for _ in range(500)})

        # 1. Теги
        self.stdout.write('Генерация тегов...')
        existing_tags_count = Tag.objects.count()
        tags = [
            Tag(name=f'{random.choice(words_pool)}_{existing_tags_count + i}')
            for i in range(num_tags)
        ]
        Tag.objects.bulk_create(tags, batch_size=5000, ignore_conflicts=True)
        tag_ids = list(Tag.objects.values_list('id', flat=True))

        # 2. Пользователи и профили
        self.stdout.write('Генерация пользователей...')
        existing_users_count = User.objects.count()
        # Хэшируем пароль один раз, чтобы не грузить CPU на миллионах итераций PBKDF2
        hashed_password = make_password('password123')

        user_batch_size = 5000
        created_user_ids = []
        for start_idx in range(0, num_users, user_batch_size):
            chunk = min(user_batch_size, num_users - start_idx)
            users_chunk = [
                User(
                    username=f'user_{existing_users_count + start_idx + i}',
                    email=f'user_{existing_users_count + start_idx + i}@qurilka.ru',
                    password=hashed_password,
                )
                for i in range(chunk)
            ]
            created_users = User.objects.bulk_create(users_chunk, batch_size=user_batch_size)
            if created_users and created_users[0].id is not None:
                created_user_ids.extend([u.id for u in created_users])
            else:
                created_user_ids.extend(
                    list(User.objects.order_by('-id')[:chunk].values_list('id', flat=True))
                )

        profiles = [
            Profile(user_id=uid, rank=random.choice(RANKS))
            for uid in created_user_ids
        ]
        Profile.objects.bulk_create(profiles, batch_size=5000, ignore_conflicts=True)

        user_ids = list(User.objects.values_list('id', flat=True))

        # 3. Вопросы
        self.stdout.write('Генерация вопросов...')
        q_batch_size = 5000
        created_question_ids = []
        for start_idx in range(0, num_questions, q_batch_size):
            chunk = min(q_batch_size, num_questions - start_idx)
            questions_chunk = [
                Question(
                    author_id=random.choice(user_ids),
                    title=random.choice(titles_pool),
                    text=random.choice(texts_pool),
                    rating=random.randint(0, 50),
                )
                for _ in range(chunk)
            ]
            created_questions = Question.objects.bulk_create(questions_chunk, batch_size=q_batch_size)
            if created_questions and created_questions[0].id is not None:
                created_question_ids.extend([q.id for q in created_questions])
            else:
                created_question_ids.extend(
                    list(Question.objects.order_by('-id')[:chunk].values_list('id', flat=True))
                )

        # Привязка тегов к вопросам через промежуточную таблицу (M2M bulk insert)
        self.stdout.write('Привязка тегов к вопросам...')
        through_model = Question.tags.through
        through_records = []
        for q_id in created_question_ids:
            picked_tags = random.sample(tag_ids, min(3, len(tag_ids)))
            for t_id in picked_tags:
                through_records.append(through_model(question_id=q_id, tag_id=t_id))
            if len(through_records) >= 10000:
                through_model.objects.bulk_create(through_records, batch_size=5000, ignore_conflicts=True)
                through_records = []
        if through_records:
            through_model.objects.bulk_create(through_records, batch_size=5000, ignore_conflicts=True)

        question_ids = list(Question.objects.values_list('id', flat=True))

        # 4. Ответы
        self.stdout.write('Генерация ответов...')
        ans_batch_size = 10000
        created_answer_ids = []
        for start_idx in range(0, num_answers, ans_batch_size):
            chunk = min(ans_batch_size, num_answers - start_idx)
            answers_chunk = [
                Answer(
                    question_id=random.choice(question_ids),
                    author_id=random.choice(user_ids),
                    text=random.choice(texts_pool),
                    is_correct=(random.random() < 0.1),
                    rating=random.randint(0, 30),
                )
                for _ in range(chunk)
            ]
            created_answers = Answer.objects.bulk_create(answers_chunk, batch_size=5000)
            if created_answers and created_answers[0].id is not None:
                created_answer_ids.extend([a.id for a in created_answers])
            else:
                created_answer_ids.extend(
                    list(Answer.objects.order_by('-id')[:chunk].values_list('id', flat=True))
                )

        answer_ids = list(Answer.objects.values_list('id', flat=True))

        # 5. Оценки (лайки)
        self.stdout.write('Генерация оценок...')
        num_qlikes = num_likes // 2
        num_alikes = num_likes - num_qlikes

        like_batch_size = 10000
        for _ in range(0, num_qlikes, like_batch_size):
            chunk = min(like_batch_size, num_qlikes)
            qlikes = [
                QuestionLike(
                    user_id=random.choice(user_ids),
                    question_id=random.choice(question_ids),
                    value=random.choice([1, -1]),
                )
                for _ in range(chunk)
            ]
            QuestionLike.objects.bulk_create(qlikes, batch_size=5000, ignore_conflicts=True)

        for _ in range(0, num_alikes, like_batch_size):
            chunk = min(like_batch_size, num_alikes)
            alikes = [
                AnswerLike(
                    user_id=random.choice(user_ids),
                    answer_id=random.choice(answer_ids),
                    value=random.choice([1, -1]),
                )
                for _ in range(chunk)
            ]
            AnswerLike.objects.bulk_create(alikes, batch_size=5000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'Успешно сгенерированы данные с ratio={ratio}!'))
