#!./venv/bin/python
from selenium import webdriver
from selenium.common import exceptions as serror
from selenium.webdriver.common.keys import Keys
import sys
from getpass import getpass
import time
import random

print("""
  _____           _           ___           _   _     
  \_   \_ __  ___| |_ __ _   /   \___  __ _| |_| |__  
   / /\/ '_ \/ __| __/ _` | / /\ / _ \/ _` | __| '_ \ 
/\/ /_ | | | \__ \ || (_| |/ /_//  __/ (_| | |_| | | |
\____/ |_| |_|___/\__\__,_/___,' \___|\__,_|\__|_| |_|
""")

app = True
main_logined = False
option = webdriver.FirefoxOptions()
option.headless=True

if len(sys.argv) > 1:
    if sys.argv[1] == "-D":
        option.headless=False



def log(text):
    with open('insta_death.log', 'a') as file:
        file.write(time.strftime('%Y/%m/%d %H:%M:%S ') + text + '\n')

def create_browser():
    global browser
    try:
        browser = webdriver.Firefox(options=option)
    except serror.WebDriverException:
        print("\nWebdriver not in path !\nplease copy webdriver in /usr/bin")
        sys.exit()

def create_driver():
    try:
        browser = webdriver.Firefox(options=option)
        return browser
    except serror.WebDriverException:
        print("\nWebdriver not in path !\nplease copy webdriver in /usr/bin")
        sys.exit()

def login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(1)
    try:
        driver.find_element_by_xpath('//*[text()="Accept All"]').click()
    except Exception:
        pass
    time.sleep(2)
    while True:
        try:
            driver.find_element_by_xpath("//input[@name='username']").send_keys(username)
            driver.find_element_by_xpath("//input[@name='password']").send_keys(password)
            driver.find_element_by_xpath("//button[@type='submit']").click()
            time.sleep(5)
            if driver.current_url == "https://www.instagram.com/accounts/login/":
                print("\nWrong Password!\n")
                return False
            else:
                return True
        except serror.NoSuchElementException:
            continue
        except serror.ElementClickInterceptedException:
            print("\nInvalid Login data!\n")
            return False

def logout(driver):
    driver.get("https://www.instagram.com/accounts/logout/")

def main_login():
    global main_logined
    if not main_logined:
        while not main_logined:
            print("Main Account Login")
            res = login(
                browser,
                input("Instagram Username: "),
                getpass("Instagram Password: ")
            )
            if res:
                main_logined = True
            else:
                main_logined = False

def is_private(driver):
    try:
        driver.find_element_by_xpath("//h2[normalize-space()='This Account is Private']")
        print("\nThis Account is Private\nFollow to see their photos and videos.\n")
        return True
    except serror.NoSuchElementException:
        return False

def is_404(driver):
    try:
        driver.find_element_by_xpath('//h2[normalize-space()="Sorry, this page isn\'t available."]')
        print("\n404 Error Page Not Found\n")
        return True
    except serror.NoSuchElementException:
        return False

def is_not_valid_page(driver):
    if is_private(driver):
        return True
    elif is_404(driver):
        return True
    else:
        return False

def try_comment_scrool_post():
    for i in range(5):
        time.sleep(1)
        try:
            browser.find_element_by_xpath("//button[@class='dCJp8 afkep']")
        except serror.NoSuchElementException:
            continue
        return True
    return False

def get_commenter_with_link():
    main_login()
    link = ""
    while not link.startswith("https://www.instagram.com/p/"):
        print("\nSample: https://www.instagram.com/p/[ID]")
        link = input("Post Link: ")
    filename = input("File Name for save id: ")
    browser.get(link)
    time.sleep(2)
    if is_not_valid_page(browser):
        return 0
    er = False
    while True:
        try:
            time.sleep(1)
            browser.find_element_by_xpath("//button[@class='dCJp8 afkep']").click()
        except serror.NoSuchElementException:
            if try_comment_scrool_post():
                continue
            else:
                break
    comments = browser.find_elements_by_xpath("//ul[@class='Mr508 ']")
    users = []
    with open(filename, "a") as file:
        for comment in comments:
            u = comment.text.split("\n")[0]
            if u not in users:
                users.append(u)
                file.write(f"{u}\n")
    print("\n", len(users), " User saved.")

