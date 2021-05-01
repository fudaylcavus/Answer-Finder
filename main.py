from selenium import webdriver
import time
import sys


answer_count = 0


def search_in_google(driver, query):
    url = 'http://www.google.com/search?q=' + query
    driver.get(url)


def get_google_results(driver, priority):
    result_links = driver.find_elements_by_class_name('yuRUbf')
    result_names = driver.find_elements_by_xpath(
        '//*[@id="rso"]/*/*/*/*/*/*/*/div/div/div[1]/a/h3')
    # First result best for us if there's no result including our priority
    selected_links = result_links[0]
    if priority:
        for i in range(len(result_links)):
            if priority in result_links[i].text:
                selected_links = result_links[i]
                break
    selected_links.click()


def find_answer_in_quizlet(driver, questions, min_match_rate, check_every_question):
    # quizlet not loading content before scroll
    driver.execute_script("window.scrollBy(0, document.body.clientHeight/2.3)")
    driver.execute_script(
        'document.getElementById("TopNavigationReactTarget").style.display = "none"'
    )
    driver.execute_script(
        'document.querySelector(\'div[class*="SetPageStickyHeader"]\').style.display = "none"'
    )
    time.sleep(.4)
    quizletCards = driver.find_elements_by_css_selector(
        'div[aria-label="Term"]')
    return find_and_save(quizletCards, questions, min_match_rate, check_every_question)


def find_answer_in_brainscape(driver, questions, min_match_rate, check_every_question):
    questionCards = driver.find_elements_by_css_selector(
        'section[itemtype="http://schema.org/Question"]')
    return find_and_save(questionCards, questions, min_match_rate, False)


def clean_answer(answer):
    return answer.replace("\n", " ")


def match_rate(answer, query):
    maxSimilarityRate = 0
    answer = clean_answer(answer)
    for i in range(len(answer)):
        similarity = 0
        for j in range(len(query)):
            if i + j >= len(answer):
                break
            if answer[i+j] == query[j]:
                similarity += 1
        if similarity > maxSimilarityRate:
            maxSimilarityRate = similarity

    percentage = maxSimilarityRate / len(query) * 100
    # print(f"[{percentage:.2f}%]")
    return percentage


def find_and_save(possible_answers, questions, min_match_rate, check_every_question):
    global answer_count
    found_indexes = []
    match_rates_by_index = [0 for i in range(len(questions))]
    for answer in possible_answers:
        # this is exam so any other question's solution might also be in the same page.
        for i in range(len(questions)):
            if not check_every_question and i >= 1:
                break
            match_rates_by_index[i] = match_rate(answer.text, questions[i])

        highest_rate_index = match_rates_by_index.index(
            max(match_rates_by_index))

        if match_rates_by_index[highest_rate_index] >= min_match_rate:
            if (highest_rate_index not in found_indexes):
                found_indexes.append(highest_rate_index)
                answer_count += 1
                with open(f"./Answers/answer{answer_count}.png", "wb") as f:
                    f.write(answer.screenshot_as_png)

    return found_indexes


def run_copy_system(driver, questions, priority, min_match_rate, check_every_question):
    function_for_website = {"quizlet": find_answer_in_quizlet,
                            "brainscape": find_answer_in_brainscape}
    while 0 != len(questions):
        search_in_google(driver, questions[0])
        get_google_results(driver, priority)
        current_url = driver.current_url
        func_will_used = None

        for website in function_for_website:
            if website in current_url:
                func_will_used = function_for_website[website]

        if func_will_used:
            indexes_will_removed = func_will_used(
                driver, questions, min_match_rate, check_every_question)

        for j in range(len(indexes_will_removed)):
            # every time when I pop something, values higher than jth element will shift to 1 index left.
            for k in range(len(indexes_will_removed)):
                if indexes_will_removed[k] > indexes_will_removed[j]:
                    indexes_will_removed[k] -= 1
            questions.pop(indexes_will_removed[j])


def read_questions(file):
    questions = []
    with open(file, "r") as f:
        for line in f.readlines():
            questions.append(line.strip())
    return questions


def setup():
    # Example args: main.py -mr 80 -sw True -qf questions.txt -p quizlet
    question_file = None
    same_website_search = False
    minimum_match_rate = 70
    priority = "quizlet"
    wrong_arguments = False
    questions = []

    # PATH/TO/ADBLOCK/MAKES/APLICATION/FASTER/
    ADBLOCK_PATH = "C:\\Users\\fuday\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions\\gighmmpiobklfepjocnamgkkbiglidom\\4.32.1_0"

    chr_profile = webdriver.ChromeOptions()
    if ADBLOCK_PATH:
        chr_profile.add_argument(f"load-extension={ADBLOCK_PATH}")

    for i in range(len(sys.argv)):
        if i + 1 >= len(sys.argv):
            break

        current_arg = str(sys.argv[i]).strip()
        next_arg = str(sys.argv[i+1]).strip()

        if current_arg == "-sw":
            if next_arg == "True":
                same_website_search = True
            elif next_arg == "False":
                same_website_search = False
            else:
                wrong_arguments = True

        if current_arg == "-qf":
            if not next_arg.endswith(".txt"):
                wrong_arguments = True
            else:
                question_file = next_arg

        if current_arg == "-mr":
            try:
                minimum_match_rate = int(next_arg)
            except:
                wrong_arguments = True

        if current_arg == "-p":
            if next_arg == "quizlet":
                priority = "quizlet"
            elif next_arg == "brainscape":
                priority = "brainscape"
            else:
                wrong_arguments = True

    if wrong_arguments:
        print("One or more arguments are given wrong! Please check the usage in README.md")
        exit()

    if question_file:
        questions = read_questions(question_file)
    else:
        print("Enter the questions line by line, once they done type END to the new line")
        while True:
            inputline = input("new input: ").strip()
            if inputline == "END":
                break
            else:
                questions.append(inputline)

    driver = webdriver.Chrome(options=chr_profile)
    return (driver, questions, priority, minimum_match_rate, same_website_search)


def main():
    driver, questions, priority, minimum_match_rate, same_website_search = setup()
    run_copy_system(driver, questions, priority,
                    minimum_match_rate, same_website_search)
    driver.close()
    # print(f"{answer_count}/{} answers found!")


main()
time.sleep(1000)
