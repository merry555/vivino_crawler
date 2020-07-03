import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
#import pyautogui as g
import numpy as np
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from multiprocessing import Process, Value, Array, Lock

def crawl(titles:list,lock_print,lock_file):
    driver = webdriver.Chrome('./sel/chromedriver')
    for winename in titles:
        #lock_print.acquire()
        #print('winename:',winename)
        #lock_print.release()

        driver.get('https://www.vivino.com/')
        elem_input = driver.find_element_by_class_name('searchBar__searchInput--2Nf0D')
        elem_input.send_keys(winename)
        elem_input.submit()
        elem_image = driver.find_element_by_class_name('link-color-alt-grey')
        link = elem_image.get_attribute('href')
        driver.get(link)
        driver.implicitly_wait(3)

        body = driver.find_element_by_css_selector('body')
        for i in range(8):
            body.send_keys(Keys.PAGE_DOWN)

        driver.implicitly_wait(4)

        try:
            driver.find_element_by_link_text('Show more reviews').click()
        except:
            lock_print.acquire()
            print('%s is skipped. check ./skipped.txt file'%(winename))
            lock_print.release()

            lock_file.acquire()
            f = open('./skipped.txt','a+')
            f.write(winename+'\n')
            f.close()
            lock_file.release()
            continue
        
        comm_review = driver.find_element_by_class_name('allReviews__header--1AKxx')
        actions = ActionChains(driver)
        actions.move_to_element(comm_review).click().perform()
        
        for i in range(50):
            actions.send_keys(Keys.END).perform()

        data = driver.find_elements_by_class_name('reviewCard__reviewNote--fbIdd')

        l = []
        for d in data:
            l.append(d.text)

        dfWine = pd.DataFrame(np.array(l))
        lock_print.acquire()
        print("winename: %s number of reviews: %d "%(winename,len(dfWine)))
        lock_print.release()

        dfWine.to_csv('./sel/tempoutput/%s.csv'%(winename))


def main():
    df = pd.read_csv('./sel/title_130k_rmYear_lower_sorted.csv')
    names = df['0'].values.tolist()
    nProcess = 1
    procs = []
    lock_print = Lock()
    lock_file = Lock()
    start = 65500
    dist = 500
    for i in range(nProcess):
        p = Process(target=crawl,args=(names[start:start+dist],lock_print,lock_file))
        p.start()
        procs.append(p)
        start += dist
    
    for p in procs:
        p.join()
    
    print('crawling is finished. start:%d end:%d'%(start,dist*nProcess))


if __name__ == "__main__":
    main()