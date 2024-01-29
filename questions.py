
def get_questions(file_path):
    with open(file_path, 'r', encoding='KOI8-R') as file:
        file_content = file.read()

    split_file = file_content.split('\n\n')
    questions = {}

    for question_number in range(len(split_file))[3:]:
        if 'Вопрос' in split_file[question_number]:
            question_title, question = split_file[question_number].split(':\n')
            answer_title, answer = split_file[question_number + 1].split(':\n')
            questions[question] = answer
        elif 'Автор' in split_file[question_number] or 'Источник' in split_file[question_number] or 'Ответ' in \
                split_file[question_number]:
            continue
    return questions


print(get_questions('questions/1vs1200.txt'))