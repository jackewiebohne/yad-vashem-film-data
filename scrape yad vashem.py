import requests
from bs4 import BeautifulSoup
import pandas as pd
import re, math, time, pickle,sys, selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager


start_url = "https://library.yadvashem.org/index.html?language=en&mov=1"
next_page_url = start_url
options = Options()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get(start_url)


def scrape_yv(driver, counter=1, data_list=[], last_print=0, error_links=[]):
    try:
        # in case pop up window is already there
        pop_up_close_button = driver.find_element(By.XPATH, '//button[@class="close modal_close"]')
        pop_up_close_button.click()
    except:
        pass
    try:
        wait = WebDriverWait(driver, 9)
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-click="submit"]')))
        search_button.click()
    except:
        pass
    time.sleep(4)
    if counter > 1:
        print(f'starting at: {counter}')
        input_field = driver.find_element(By.ID, "records-txt-page-num-up")
        input_field.clear()
        input_field.send_keys(str(counter), Keys.ENTER)
    try:
        baselink = 'https://library.yadvashem.org/'
        page_html = driver.page_source
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'see_full_details')))

        # Get the page source after the dynamic content has loaded
        main_page_source = driver.page_source
        mainsoup = BeautifulSoup(main_page_source, 'html.parser')
        item_links = mainsoup.find_all('a', {'class':'see_full_details'})
        total_num_pp = mainsoup.find('span', class_='spn-pages-total').text.strip()
        total_num_pp = int(total_num_pp)
        while counter >= total_num_pp
            if (counter/total_num_pp) >= last_print + 0.05 or counter <= 1 or counter == total_num_pp:
                df = pd.DataFrame(data_list)
                df.to_csv(r'C:\Users\hwx756\Downloads\yad vashem data/yad_vashem_filmdata_' + str(counter) + '.csv', index=False, sep='\t')
                print(f'page no: {counter}; percent progress: {round(counter/total_num_pp,3) * 100}')
                print(f'number of items scraped: {len(data_list)}')
                print(f'number of errors detected: {len(error_links)}')
                data_list = []
                last_print = counter/total_num_pp:
                    return counter, data_list, error_links
                if counter == total_num_pp:
            for item_link in item_links:
                try:
                    full_details_url = item_link['href']
                    # Construct the full URL of the "Full Details" page
                    full_details_url = baselink + full_details_url
                    # Open a new browser window for the "Full Details" page
                    driver.execute_script("window.open('', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])
                    # Visit the "Full Details" page
                    driver.get(full_details_url)
                    time.sleep(1)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))                                        
                    # parse
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    rows = soup.find('tbody').find_all('tr')
                    # iterate over table rows
                    item_data = {}
                    for row in rows:
                        key = row.td.text
                        multiple_ele = row.td.find_next('td').find_all('br')
                        if multiple_ele:
                            val = row.td.find_next('td').get_text(separator=', ').strip()
                        else:
                            val = row.td.find_next('td').text
                        item_data[key] = val
                    data_list.append(item_data)
                    driver.close()
                    # return to original overview page
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    try:
                        while True: # to dismiss repeat alerts
                            alert = driver.switch_to.alert
                            alert.accept()
                            print('(1) dismissing alert')
                            time.sleep(3)
                    except:
                        print(f'unexpected error, skipping item: {item_link}')
                        error_links.append(item_link)
                        try:
                            first_window_handle = driver.window_handles[0]
                            # close all windows except for the first
                            for window_handle in driver.window_handles[1:]:
                                driver.switch_to.window(window_handle)
                                driver.close()
                            driver.switch_to.window(first_window_handle)
                        except:
                            driver.switch_to.window(driver.window_handles[0])
            # Check for pop-up window on main page
            try:
                pop_up_close_button = driver.find_element(By.XPATH, '//button[@class="close modal_close"]')
                pop_up_close_button.click()
            except:
                pass

            # Check for the presence of the "Next" button and click it if available
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@id="next-page-d"]')))
            next_button.click()
            time.sleep(3)
            counter += 1
    except UnexpectedAlertPresentException:
        try:
            while True: # to dismiss repeat alerts
                alert = driver.switch_to.alert
                alert.accept()
                print('(2) dismissing alert')
                time.sleep(3)
        except NoAlertPresentException:
            try:
                first_window_handle = driver.window_handles[0]
                # close all windows except for the first
                for window_handle in driver.window_handles[1:]:
                    driver.switch_to.window(window_handle)
                    driver.close()
                driver.switch_to.window(first_window_handle)
            except:
                driver.switch_to.window(driver.window_handles[0])
                print('recursive call')
                scrape_yv(driver=driver, counter=counter,
                          data_list=data_list, last_print=last_print, error_links=error_links)       
    except KeyboardInterrupt:
        print('keyboard interrupt. saving result')
        df = pd.DataFrame(data_list)
        df.to_csv(r'C:\Users\hwx756\Downloads\yad vashem data/yad_vashem_filmdata_err_' + str(counter) + '.csv', index=False, sep='\t')
        return counter, data_list, error_links
    except Exception as e:
        print(f'unexpected error:  \n{e}\nreturning.')
        print(f'number of items scraped: {len(data_list)}')
        print(f'number of errors detected: {len(error_links)}')
        if error_links: print(f'last error link {error_links[-1]}')
        print(f'last two scraped items {data_list[-2:]}')
        df = pd.DataFrame(data_list)
        df.to_csv(r'C:\Users\hwx756\Downloads\yad vashem data/yad_vashem_filmdata_err_' + str(counter) + '.csv', index=False, sep='\t')
        return counter, data_list, error_links


counter, data_list, error_links = scrape_yv(driver=driver,counter=42)

df = pd.DataFrame(data_list)
