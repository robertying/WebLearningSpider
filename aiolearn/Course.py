import re
import asyncio
from datetime import datetime
from .Message import Message
from .File import File
from .Work import Work
from .Info import Info
from .config import (
    _COURSE_WORK, _COURSE_MSG, _COURSE_FILES, _COURSE_INFO, _COURSE_INFO_NEW,
    _COURSE_MSG_NEW, _COURSE_WORK_NEW, _COURSE_FILE_NEW,
    _URL_PREF, _ID_COURSE_URL, _PAGE_FILE, _PAGE_MSG)
from bs4 import Comment


def parseStamp(stamp):
    return datetime.fromtimestamp(int(stamp) / 1000).strftime('%Y-%m-%d')


class Course:

    def __init__(self, user, id, name=None, url=None, is_new=False):
        self.id = id
        self.name = name
        self.user = user
        self.is_new = is_new
        if url is None:
            self.url = _ID_COURSE_URL % id
        else:
            self.url = url

    @property
    async def works(self):
        async def get_work(item):
            tds = item.find_all('td')
            url = _URL_PREF + item.find('a')['href']
            ids = re.findall(r'id=(\d+)', url)
            id = ids[0]
            course_id = ids[1]
            title = item.find('a').contents[0]
            start_time = tds[1].contents[0]
            end_time = tds[2].contents[0]
            submitted = ("已经提交" in tds[3].contents[0])
            graded = not tds[5].contents[3].attrs.get('disabled')
            completion = 2 if graded else (1 if submitted else 0)
            return Work(
                user=user,
                id=id,
                course_id=course_id,
                title=title,
                url=url,  # deferred fetch
                start_time=start_time,
                end_time=end_time,
                completion=completion
            )

        async def get_work_new(item):
            info = item['courseHomeworkInfo']
            record = item['courseHomeworkRecord']

            return Work(
                user=user,
                id=info['homewkId'],
                course_id=info['courseId'],
                title=info['title'],
                detail_new=info['detail'],
                start_time=parseStamp(info['beginDate']),
                end_time=parseStamp(info['endDate']),
                completion=int(record['status'])
            )

        user = self.user
        if not self.is_new:
            works_url = _COURSE_WORK % self.id
            works_soup = await self.user.make_soup(works_url)
            tasks = [get_work(i) for i
                     in works_soup.find_all('tr', class_=['tr1', 'tr2'])]
        else:
            works_url = _COURSE_WORK_NEW % self.id
            works_json = await self.user.cook_json(works_url)
            tasks = [get_work_new(i) for i in works_json['resultList']]
        works = await asyncio.gather(*tasks)
        return works

    @property
    async def messages(self):
        async def get_message(item):
            tds = item.find_all('td')
            title = tds[1].contents[1].text
            url = _PAGE_MSG % tds[1].contents[1]['href']
            ids = re.findall(r'id=(\d+)', url)
            id = ids[0]
            course_id = ids[1]
            date = tds[3].text
            return Message(
                user=user,
                id=id,
                course_id=course_id,
                title=title,
                url=url,  # deffered fetch
                date=date
            )

        async def get_message_new(item):
            notice = item['courseNotice']
            return Message(
                user=user,
                id=notice['id'],
                course_id=notice['courseId'],
                title=notice['title'],
                detail_new=notice['detail'],
                date=notice['regDate']
            )

        user = self.user
        if not self.is_new:
            msg_url = _COURSE_MSG % self.id
            msg_soup = await self.user.make_soup(msg_url)
            tasks = [get_message(i) for i in msg_soup.find_all(
                'tr', class_=['tr1', 'tr2'])]
        else:
            msg_url = _COURSE_MSG_NEW % self.id
            msg_json = await self.user.cook_json(msg_url)
            tasks = [get_message_new(i)
                     for i in msg_json['paginationList']['recordList']]
        messages = await asyncio.gather(*tasks)
        return messages

    @property
    async def files(self):
        async def get_file(item):
            name, id = re.search(r'getfilelink=([^&]+)&id=(\d+)', str(
                item.find(text=lambda text: isinstance(text, Comment)))).groups()
            a = item.find('a')
            url = _PAGE_FILE % (self.id, name)
            title = re.sub(r'[\n\r\t ]', '', a.contents[0])
            name = re.sub(r'_[^_]+\.', '.', name)
            return File(
                user=user,
                id=id,
                name=name,
                url=url,
                title=title,
                size=0,  # TODO
                date=0  # TODO
            )

        async def get_file_new(item):
            res = item['resourcesMappingByFileId']
            return File(
                user=user,
                id=res['fileId'],
                name=res['fileName'],
                title=item['title'],
                size=res['fileSize'],
                date=res['regDate']
            )

        user = self.user
        if (not self.is_new):
            file_url = _COURSE_FILES % self.id
            files_soup = await self.user.make_soup(file_url)
            tasks = [get_file(item) for item in files_soup.find_all(
                'tr', class_=['tr1', 'tr2'])]
        else:
            file_url = _COURSE_FILE_NEW % self.id
            files_json = await self.user.cook_json(file_url)

            def first_value(dict):
                return next(iter(dict.values()))
            tasks = [get_file_new(item) for item in
                     first_value(
                first_value(
                    files_json['resultList']
                )['childMapData']
            )['courseCoursewareList']
            ]
        files = await asyncio.gather(*tasks)
        return files

    @property
    def dict(self):
        d = self.__dict__.copy()
        user = self.user.__dict__.copy()
        del user['session']
        d['user'] = user
        return d

    @property
    async def info(self):
        async def get_info(item):
            tds = item.find_all('td')
            cid = tds[6].text.replace(" ", "")
            course_id = tds[4].text.replace(" ", "")
            name = tds[8].text.replace(" ", "")
            credit = tds[10].text.replace(" ", "")
            studyTime = tds[12].text.replace(" ", "")
            textbook = tds[27].text.replace(" ", "")
            referenceBook = tds[29].text.replace(" ", "")
            examKind = tds[31].text.replace(" ", "")
            intro = tds[33].text.replace(" ", "")
            teacher = tds[19].text.replace("\xa0", "")

            return Info(
                user=user,
                name=name,
                cid=cid,
                course_id=course_id,
                credit=credit,
                studyTime=studyTime,
                textbook=textbook,
                referenceBook=referenceBook,
                examKind=examKind,
                intro=intro,
                teacher=teacher
            )

        async def get_info_new(item):
            teacher = item["resultList"]["teacherInfo"]["name"]
            # fetch whatever you want from json file and initialize Info object with them
            return Info(
                user="",
                name="name",
                cid="cid",
                course_id="course_id",
                credit="credit",
                studyTime="studyTime",
                textbook="textbook",
                referenceBook="referenceBook",
                examKind="examKind",
                intro="intro",
                teacher=teacher
            )

        user = self.user
        if not self.is_new:
            info_url = _COURSE_INFO % self.id
            info_soup = await self.user.make_soup(info_url)
            info = await get_info(info_soup)
        else:
            info_url = _COURSE_INFO_NEW % self.id
            info_json = await self.user.cook_json(info_url)
            info = await get_info_new(info_json)

        return info
