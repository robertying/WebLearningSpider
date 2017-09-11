[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)]()
# WebLearningSpider
Improved [kehao95](https://github.com/kehao95)'s aiolearn

For fetching data from [Tsinghua WebLearning](http://learn.tsinghua.edu.cn)

清华大学网络学堂爬虫
## Features
- Asynchronous
- Supporting multi-user connections
## Improvements
- Add course info fetching
- Add New WebLearning support
## Example
```python
import asyncio
import getpass
import aiolearn

async def main():
    user = aiolearn.User(username=input('input username'), password=getpass.getpass("input password:"))
    semester = aiolearn.Semester(user, current=False)
    courses = await semester.courses
    for course in courses:
        print(course.name)
        works = await course.works
        messages = await course.messages
        files = await course.files
        info = await course.info
        print('\n>>works')
        for work in works:
            print(work.title)
        print('\n>>messages')
        for message in messages:
            print(message.title)
        print('\n>>files')
        for file in files:
            print(file.name)
        print('\n>>info')
        for i in info:
            print(info.teacher)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
```
## References
- [kehao95/aiolearn](https://github.com/kehao95/aiolearn)