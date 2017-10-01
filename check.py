#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from notifications.twilio import TwilioNotifier
from notifications.messenger import MessengerNotifier

import getpass
from os import environ, getenv
from sys import stdout
from os.path import join, dirname
from dotenv import load_dotenv

import time

class GDQMemberChecker:

    def __init__(self, cap, *args, **kwargs):
        self.member_cap = cap
        if kwargs['headless']:
            self.driver = webdriver.PhantomJS()
        else:
            self.driver = webdriver.Chrome()
        self.driver.get("https://gamesdonequick.com")
        assert "Games Done Quick" in self.driver.title
        self.logged_in = len(self.driver.find_elements_by_link_text("Login")) == 0 # Normally is False

    def destroy(self):
        self.driver.quit()

    def navigate(self, where):
        if where == 'login':
            login_els = self.driver.find_elements_by_link_text("Login")
            if len(login_els) > 0:
                login_els[0].click()
        elif where == 'profile':
            nav_els = self.driver.find_elements_by_css_selector("ul.nav.navbar-right")
            if len(nav_els) > 0:
                all_a = nav_els[0].find_elements(By.TAG_NAME, 'a')
                a = list(filter(lambda x: "profile" in x.get_attribute("href"), all_a))
                self.driver.get(a[0].get_attribute("href"))
            else:
                print("No nav elements; can't get profile link")
        return False

    def login(self, email, password):
        email_el = self.driver.find_element_by_id("email")
        password_el = self.driver.find_element_by_id("password")

        email_el.clear()
        email_el.send_keys(email)
        password_el.send_keys(password + "\n")

        warn_els = self.driver.find_elements_by_css_selector("div.alert.alert-danger")
        self.logged_in = len(warn_els) == 0
        return self.logged_in

    def check_number(self):
        # There is no real way to find the limit in GDQ's markup, so I'll just search for the limit
        num_el = self.driver.find_element_by_xpath("//*[contains(text(), '{}')]".format(self.member_cap))
        return num_el.get_attribute("textContent")

    def refresh(self):
        self.driver.refresh()

gdq = None
fbm = None

def attempt_login(override=False):
    # Login helper function
    credentials_from_env = False
    email = environ.get("GDQ_EMAIL")
    if not email or override:
        email = input("Email: ").strip()
    else:
        credentials_from_env = True
    password = environ.get("GDQ_PASSWORD")
    if not password or override:
        password = getpass.getpass("Password: ").strip()
    else:
        credentials_from_env = True
    if not gdq.login(email, password):
        if credentials_from_env:
            print("WARN: Environment credentials are incorrect")
            print("Prompting for user input")
            attempt_login(True)
        else:
            attempt_login()

def main():
    global gdq
    global fbm

    # Load environment
    dotenv_path = join(dirname(__file__), 'conf.env')
    load_dotenv(dotenv_path)

    # Read member cap
    GDQ_MEMBER_CAP = int(getenv("GDQ_MEMBER_CAP"))
    if not GDQ_MEMBER_CAP:
        print("No member cap specified. Exiting...")
        sys.exit(1)

    # Start twilio notifier
    twil_settings = {
        'sid': getenv("GDQ_TWILIO_SID"),
        'token': getenv("GDQ_TWILIO_TOKEN"),
        'to': getenv("GDQ_TWILIO_PHONE_TO"),
        'fm': getenv("GDQ_TWILIO_PHONE_FROM")
    }
    if all(value != None for value in twil_settings.values()):
        twil = TwilioNotifier(**twil_settings)
        print("Started Twilio notifier")
    else:
        print("Twilio notifier disabled")

    # Start messenger notifier
    fbm_settings = {
        'email': getenv("GDQ_MESSENGER_EMAIL"),
        'password': getenv("GDQ_MESSENGER_PASSWORD")
    }
    if all(value != None for value in fbm_settings.values()):
        print("Starting Messenger notifier")
        fbm = MessengerNotifier(**fbm_settings)
        print("Started Messenger notifier")
    else:
        print("Messenger notifier disabled")

    # Start selenium
    gdq = GDQMemberChecker(GDQ_MEMBER_CAP, headless=False)
    if not gdq.logged_in:
        gdq.navigate("login")
        attempt_login()

    assert gdq.logged_in

    # Load profile page -- contains member count
    gdq.navigate("profile")

    lastActual = None
    while True:
        strnum = gdq.check_number()
        actual = int(strnum.split("/")[0].strip())
        print("{}: {}{}". format(time.strftime("%Y-%m-%d %H:%M:%S"), strnum, '\a: Registration open!' if actual < GDQ_MEMBER_CAP else ''))
        if lastActual != None and actual != lastActual:
            if twil: twil.notify("Spots changed to {} from {}".format(actual, lastActual))
            if fbm:   fbm.notify("Spots changed to {} from {}".format(actual, lastActual))
        lastActual = actual

        time.sleep(5)
        gdq.refresh()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if gdq: gdq.destroy()
        if fbm: fbm.logout()
