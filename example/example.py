import asyncio
import getpass
import pymongo
from pymongo import MongoClient
from context import aiolearn


async def main():
    user = aiolearn.User(username=input('Input username: '),
                         password=getpass.getpass("Input password: "))

    client = MongoClient()
    db = client.courseDB
    courseInfo = db.courseInfo

    semester = aiolearn.Semester(user, when="all")
    courses = await semester.courses

    for course in courses:
        teacher = await course.teacher
        info = await course.info
        print(course.name + ' ' + teacher.teacherName + '\n' + info.intro + '\n')
        c = {
            'courseName':course.name,
            'teacherName':info.teacher,
        }
       # courseInfo.insert_one(c)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
