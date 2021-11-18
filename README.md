# Answer-Finder

## Reason why I built this:
About two or more of my teachers were asking from websites,
that we can find the answers with quick search. Then one of my 
friend told me that I should automate it, then I made it, Since I like programming and that kinda funny stuffs :)

This script had found 20/20 solutions of my exams (tested later on)

#### Example Video 
[Click for less than 1 minute, preview video](https://youtu.be/GlEJPl7nWEU)
#### Example Screenshots
Example screenshots are in the `Answers/` folder. It's only scraping the answer related part of the page.

## Executing with system arguments
You can use arguments to use some features otherwise it will use default values.

| argument | value | description | default value
| ------ | ------ | ------ | --- |
| -mr | 1 <= x <= 100 | minimum matching rate to accept results as an answer | 70%
| -sw | True / False | should app search questions in the same website | False
| -qf | direct path to file | specify the path of the question file | None
| -p | quizlet / brainscape | prior website to search results in | quizlet


> Note: CSS/HTML structures of the given websites can change, if that happens script won't work