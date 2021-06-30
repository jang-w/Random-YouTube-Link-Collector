from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import random

def getVideos(numRolls):
    with open('words.txt', 'r', encoding='utf-8') as w:
        words = w.readlines()

    fire_options = Options()
    fire_options.add_argument('--headless')
    videosOfDay = []
    videoBrowser = webdriver.Firefox(options=fire_options)
    
    x = 0
    while x < numRolls:
        wordRoll = random.choice(words)
        wordRoll2 = random.choice(words)

        try:
            videoBrowser.get(f'https://youtube.com/results?search_query={wordRoll}+{wordRoll2}+before%3A2012-08-08&safeSearch=moderate') 
            video = videoBrowser.find_elements_by_id('video-title')
            r = random.choice(range(1, len(video) - 1))
            videoTitle = video[r].text
            video[r].click()
            videosOfDay.append(f'{videoTitle} : {videoBrowser.current_url}')
            x += 1 
        except IndexError:
            continue
        except selenium.common.exceptions.ElementNotInteractableException:
            continue
        except selenium.common.exceptions.NoSuchElementException:
            continue
    videoBrowser.close()
    return videosOfDay

print(getVideos(5))
