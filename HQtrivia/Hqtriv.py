import datetime
import nltk

import pytesseract
import pyscreenshot as ImageGrab

from multiprocessing import Pool as ThreadPool
from PIL import Image

from googleapiclient.discovery import build
# AIzaSyBbPdJw412ccxgjV7pGrgeHr1dSmQxhdGU - bysorynyos@gmail.com
# cx - 018164122682344646569:wc9xki-vvnm

# AIzaSyDEheOURUxGxg0ikEoozwSih3gltFs06wM - sorin.ionut.bajenaru@gmail.com
# cx - 013791422782072695689:-qvygz_-ybe

SERVICE = build("customsearch", "v1", developerKey="AIzaSyDEheOURUxGxg0ikEoozwSih3gltFs06wM")

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'

ALLOWED_POS = ["CD", "JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "RBS", "RP", "VB", "VBD", "VBZ", "VBG", "WRB"]


def isAllowedPOS(word):
    if ALLOWED_POS.__contains__(word):
        return True
    return False


def cleanQuestion(question):
    finalString = ""

    question_token = nltk.word_tokenize(question)
    question = nltk.pos_tag(question_token)

    #print()
    #print(question_token)
    #print(question)
    #print()

    for idx, word in enumerate(question):
        if (isAllowedPOS(question[idx][1]) and  len(question[idx][0]) > 1):
            finalString = finalString + " " + question[idx][0]
    return finalString


def cleaner(text):
    text = text.replace('\n', ' ')
    text = text.replace("'", "")
    text = text.replace(".", "")
    text = text.replace(",", "")
    text = text.replace("-", "")
    text = text.replace("_", "")
    text = text.replace(":", "")
    text = text.replace("!", "")
    text = text.replace("?", "")
    return text


def removeLines(text):
    text = text.replace("'", "")
    text = text.replace('"', "")

    lastchar = 0
    newtext = ""

    for char in text:
        curentchar = 0

        if (char == '\n' or char == ' ' or char == '\t' or char == '\r'):
            curentchar = 1

        if (curentchar == 1 and lastchar == 0):
            newtext = newtext + char
            lastchar = 1
        else:
            if (curentchar == 0 and lastchar == 1):
                newtext = newtext + char
                lastchar = 0
            else:
                if (curentchar == 0 and lastchar == 0):
                    newtext = newtext + char

    newtext = newtext + '\n'
    return newtext


def processImage(imagName):
    img = Image.open(imagName)
    #img = Image.open('tests\hqtest.jpg')
    result = pytesseract.image_to_string(img, lang='eng', config=tessdata_dir_config)

    result = removeLines(result)
    #print()
    #print(result)
    questionMark = result.find("?")
    holder = "\n"

    space_one = result.index(holder, questionMark)
    space_two = result.index(holder, space_one + 1)
    space_three = result.index(holder, space_two + 1)

    option_a = result[space_one:space_two]
    option_b = result[space_two:space_three]
    option_c = result[space_three:]
    question = result[:questionMark]

    question = cleaner(question)
    option_a = cleaner(option_a)
    option_b = cleaner(option_b)
    option_c = cleaner(option_c)

    print("question = " + question)
    print("option a: " + option_a)
    print("option b: " + option_b)
    print("option c: " + option_c)

    question = cleanQuestion(question)
    #print("parsed q: " + question)
    #print()

    performSearch(question, option_a, option_b, option_c)


def performSearch(question, option_a, option_b, option_c):
    a_hits = 0
    b_hits = 0
    c_hits = 0

    inputs = [question + option_a, question + option_b, question + option_c]
    options = [option_a, option_b, option_c]

    #print(inputs)
    #print(options)
    #print()

    pool = ThreadPool(4)

    googleResults = pool.map(googleSearch, inputs)
    frontPageSnippets = frontPageHitsSnips(question)

    pool.close()
    pool.join()

    #print()
    #print(googleResults)
    #print(frontPageSnippets)
    #print()

    for idx in range(len(frontPageSnippets)):
        if (frontPageSnippets[idx].find(str(option_a).strip()) != -1):
            a_hits = a_hits + 1
        elif (frontPageSnippets[idx].find(str(option_b).strip()) != -1):
            b_hits = b_hits + 1
        elif (frontPageSnippets[idx].find(str(option_c).strip()) != -1):
            c_hits = c_hits + 1
    frontHits = [a_hits, b_hits, c_hits]
    printAnswer(googleResults, options, frontHits)


def frontPageHitsSnips(query):
    snippets = []
    res = SERVICE.cse().list(q=query, cx='013791422782072695689:-qvygz_-ybe').execute()
    for idx in range(0, 10):
        snippets.append(str(res['items'][idx]['snippet']))
    return snippets


def googleSearch(query):
    res = SERVICE.cse().list(q=query, cx='013791422782072695689:-qvygz_-ybe').execute()
    return int(res['searchInformation']['totalResults'])


def printAnswer(google, options, frontPage):
    num_a = google[0]
    num_b = google[1]
    num_c = google[2]

    front_a = frontPage[0]
    front_b = frontPage[1]
    front_c = frontPage[2]

    print("A ===== " + str(num_a) + "  hits = " + str(front_a))
    print("B ===== " + str(num_b) + "  hits = " + str(front_b))
    print("C ===== " + str(num_c) + "  hits = " + str(front_c))

    winnerF = max(front_a, front_b, front_c)
    winnerV = max(num_a, num_b, num_c)

    if (winnerF == 0):
        if (winnerV == num_a):
            answer = str(options[0])
        elif (winnerV == num_b):
            answer = str(options[1])
        else:
            answer = str(options[2])
    else:
        if (winnerF == front_a):
            answer = str(options[0])
        elif (winnerF == front_b):
            answer = str(options[1])
        else:
            answer = str(options[2])

    print("**************************************************" + "\nANSWER = " + answer + "\n**************************************************")


def main():
    image = ImageGrab.grab(bbox=(900, 300, 1300, 730))  # X1,Y1,X2,Y2
    #image = ImageGrab.grab(bbox=(770, 330, 1150, 740))  # X1,Y1,X2,Y2
    imageName = "scr" + datetime.datetime.now().strftime("%d_%m_%H_%M_%S") + ".png"
    image.save(imageName)
    processImage(imageName)


if __name__ == '__main__':
    main()

