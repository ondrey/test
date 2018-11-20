# -*- coding: utf-8 -*-
import sys, urllib2, urllib, json
from datetime import datetime


class Resource():
    def __init__(self, host, namespace=None):
        self.host = host
        self.namespace = namespace
        self.count_commits = 0
        self.access_token = namespace.access_token

    def get_res(self, res_tmp, res_prms={}, url_prms={}):
        """
        Выполнить GET запрос к API
        :param res_tmp: шаблон запроса GET, например /orgs/octokit/repos
        :param res_prms: Параметры будут подставленны в шаблон. Например get('/orgs/octokit/{command}', {'command':'repos'})
        :param url_prms: Параметры, будут добавлены URL после знака "?"
        :return: json
        """
        if self.access_token:
            url_prms.update({'access_token': self.access_token})

        urlful = self.urljoin(self.host, res_tmp.format(**res_prms))
        urlful += '?{0}'.format(urllib.urlencode(url_prms))

        json_obj = json.load(urllib2.urlopen(urlful))
        if "message" in json_obj:
            raise NameError(u"Неожиданный ответ {0}".format(json_obj['message']))

        return json_obj

    @staticmethod
    def urljoin(*args):
        return '/'.join(map(lambda x: x.replace('\\', '/').strip('/'), args))

    @staticmethod
    def parser_date(date_str):
        return datetime.strptime(date_str, '%d.%m.%Y')

    @staticmethod
    def parser_url(rep_url):
        url_parce = Resource.urljoin(rep_url).split('/')

        if len(url_parce) >= 2:
            return url_parce[-2:]

        raise ValueError("Incorrect repository URL. {0}".format(rep_url))

    def get_commits(self, cnt=30):
        """
        Активность участников разработки, анализ на основе истории комитов.

        GET /repos/:owner/:repo/commits

        :param cnt: Количество элементов для отображения
        :return:
        """
        sys.stdout.write(u'\t')
        commits = []
        page = 1
        while True:
            result = self.get_res("repos/{owner}/{repo}/commits",
                res_prms={'owner': self.namespace.repo[0], 'repo': self.namespace.repo[1]},
                url_prms=dict(
                    page=page,
                    per_page=100,  # Количество элементов на странице, максимум 100
                    since=self.namespace.since.strftime("%Y-%m-%dT00:00:00Z") if self.namespace.since else None,
                    until=self.namespace.until.strftime("%Y-%m-%dT23:59:59Z") if self.namespace.until else None,
                    sha=self.namespace.sha))

            if len(result) == 0:
                break
            else:
                commits += result
                page += 1
                sys.stdout.write('.')

        commits_login = {}
        for i in commits:
            self.count_commits +=1
            if i[u'author']:
                if i[u'author'][u'login'] not in commits_login:
                    commits_login[i[u'author'][u'login']] = 1
                else:
                    commits_login[i[u'author'][u'login']] += 1

        s_commits_login = commits_login.items()
        s_commits_login.sort(key=lambda x: x[1], reverse=True)
        del commits_login
        sys.stdout.write(u'\n')
        return s_commits_login[-cnt:]

    def get_info(self, age_max=30, command=None):
        """
        Получить информацию по кол-ву issues or pull request

        GET /repos/:owner/:repo/issues
        GET /repos/:owner/:repo/pulls

        :param age_max: Ограничение по возрасту, в днях. Для определения стариков
        :param command: 'issues' or 'pulls'
        :return:
        """

        sys.stdout.write(u'\t')
        all = []
        page = 1
        while True:
            result = self.get_res("repos/{owner}/{repo}/{comm}",
                res_prms={'owner': self.namespace.repo[0], 'repo': self.namespace.repo[1], 'comm': command},
                url_prms=dict(
                    page=page,
                    per_page=100,  # Количество элементов на странице, максимум 100
                    state='all'))

            if len(result) == 0:
                break
            else:
                all += result
                page += 1
                sys.stdout.write('.')

        info = {'open': 0, 'closed': 0, 'old': 0}

        for i in all:
            if i['state'] in info:
                info[i['state']] += 1
                age = datetime.now() - datetime.strptime(i['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                if age.days >= age_max and i['state'] == 'open':
                    info['old'] += 1

        return info