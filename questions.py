import random


def get_questions(file_path):
    with open(file_path, 'r', encoding='KOI8-R') as file:
        file_content = file.read()

    split_content = file_content.split('\n\n')
    questions = {}

    for question_number in range(len(split_content))[3:]:
        if 'Вопрос' in split_content[question_number]:
            question_title, question = split_content[question_number].split(':\n')
            answer_title, answer = split_content[question_number + 1].split(':\n')
            questions[question] = answer.replace("\n", " ").rstrip(' ')
        elif 'Автор' in split_content[question_number] or 'Источник' in split_content[question_number] or 'Ответ' in \
                split_content[question_number]:
            continue
    return questions


def get_random_question(path):
    questions = get_questions(path)
    question, answer = random.choice(list(questions.items()))
    if '.' in answer:
        answer = answer.split('.')[0]
    if '(' in answer:
        answer = answer.split('(')[0]
    return question, answer



