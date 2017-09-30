#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import getpass
from os import environ, getenv
from sys import stdout

import time

GDQ_DEFAULT_CAP = 1850

class GDQMemberChecker:

    def __init__(self, cap, *args, **kwargs):
        self.member_cap = cap or GDQ_DEFAULT_CAP
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
                print("Logging in...")
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
        num_el = self.driver.find_element_by_xpath("//*[contains(text(), '{}')]".format(GDQ_MEMBER_CAP))
        return num_el.get_attribute("textContent")

    def refresh(self):
        self.driver.refresh()

if __name__ == "__main__":
    GDQ_MEMBER_CAP = getenv("GDQ_MEMBER_CAP", 1850)

    gdq = GDQMemberChecker(GDQ_MEMBER_CAP, headless=False)
    gdq.navigate("login")

    def login(override=False):
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
                login(True)
            else:
                login()
    login()

    assert len(gdq.driver.find_elements_by_link_text("Login")) == 0

    gdq.navigate("profile")
    while True:
        strnum = gdq.check_number()
        actual = int(strnum.split("/")[0].strip())
        print("{}: {}{}". format(time.strftime("%Y-%m-%d %H:%M:%S"), strnum, '\a' if actual < GDQ_MEMBER_CAP or True else ''))
        time.sleep(5)
        gdq.refresh()
