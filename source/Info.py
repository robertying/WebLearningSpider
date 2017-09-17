import re


class Info:

    def __init__(self, user, cid, course_id, name, credit, studyTime, textbook,
                 referenceBook, examKind, teacher, intro='', url=None):

        self.user = user
        self.name = name
        self.cid = cid
        self.course_id = course_id
        self.credit = credit
        self.studyTime = studyTime
        self.textbook = textbook
        self.referenceBook = referenceBook
        self.examKind = examKind
        if intro is None:
            self.intro = ''
        else:
            self.intro = intro
        self.teacher = teacher
        self.url = url
