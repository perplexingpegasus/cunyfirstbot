from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time


reload_text = "Page failed to load... Trying again.\n"
login_again = "Multiple reload attempts failed... Logging in again.\n"

attempts = []
registrations = []


print('*******CUNY-FIRST-REGISTRATION-BOT*******\n\n')
print(
    "Welcome to CUNY First Registration Bot\n"
    "Make sure all of the classes you're trying to get into are in your shopping cart first\n\n"
    "Enter your CUNYfirst username and password\n"
    "(don't worry, the program doesn't store it or send it anywhere)\n"
    "then enter how many minutes the program should wait in between checking for class openings\n"
    )


def get_wait_time():
    try:
        wait_time = 60 * int(input("Wait time in between checking (1-10 minutes): "))
        print('\n')
        while wait_time > 600 or wait_time < 60:
            wait_time = 60 * int(input("Wait time in between checking (1-10 minutes): "))
            print('\n')
    except ValueError:
        get_wait_time()
    else:
        return wait_time


def get_username_and_password():
    username = input("CUNYfirst username: ")
    password = input("CUNYfirst password: ")
    return username, password


username, password = get_username_and_password()
wait_time = get_wait_time()


browser = webdriver.Firefox()
print('\nConnected to Firefox...\n'
      "\nClosing Firefox will terminate this program, so like don't do that, okay?\n"
      "\nAlso this would be a good time to tell you that if you entered the wrong login info it's obviously not gonna work.\n")


def login(username, password):

    browser.get('https://home.cunyfirst.cuny.edu/')
    username_input = browser.find_element_by_id('cf-login')
    password_input = browser.find_element_by_id('password')
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.submit()




def student_center():
    try:
        element = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Student Center"))
        )
    except TimeoutException:
        print(reload_text)
        browser.refresh()
        student_center()
    else:
        element.click()


def start_loop():
    if len(attempts) < 10:
        try:
            frame = WebDriverWait(browser, 60).until(
                EC.presence_of_element_located((By.ID, "ptifrmtgtframe"))
            )
        except TimeoutException:
            attempts.append(1)
            print(reload_text)
            browser.refresh()
            start_loop()
        else:
            browser.switch_to.frame(frame)
            enroll()
    else:
        for _ in attempts:
            attempts.remove(_)
        login(username, password)
        student_center()
        start_loop()


def enroll():
    try:
        element = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.ID, "DERIVED_SSS_SCR_SSS_LINK_ANCHOR3"))
        )
    except TimeoutException:
        print(reload_text)
        browser.refresh()
        start_loop()
    else:
        element.click()
        check_for_opens()



def check_for_opens():
    try:
        icons = WebDriverWait(browser, 60).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "SSSIMAGECENTER"))
        )
    except TimeoutException:
        print(reload_text)
        browser.refresh()
        start_loop()
    else:
        for icon in icons:
            if icon.get_attribute('alt') == "Open":
                print('Found an opening...\n')
                break
        else:
            print("No classes open yet. Checking again in {} minute(s).\n".format(int(wait_time / 60)))
            time.sleep(wait_time)
            browser.refresh()
            start_loop()
        proceed()



def proceed():
    try:
        element = WebDriverWait(browser, 90).until(
            EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_LINK_ADD_ENRL\$82\$"))
        )
    except TimeoutException:
        print(reload_text)
        browser.refresh()
        start_loop()
    else:
        element.click()
        finish_enrolling()


def finish_enrolling():
    try:
        element = WebDriverWait(browser, 90).until(
            EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_SSR_PB_SUBMIT"))
        )
    except TimeoutException:
        print(reload_text)
        browser.refresh()
        start_loop()
    else:
        element.click()
        success_or_failure()

def success_or_failure():
    try:
        time.sleep(5)
        classes = WebDriverWait(browser, 90).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[id^='R_CLASS_NAME$']"))
        )
        icons = WebDriverWait(browser, 90).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "SSSIMAGECENTER"))
        )
    except TimeoutException:
        print(reload_text)
        browser.refresh()
        start_loop()
    else:
        repeat = False
        for class_number, icon in zip(classes, icons):
            if icon.get_attribute('alt') == "Success":
                print("You got into {}!".format(class_number.text))
                registrations.append(class_number)
            elif icon.get_attribute('alt') == "Error":
                repeat = True
            else:
                success_or_failure()
        if repeat:
            print("Some registrations failed. Checking again in {} minute(s)\n".format(int(wait_time / 60)))
            time.sleep(wait_time)
            browser.refresh()
            start_loop()
        else:
            print("Congrats. You got into all your classes...\n")
            for class_name in registrations:
                print(class_name)
            browser.quit()

try:
    login(username, password)
    student_center()
    start_loop()
except WebDriverException as e:
    print(str(e))
    print('The program stopped because browser was closed or something. Next time stop fucking with it and just let it run, okay?\n')
    if registrations:
        for class_name in registrations:
            print('You got into these classes...\n')
            print(class_name)