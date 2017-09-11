import asyncio
import getpass
from context import aiolearn


async def main():
    user = aiolearn.User(username=input('Input username: '),
                         password=getpass.getpass("Input password: "))
    user = aiolearn.User(username='yingr16', password='$lBqczk100ndbddT')
    semester = aiolearn.Semester(user, when="all")
    courses = await semester.courses

    for course in courses:
        info = await course.info
        print(course.name + ' ' + info.teacher)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
