import argparse


def parse_question_path():
    parser = argparse.ArgumentParser(
        description='Запуск бота викторины'
    )
    parser.add_argument('-p', '--path', help='Путь к файлу с вопросами', default='questions/1vs1200.txt')
    args = parser.parse_args()
    return args.path