def get_liker_with_link():
    main_login()
    link = ""
    while not link.startswith("https://www.instagram.com/p/"):
        print("Sample: https://www.instagram.com/p/[ID]")
        link = input("Post Link: ")
    browser.get(link)
    filename = input("File Name for save id: ")
    time.sleep(2)
    if is_not_valid_page(browser):
        return 0
    browser.find_element_by_class_name("zV_Nj").click()
    time.sleep(2)
    last_id = ""
    old = set()
    users_id = set()
    users_id_text = set()
    while True:
        news = set()
        elements = browser.find_elements_by_xpath("//body/div[contains(@role,'presentation')]/div[contains(@role,'dialog')]/div[contains(@class,'_1XyCr')]/div[contains(@class,'')]/div/div/div")
        old |= set(elements)
        news |= old
        news -= users_id
        for i in news:
            users_id_text.add(i.text.split("\n")[0])
            users_id.add(i)

        try:
            browser.execute_script("return arguments[0].scrollIntoView();", elements[-1])
        except IndexError:
            time.sleep(1)
            continue
        if last_id == elements[-1].text.split("\n")[0]:
            break
        else:
            last_id = elements[-1].text.split("\n")[0]
            time.sleep(1)
            continue
    with open(filename, "a") as file:
        for i in users_id_text:
            file.write(i+"\n")
    print("\n", len(users_id_text), " User saved.")

def get_following_by_id():
    main_login()
    username = input("Username of page: @")
    browser.get(f"https://www.instagram.com/{username}/")
    time.sleep(2)
    filename = input("File Name for save id: ")
    if is_not_valid_page(browser):
        return 0
    browser.find_element_by_xpath(f"//a[@href='/{username}/following/']").click()
    time.sleep(2)
    last_id = ""
    old = set()
    users_id = set()
    users_id_text = set()
    while True:
        news = set()
        elements = browser.find_elements_by_xpath("//body/div[contains(@role,'presentation')]/div[contains(@role,'dialog')]/div[contains(@class,'_1XyCr')]/div[contains(@class,'isgrP')]/ul[contains(@class,'_6xe7A')]/div[contains(@class,'PZuss')]/li")
        old |= set(elements)
        news |= old
        news -= users_id
        for i in news:
            users_id_text.add(i.text.split("\n")[0])
            users_id.add(i)
        try:
            browser.execute_script("return arguments[0].scrollIntoView();", elements[-1])
        except IndexError:
            time.sleep(1)
            continue
        if last_id == elements[-1].text.split("\n")[0]:
            break
        else:
            last_id = elements[-1].text.split("\n")[0]
            time.sleep(1)
            continue
    with open(filename, "a") as file:
        for i in users_id_text:
            file.write(i+"\n")
    print("\n", len(users_id_text), " User saved.")

def get_followers_by_id():
    main_login()
    username = input("Username of page: @")
    browser.get(f"https://www.instagram.com/{username}/")
    time.sleep(2)
    filename = input("File Name for save id: ")
    if is_not_valid_page(browser):
        return 0
    browser.find_element_by_xpath(f"//a[@href='/{username}/followers/']").click()
    time.sleep(2)
    last_id = ""
    old = set()
    users_id = set()
    users_id_text = set()
    while True:
        news = set()
        elements = browser.find_elements_by_xpath("//body/div[contains(@role,'presentation')]/div[contains(@role,'dialog')]/div[contains(@class,'_1XyCr')]/div[contains(@class,'isgrP')]/ul[contains(@class,'_6xe7A')]/div[contains(@class,'PZuss')]/li")
        old |= set(elements)
        news |= old
        news -= users_id
        for i in news:
            users_id_text.add(i.text.split("\n")[0])
            users_id.add(i)
        try:
            browser.execute_script("return arguments[0].scrollIntoView();", elements[-1])
        except IndexError:
            time.sleep(1)
            continue
        if last_id == elements[-1].text.split("\n")[0]:
            break
        else:
            last_id = elements[-1].text.split("\n")[0]
            time.sleep(1)
            continue
    with open(filename, "a") as file:
        for i in users_id_text:
            file.write(i+"\n")
    print("\n", len(users_id_text), " User saved.")

def send_direct(driver, message, user):
    driver.get("https://www.instagram.com/direct/inbox/")
    time.sleep(0.5)
    try:
        driver.find_element_by_css_selector("button.aOOlW:nth-child(2)").click()
    except serror.NoSuchElementException:
        pass
    while True:
        try:
            driver.find_element_by_xpath("//div[contains(@class,'QBdPU')]//*[local-name()='svg']").click()
            break
        except serror.NoSuchElementException:
            continue
    driver.find_element_by_xpath("//input[@placeholder='Search...']").send_keys(user)
    time.sleep(2.5)
    driver.find_element_by_css_selector("div.-qQT3:nth-child(1) > div:nth-child(1) > div:nth-child(3) > button:nth-child(1) > span:nth-child(1)").click()
    driver.find_element_by_xpath("//div[contains(@class,'rIacr')]").click()
    time.sleep(1.7)
    message = message.split("\n")
    msgbox = driver.find_element_by_xpath("//textarea[contains(@placeholder,'Message...')]")
    for i in message:
        msgbox.send_keys(i)
        webdriver.ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).perform()

    driver.find_element_by_xpath("//button[normalize-space()='Send']").click()
    time.sleep(0.5)
    log(f'Direct send to {user}')

