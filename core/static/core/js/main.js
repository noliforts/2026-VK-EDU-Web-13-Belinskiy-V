function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    const csrftoken = getCookie('csrftoken');

    // 1. AJAX Лайки и дизлайки
    document.querySelectorAll('.vote-btn').forEach((btn) => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const ratingContainer = btn.closest('.rating');
            if (!ratingContainer) return;

            const target = ratingContainer.dataset.target || 'question';
            const itemId = ratingContainer.dataset.id;
            const voteType = btn.dataset.vote;

            const url = target === 'question' 
                ? `/question/${itemId}/vote/` 
                : `/answer/${itemId}/vote/`;

            try {
                const formData = new FormData();
                formData.append('type', voteType);

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                    },
                    body: formData,
                });

                if (response.status === 401) {
                    alert('Войдите на сайт, чтобы голосовать!');
                    return;
                }

                const data = await response.json();
                if (response.ok && data.status === 'ok') {
                    const valSpan = ratingContainer.querySelector('.rating-value');
                    if (valSpan) {
                        valSpan.textContent = data.new_rating;
                    }
                    // Переключаем активный класс
                    const wasActive = btn.classList.contains('active');
                    ratingContainer.querySelectorAll('.vote-btn').forEach(b => b.classList.remove('active'));
                    if (!wasActive) {
                        btn.classList.add('active');
                    }
                } else {
                    alert(data.error || 'Ошибка при сохранении оценки.');
                }
            } catch (err) {
                console.error(err);
                alert('Не удалось отправить голос. Проверьте соединение.');
            }
        });
    });

    // 2. AJAX Выбор правильного ответа
    document.querySelectorAll('.correct-answer-checkbox').forEach((checkbox) => {
        checkbox.addEventListener('change', async () => {
            const questionId = checkbox.dataset.questionId;
            const answerId = checkbox.dataset.answerId;
            const url = `/question/${questionId}/correct_answer/`;

            try {
                const formData = new FormData();
                formData.append('answer_id', answerId);

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                    },
                    body: formData,
                });

                if (response.status === 401) {
                    alert('Войдите на сайт!');
                    checkbox.checked = !checkbox.checked;
                    return;
                }
                if (response.status === 403) {
                    alert('Только автор вопроса может выбирать верный ответ!');
                    checkbox.checked = !checkbox.checked;
                    return;
                }

                const data = await response.json();
                if (response.ok && data.status === 'ok') {
                    // Снимаем выбор со всех остальных ответов
                    document.querySelectorAll('.correct-answer-checkbox').forEach((cb) => {
                        if (cb !== checkbox) cb.checked = false;
                    });
                    checkbox.checked = data.is_correct;
                } else {
                    alert(data.error || 'Ошибка при изменении статуса ответа.');
                    checkbox.checked = !checkbox.checked;
                }
            } catch (err) {
                console.error(err);
                alert('Ошибка соединения.');
                checkbox.checked = !checkbox.checked;
            }
        });
    });
});
