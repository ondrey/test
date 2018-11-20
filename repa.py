# -*- coding: utf-8 -*-
import argparse, sys, codecs
from Resource import Resource


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Repa 1.0", description=u"Анализ репозитория github.com.")

    parser.add_argument('-r', dest='repo', metavar=u"URL репозитория на github.", type=Resource.parser_url, required=True)
    parser.add_argument('-s', dest='since', metavar=u"Дата начала анализа. Формат ДД.ММ.ГГГГ", type=Resource.parser_date)
    parser.add_argument('-u', dest='until', metavar=u"Дата окончания анализа. Формат ДД.ММ.ГГГГ", type=Resource.parser_date)
    parser.add_argument('-sh', dest='sha', metavar=u"Ветка репозитория. (master)", default='master')
    parser.add_argument('-t', dest='access_token', metavar=u"Токен, 5к запросов в час, иначе 60шт.")
    parser.add_argument('-f', dest='file', metavar=u"Вывод в файл")

    namespace = parser.parse_args()
    if namespace.file:
        sys.stdout = codecs.open(namespace.file, 'w', "utf-8")

    res_git = Resource('https://api.github.com/', namespace)

    sys.stdout.write(u'\n\tАКТИВНЫЕ УЧАСТНИКИ:\n')

    sys.stdout.write(u'\tКол-во:\t|Логин:\n')

    for login, cnt_comm in res_git.get_commits(30):
        sys.stdout.write(u'\t{1}\t|{0}\n'.format(login, cnt_comm))
    sys.stdout.write(u'\tВсего {0} коммитов.\n'.format(res_git.count_commits))

    pull_req = res_git.get_info(30, 'pulls')
    sys.stdout.write(u'\n\tPULL REQUESTS:\n')
    sys.stdout.write(u'\tКол-во:\t|Тип:\n')
    sys.stdout.write(u'\t{0}\t|Открыто\n'.format(pull_req['open']))
    sys.stdout.write(u'\t{0}\t|Закрыто\n'.format(pull_req['closed']))
    sys.stdout.write(u'\t{0}\t|Старше 30 дней\n'.format(pull_req['old']))

    issues = res_git.get_info(14, 'issues')
    sys.stdout.write(u'\n\tISSUES:\n')
    sys.stdout.write(u'\tКол-во:\t|Тип:\n')
    sys.stdout.write(u'\t{0}\t|Открыто\n'.format(issues['open']))
    sys.stdout.write(u'\t{0}\t|Закрыто\n'.format(issues['closed']))
    sys.stdout.write(u'\t{0}\t|Старше 14 дней\n'.format(issues['old']))