def send_multi_direct():
    bots = []
    filename = input("Account Combo List: ")
    users_list = input("Users List: ")
    message_list = input("Message List: ")
    messages = []
    users = []
    with open(filename, "r") as file:
        for i in file:
            i = i.strip()
            if i:
                l = i.split(':')
                bots.append([l[0], l[1], create_driver()])
    for bot in bots:
        while True:
            if not login(bot[2], bot[0], bot[1]):
                print(bot[0], ":", bot[1])
                bot[1] = input("Enter Valid Password: ")
                continue
            else:
                break
    with open(message_list, "r") as file:
        text = ''
        for i in file:
            text += i
        messages += text.split(';')
    
    with open(users_list, "r") as file:
        for i in file:
            if i.strip():
                users.append(i)
    
    while users:
        for bot in bots:
            try:
                send_direct(
                    bot[2],
                    random.choice(messages),
                    users.pop(0)
                )
                with open(users_list+".unsend", "w") as f:
                    f.write("\n".join(users))
            except IndexError:
                for bot in bots:
                    bot[2].close()
            except Exception:
                continue
    print("\nMessages Sended.")

def follow(driver, username):
    driver.get(f'https://www.instagram.com/{username}/')
    time.sleep(2)
    try:
        driver.find_element_by_xpath("//*[text()='Follow']").click()
        time(2)
        log(f'User followed {username}')
    except serror.NoSuchElementException:
        pass

def multi_follow():
    bots = []
    filename = input("Account Combo List: ")
    users_list = input("Users List: ")
    users = []
    with open(filename, "r") as file:
        for i in file:
            i = i.strip()
            if i:
                l = i.split(':')
                bots.append([l[0], l[1], create_driver()])
    for bot in bots:
        while True:
            if not login(bot[2], bot[0], bot[1]):
                print(bot[0], ":", bot[1])
                bot[1] = input("Enter Valid Password: ")
                continue
            else:
                break
    
    with open(users_list, "r") as file:
        for i in file:
            if i.strip():
                users.append(i)
    
    while users:
        for bot in bots:
            try:
                follow(
                    bot[2],
                    users.pop(0)
                )
                with open(users_list+".notfollow", "w") as f:
                    f.write("\n".join(users))
            except IndexError:
                for bot in bots:
                    bot[2].close()
            except Exception:
                continue
    print("\nUsers Followed.")

def unfollow(driver, username):
    driver.get(f'https://www.instagram.com/{username}/')
    time.sleep(2)
    try:
        driver.find_element_by_xpath("//span[@aria-label='Following']").click()
        time.sleep(1)
        driver.find_element_by_xpath("//button[normalize-space()='Unfollow']").click()
        time.sleep(1)
        log('User Unfollowed')
    except serror.NoSuchElementException:
        pass

def multi_unfollow():
    bots = []
    filename = input("Account Combo List: ")
    users_list = input("Users List: ")
    users = []
    with open(filename, "r") as file:
        for i in file:
            i = i.strip()
            if i:
                l = i.split(':')
                bots.append((l[0], l[1], create_driver()))
    for bot in bots:
        while True:
            if not login(bot[2], bot[0], bot[1]):
                print(bot[0], ":", bot[1])
                bot[1] = input("Enter Valid Password: ")
                continue
            else:
                break
    
    with open(users_list, "r") as file:
        for i in file:
            if i.strip():
                users.append(i)
    
    while users:
        for bot in bots:
            try:
                unfollow(
                    bot[2],
                    users[0]
                )
            except IndexError:
                for bot in bots:
                    bot[2].close()
            except Exception:
                continue
        users.pop(0)
    print("\nUsers Unfollowed.")

def print_banner():
    print("")
    print("1.  Get Comenter with link")
    print("2.  Get Liker with link")
    print("3.  Get User Followers")
    print("4.  Get User Following")
    print("5.  Send Direct to User List")
    print("6.  Follow List User")
    print("7.  Unfollow List User")
    print("98. Login Main User")
    print("99. Logout Main User")
    print("0.  Exit")
    print("")

def item_manage(num):
    global app
    global main_logined
    if num == "1":
        get_commenter_with_link()
    elif num == "2":
        get_liker_with_link()
    elif num == "3":
        get_followers_by_id()
    elif num == "4":
        get_following_by_id()
    elif num == "5":
        send_multi_direct()
    elif num == "6":
        multi_follow()
    elif num == "7":
        multi_unfollow()
    elif num == "98":
        main_login()
    elif num == "99":
        logout(browser)
        main_logined = False
    elif num == "0":
        app = False
    else:
        print("Wrong Number!")

if __name__ == '__main__':
    create_browser()
    while app:
        try:
            print_banner()
            item = input("> ")
            print("")
            item_manage(item)
        
        except KeyboardInterrupt:
            print("\nPlease Wait ...")
            create_browser()
            main_logined = False
    try:            
        browser.close()
    except BaseException:
        pass
    finally:
        sys.exit()
