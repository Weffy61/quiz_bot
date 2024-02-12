import random


def get_questions(file_path):
    with open(file_path, 'r', encoding='KOI8-R') as file:
        file_content = file.read()

    split_content = file_content.split('\n\n')
    questions = {}

    for content in split_content[3:]:
        if 'Вопрос' in content:
            question_title, question = content.split(':\n')
            answer_title, answer = split_content[split_content.index(content) + 1].split(':\n')
            questions[question] = answer.replace("\n", " ").rstrip(' ')

        elif content in ('Автор', 'Источник', 'Ответ'):
            continue
    return questions


def get_random_question(questions):
    question, answer = random.choice(list(questions.items()))
    if '.' in answer:
        answer = answer.split('.')[0]
    if '(' in answer:
        answer = answer.split('(')[0]
    return question, answer



