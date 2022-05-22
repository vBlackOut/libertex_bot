#!/usr/bin/python
# -*- coding: utf-8  -*-

# dependency for Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Dependency for wait element
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException,
                                        TimeoutException,
                                        StaleElementReferenceException,
                                        ElementNotInteractableException,
                                        SessionNotCreatedException)

# other element
from forex_python.converter import CurrencyRates
from rich.console import Console
from rich.table import Table
from utils import *
import base64
import time
import datetime
import re
import pickle
import requests
from database import logs_database
import numpy as np
from sklearn.linear_model import LinearRegression
from collections import Counter
import scipy.stats
from os import path

__version__ = "0.0.9"
__author__ = "vBlackOut"

class Trading():

    def __init__(self):
        self.debug = False
        self.navigateur = None
        self.broswer()
        self.ut = Utils(self.navigateur)
        self.test_action = True
        self.tab = {}
        self.profit = {}
        self.high_mise = {}
        self.max_high_mise = {}
        self.console = None
        self.data_trading = {}
        self.count_number_lost = 0
        self.last_date_count_lost = None
        self.start_simu = {}
        self.check_probability = datetime.datetime.now()
        self.probability_value = [0,0]
        compte = {"username": "user", "password": "password"}
        self.login(compte)
        self.get_trading_currency()

    def cleanhtml(self, text):
        TAG_RE = re.compile(r'<[^>]+>')
        return TAG_RE.sub('', text)

    def broswer(self):
        print(bcolors.OKGREEN + "connect to app.libertex.com" + bcolors.ENDC)

        url = "https://app.libertex.com/login"
        options_firefox = Options()
        if self.debug == True:
            options_firefox.headless = False
        else:
            options_firefox.headless = True
            options_firefox.set_preference('dom.webnotifications.enabled', True)
            options_firefox.set_preference('network.cookie.cookieBehavior', True)
            options_firefox.add_argument("start-maximized")
            options_firefox.add_argument("disable-infobars")
            options_firefox.add_argument("--disable-extensions")
            options_firefox.add_argument('--no-sandbox')
            options_firefox.add_argument('--disable-application-cache')
            options_firefox.add_argument('--disable-gpu')
            options_firefox.add_argument("--disable-dev-shm-usage")

        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.http.pipelining", True)
        profile.set_preference("network.http.proxy.pipelining", True)
        profile.set_preference("network.http.pipelining.maxrequests", 12)
        profile.set_preference("content.notify.interval", 500000)
        profile.set_preference("content.notify.ontimer", True)
        profile.set_preference("content.switch.threshold", 250000)
        profile.set_preference("browser.cache.memory.capacity", 65536) # Increase the cache capacity.
        profile.set_preference("browser.startup.homepage", "about:blank")
        profile.set_preference("reader.parse-on-load.enabled", False) # Disable reader, we won't need that.
        profile.set_preference("browser.pocket.enabled", False) # Duck pocket too!
        profile.set_preference("loop.enabled", False)
        profile.set_preference("browser.chrome.toolbar_style", 1) # Text on Toolbar instead of icons
        profile.set_preference("browser.display.show_image_placeholders", False) # Don't show thumbnails on not loaded images.
        profile.set_preference("browser.display.use_document_colors", False) # Don't show document colors.
        profile.set_preference("browser.display.use_document_fonts", 0) # Don't load document fonts.
        profile.set_preference("browser.display.use_system_colors", False) # Use system colors.
        profile.set_preference("browser.formfill.enable", False) # Autofill on forms disabled.
        profile.set_preference("browser.helperApps.deleteTempFileOnExit", True) # Delete temprorary files.
        profile.set_preference("browser.shell.checkDefaultBrowser", False)
        profile.set_preference("browser.startup.homepage", "about:blank")
        profile.set_preference("browser.startup.page", 0) # blank
        profile.set_preference("browser.tabs.forceHide", True) # Disable tabs, We won't need that.
        profile.set_preference("browser.urlbar.autoFill", False) # Disable autofill on URL bar.
        profile.set_preference("browser.urlbar.autocomplete.enabled", False) # Disable autocomplete on URL bar.
        profile.set_preference("browser.urlbar.showPopup", False) # Disable list of URLs when typing on URL bar.
        profile.set_preference("browser.urlbar.showSearch", False) # Disable search bar.
        profile.set_preference("extensions.checkCompatibility", False) # Addon update disabled
        profile.set_preference("extensions.checkUpdateSecurity", False)
        profile.set_preference("extensions.update.autoUpdateEnabled", False)
        profile.set_preference("extensions.update.enabled", False)
        profile.set_preference("general.startup.browser", False)
        profile.set_preference("plugin.default_plugin_disabled", False)
        profile.set_preference("permissions.default.image", 2) # Image load disabled again
        service = Service(log_path=path.devnull)
        self.navigateur = webdriver.Firefox(profile, options=options_firefox, service=service)
        #self.navigateur.set_window_size(1300, 1000)

        self.navigateur.maximize_window()
        # try:
        #     self.cookies = pickle.load(open("cookies.pkl", "rb"))
        # except FileNotFoundError:
        #     self.cookies = False
        time.sleep(2)
        self.navigateur.get(url)
        return self.navigateur


    def login(self, compte):
        time.sleep(1)

        main_window = self.navigateur.current_window_handle
        self.tab["main"] = main_window

        inputs = self.ut.retry(method=By.XPATH, element="//input[@id='login-field']",
                                   objects="input", send_keys=compte['username'], method_input=By.ID,
                                   element_input="submit", message="Enter ID with input",
                                   message_fail="Timeout check element recheck...",
                                   timeout=1, check_login=False, timeout_fail=2, retry=0)

        inputs = self.ut.retry(method=By.XPATH, element="//input[@id='password-field']",
                                   objects="input", send_keys=compte['password'], method_input=By.ID,
                                   element_input="submit", message="Enter PASSWORD with input",
                                   message_fail="Timeout check element recheck...",
                                   timeout=1, check_login=False, timeout_fail=2, retry=0)

        self.ut.retry(method=By.XPATH,
                      element="//input[@value='Log in']",
                      objects="click_element", timeout=5, retry=0)
        print("get profil account...")
        time.sleep(5)
        # pickle.dump(self.navigateur.get_cookies() , open("cookies.pkl","wb"))

    def get_trading_currency(self):

        self.open_tab("crypto/SOLUSD")
        #self.open_tab("currency/EURUSD")
        #self.open_tab("crypto/BTCUSD")

        time.sleep(2)

        while True:
            pickle.dump(self.navigateur.get_cookies() , open("cookies.pkl","wb"))

            for currency, value in self.tab.items():
                #try:
                self.switch_to_trading(currency)
                self.output()
                # except Exception as e:
                #     if self.debug == True:
                #         print(e)
                        #time.sleep(100)

    def simulate_trading(self, start=113, stop=115, deal="buy"):
        c = CurrencyRates()
        dt = datetime.datetime.now()

        currency_convert = c.get_rate('USD', 'EUR', dt)
        amount = (stop - start) / 0.01

        if deal == "buy":
            data = {
            	"buyOrSell": "1",
            	"lots": "1",
            	"pipAmount": amount,
            	"onePipSize": "0.01",
            	"lotSize": "1",
            	"rate": currency_convert
            }
        else:
            data = {
            	"buyOrSell": "0",
            	"lots": "1",
            	"pipAmount": amount/2,
            	"onePipSize": "0.01",
            	"lotSize": "1",
            	"rate": currency_convert
            }

        response = requests.post("https://www.rebatekingfx.com/widgets/calculation/profit", data=data).json()
        return response


    def open_tab(self, trading_tab):
        self.navigateur.switch_to.new_window()
        t = self.navigateur.window_handles[-1]# Get the handle of new tab
        self.navigateur.switch_to.window(t)
        self.navigateur.get("https://app.libertex.com/products/{}/".format(trading_tab))

        elem_name = self.ut.retry(method=By.XPATH,
                             element="//span[@class='alias']",
                             objects="single_element", message="",
                             timeout=20, retry=2)

        self.tab[elem_name.get_attribute("innerHTML")] = t

    def execute(self, action):

        file = open('script_webpage_protected.js', mode='r')
        script = file.read()

        data = self.navigateur.execute_script("var s=window.document.createElement('script');" +
        "s.type = 'text/javascript';" + "{}".format(script.replace("[script_execute]", action)) +
        "window.document.body.appendChild(s);")
        return data

    def get_chart_image(self, currency):
        currency = currency.replace("/", "")

        #time.sleep(1)
        iframe = self.ut.retry(method=By.XPATH,
                             element="//iframe",
                             objects="all_elements", message="",
                             timeout=20, retry=2)

        for frame in iframe:
            self.navigateur.switch_to.frame(frame)
            break

        # for debug
        # canvas = self.ut.retry(method=By.XPATH,
        #                      element="//canvas",
        #                      objects="all_elements", message="",
        #                      timeout=20, retry=2)
        # for i in canvas:
        #     print(i.get_attribute('outerHTML'))
        # canvas = self.navigateur.execute_script("return $('canvas').get(2).toDataURL();");

        canvas = self.execute('get_charts_image()')
        self.navigateur.switch_to.parent_frame()

        with open("images/{}.png".format(currency), "wb") as fh:
            fh.write(base64.decodebytes(bytes(canvas.replace("data:image/png;base64,", ""), "utf-8")))
        return canvas

    def probability(self, predict_short, predict_long, len_total):
        predict_buy = (predict_short["buy"] + predict_long['buy'])*100/len_total
        predict_sell = (predict_short["sell"] + predict_long['sell'])*100/len_total
        return [predict_buy, predict_sell]


    def switch_to_trading(self, trading_tab, mise=True):
        #self.navigateur.switch_to.window(self.tab[trading_tab])
        if trading_tab != "main":
            self.navigateur.switch_to.window(self.tab[trading_tab])
            time.sleep(0.005)
            data = self.execute("get_infos()")
            # prediction computer
            computer_predict_short, computer_predict_long = self.calcule_predict(data['name'], data['value'])
            self.last_check_probability = datetime.datetime.now() - self.check_probability
            time.sleep(0.005)

            if trading_tab not in data['trades'].keys():
                if trading_tab not in self.start_simu.keys():
                    self.start_simu[trading_tab] = data['value']
                    simutate = self.simulate_trading(self.start_simu[trading_tab], data['value'])

                simutate = self.simulate_trading(self.start_simu[trading_tab], data['value'])
                data["trades"][trading_tab] = {"profit" : round(simutate['result'], 2), "profit_percent": 0, "invest": "simu-buy", "startposition": data['value']}

            # gaussian predict calcule
            # if self.last_check_probability.total_seconds() >= 60:
            #     self.check_probability = datetime.datetime.now()
            self.probability_value = self.probability(computer_predict_short, computer_predict_long, 1300)


            for key, value in data['trades'].items():
                if key == trading_tab:
                    if key not in self.high_mise.keys():
                        self.high_mise[key] = [value['profit'], 0]
                    elif value['profit'] > self.high_mise[key][0]:
                        self.high_mise[key] = [value['profit'], round(value['profit']-self.high_mise[key][0], 2)]
                    else:
                        self.high_mise[key] = [self.high_mise[key][0], round(value['profit']-self.high_mise[key][0], 2)]

                    if computer_predict_short['sell'] == 300 and computer_predict_long['sell'] == 10000 and data['trades'][data['name']]['invest'] == "buy" and self.high_mise[key][1] <= -5:
                        self.action_trading(key, "stop_trading")
                        self.action_trading(key, "invert_reinvest", data['trades'][data['name']]['invest'])
                        break

                    if computer_predict_short['buy'] == 300 and computer_predict_long['buy'] == 10000 and data['trades'][data['name']]['invest'] == "sell" and self.high_mise[key][1] <= -5:
                        self.action_trading(key, "stop_trading")
                        self.action_trading(key, "invert_reinvest", data['trades'][data['name']]['invest'])
                        break

                    if computer_predict_short['sell'] == 300 and value['profit'] > 0 and data['trades'][data['name']]['profit_percent'] <= 0.1 and round(self.probability_value[0],2) > 5 and data['trades'][data['name']]['invest'] == "buy":
                        self.action_trading(key, "stop_trading")
                        self.action_trading(key, "invert_reinvest", data['trades'][data['name']]['invest'])
                        break

                    if computer_predict_short['buy'] == 300 and value['profit'] > 0 and data['trades'][data['name']]['profit_percent'] <= 0.1 and round(self.probability_value[0],2) > 5 and data['trades'][data['name']]['invest'] == "sell":
                        self.action_trading(key, "stop_trading")
                        self.action_trading(key, "invert_reinvest", data['trades'][data['name']]['invest'])
                        break

                    if computer_predict_short['buy'] == 300 and value['profit'] < -2 and data['trades'][data['name']]['invest'] == "sell" and round(self.probability_value[0],2) > 5:
                        self.action_trading(key, "stop_trading")
                        self.action_trading(key, "invert_reinvest", data['trades'][data['name']]['invest'])
                        break

                    if computer_predict_short['sell'] == 300 and value['profit'] < -2 and data['trades'][data['name']]['invest'] == "buy" and round(self.probability_value[0],2) > 5:
                        self.action_trading(key, "stop_trading")
                        self.action_trading(key, "invert_reinvest", data['trades'][data['name']]['invest'])
                        break

                    # stop if lose 5€
                    #if self.high_mise[key][0] <= -2.5 and value['profit'] < -2.5 and "simu" not in data['trades'][data['name']]['invest']:
                        #pass
                        #self.action_trading(key, "stop_trading")
                        #self.action_trading(name, "invert_reinvest", data['trades'][data['name']]['invest'])

                    # if earn - 2 % and profit positif stop trad
                    #if self.high_mise[key][1] <= -3 and self.high_mise[key][0] >= 1 and value['profit'] > 13 and "simu" not in data['trades'][data['name']]['invest']:
                        #pass
                        #self.action_trading(key, "stop_trading")
                        #time.sleep(1)
                        #self.action_trading(name, "invert_reinvest", data['trades'][data['name']]['invest'])

                    #elif data['profit_today'] > 1200 and "simu" not in data['trades'][data['name']]['invest']:
                        #pass
                        #self.last_date_count_lost = datetime.datetime.now()
                        #self.action_trading(key, "stop_trading")
                        #self.action_trading(key, "invert_reinvest", data['trades'][data['name']]['invest'])

                    # elif (data['profit_today'] > 5 and self.high_mise[key][1] <= 0) and data['trades'][data['name']]['invest'] == "sell":
                    #     self.count_number_lost = 1
                    #     self.last_date_count_lost = datetime.datetime.now()
                    #     self.action_trading(key, "stop_trading")
                    #     self.action_trading(key, "reinvest", data['trades'][data['name']]['invest'])

                    # elif (self.high_mise[key][1] <= -7 and self.high_mise[key][0] <= 0) or value['profit'] < -10:
                    #     self.count_number_lost += 1
                    #
                    #     if self.count_number_lost <= 1:
                    #         self.action_trading(key, "stop_trading")
                    #         # if get_signal == "Buy" and invest_direction == "buy":
                    #         self.action_trading(key, "invert_reinvest", data['trades'][data['name']]['invest'])
                    #         self.last_date_count_lost = datetime.datetime.now()
                    #     else:
                    #         if self.last_date_count_lost != None and (datatime.datetime.now()-self.last_date_count_lost).total_seconde() < 300:
                    #             pass
                    #         else:
                    #             self.last_date_count_lost = None
                    #             self.count_number_lost = 0
                    #self.get_chart_image(trading_tab)
                    break

            # verif trades in data profil
            if data['name'] in data['trades'].keys():
                self.data_trading[data['name']] = {
                        'date': "{}".format(datetime.datetime.fromtimestamp(int(data['date'])/1000)),
                        'value_currency': "{}".format(data['value']),
                        'percent_gain_currency': data['profit_today'],
                        'profit_currency': data['trades'][data['name']]['profit'],
                        'mise_percent': data['trades'][data['name']]['profit_percent'],
                        'max_high_mise': self.high_mise[key],
                        'trade_status': data['status'],
                        'invest_type': data['trades'][data['name']]['invest'],
                        'get_signal': "",
                        'predict_action': [computer_predict_short, computer_predict_long],
                        'signal_info': data['info_signal'],
                        'probability': "buy: {}%\nsell: {}%".format(round(self.probability_value[0],2), round(self.probability_value[1],2))
                }
                self.append_database(currency=data['name'], value=data['value'])
            else:
                self.data_trading.pop(data['name'], None)
            #print(self.data_trading)
            time.sleep(0.001)
            #print(name_currency, value_currency, percent_gain_currency, profit_currency, mise_percent)


        # c = Counter(list_data)
        #
        # # returns the probability of a given number a
        # return float(c[a]) / len(list_data)

    def calcule_predict(self, currency, current_value):
        data = logs_database.select().where(logs_database.currency==currency).order_by(logs_database.id.desc()).limit(1000)

        list_value_currency = []
        list_id_currency = []

        list_value_currency_long = []
        list_id_currency_long = []

        # predict long
        for i, currency_db in enumerate(data):
            list_value_currency_long.append(currency_db.value)
            list_id_currency_long.append(i)

        x = np.array(list_id_currency_long)
        y = np.array(list_value_currency_long)

        dict_predict_long = {"buy": 0, "sell": 0, "neutre": 0}

        if len(x) >= 1 and len(y) >= 1:
            k, d = np.polyfit(x, y, 1)
            y_pred_long = k*x + d

            predict_value_long = y_pred_long

            for i in predict_value_long[::-1]:
                if current_value > round(float(i),2):
                    action_pred = "buy"
                    dict_predict_long['buy'] += 1
                elif current_value < round(float(i),2):
                    action_pred = "sell"
                    dict_predict_long['sell'] += 1
                elif current_value == round(float(i),2):
                    dict_predict_long['neutre'] += 1


        # predict short
        for i, currency_db in enumerate(data[::-1][-300:]):
            list_value_currency.append(currency_db.value)
            list_id_currency.append(i)

        x = np.array(list_id_currency)
        y = np.array(list_value_currency)
        dict_predict_short = {"buy": 0, "sell": 0, "neutre": 0}

        if len(x) >= 1 and len(y) >= 1:

            k, d = np.polyfit(x, y, 1)
            y_pred_short = k*x + d

            predict_value_short = y_pred_short

            for i in predict_value_short:
                if current_value > round(float(i),2):
                    action_pred = "buy"
                    dict_predict_short['buy'] += 1
                elif current_value < round(float(i),2):
                    action_pred = "sell"
                    dict_predict_short['sell'] += 1
                elif current_value == round(float(i),2):
                    dict_predict_short['neutre'] += 1

        return dict_predict_short, dict_predict_long


    def append_database(self, **data):
        try:
            last_data = logs_database.select().order_by(logs_database.id.desc()).get()

            if data['value'] != int(last_data.value):
                return logs_database.create(currency=data['currency'], value=data['value']).save()
        except:
            return logs_database.create(currency=data['currency'], value=data['value']).save()


    def action_trading(self, currency, action, invest_direction=""):
        if currency in self.start_simu.keys():
            return None

        if action == "invert_reinvest":
            if invest_direction == "buy":
                print("prepare to sell...")
                time.sleep(1)

                button = self.ut.retry(method=By.XPATH,
                                      element="//div[@class='trade-methods-container']",
                                      objects="all_elements", message="",
                                      timeout=20, retry=2)
                button[0].click()
                time.sleep(1)
                button = self.ut.retry(method=By.XPATH,
                                      element="//a[@class='new-invest']",
                                      objects="all_elements", message="",
                                      timeout=20, retry=2)
                button[0].click()
                # self.navigateur.execute_script("{}".format("$('.ui-widget-overlay').remove();"))
                # # clicl to sell button
                # self.navigateur.execute_script("{}".format("$('.a-btn.reduction.show-trade-methods').click();"))
                # time.sleep(1)
                # # click to submit button
                time.sleep(1)
                self.navigateur.execute_script("{}".format("$('.a-submit').click();"))
                time.sleep(1)
                # click to x hide popup
                self.navigateur.execute_script("{}".format("$('.ui-button-icon.ui-icon.ui-icon-closethick').click();"))
                # time.sleep(1)
                # # confirm notification
                self.navigateur.execute_script("{}".format("$('.a-btn.a-btn-blue.a-btn-ok').click();"))
            else:
                print("prepare to buy")
                time.sleep(1)

                button = self.ut.retry(method=By.XPATH,
                                      element="//div[@class='trade-methods-container']",
                                      objects="all_elements", message="",
                                      timeout=20, retry=2)
                button[1].click()
                time.sleep(1)
                button = self.ut.retry(method=By.XPATH,
                                      element="//a[@class='new-invest']",
                                      objects="all_elements", message="",
                                      timeout=20, retry=2)
                button[1].click()
                time.sleep(1)

                self.navigateur.execute_script("{}".format("$('.a-submit').click();"))
                time.sleep(1)
                # click to x hide popup
                self.navigateur.execute_script("{}".format("$('.ui-button-icon.ui-icon.ui-icon-closethick').click();"))
                # time.sleep(1)
                # # confirm notification
                self.navigateur.execute_script("{}".format("$('.a-btn.a-btn-blue.a-btn-ok').click();"))

        if action == "reinvest":
            if invest_direction == "sell":
                print("prepare to sell...")
                time.sleep(1)
                self.navigateur.execute_script("{}".format("$('.ui-widget-overlay').remove();"))
                # clicl to sell button
                self.navigateur.execute_script("{}".format("$('.a-btn.new-invest.invest-btn.reduction').click();"))
                time.sleep(1)
                # click to submit button
                self.navigateur.execute_script("{}".format("$('.a-submit').click();"))
                time.sleep(1)
                # click to x hide popup
                self.navigateur.execute_script("{}".format("$('.ui-button-icon.ui-icon.ui-icon-closethick').click();"))
                time.sleep(1)
                # confirm notification
                self.navigateur.execute_script("{}".format("$('.a-btn.a-btn-blue.a-btn-ok').click();"))
            else:
                print("prepare to buy")
                time.sleep(1)
                self.navigateur.execute_script("{}".format("$('.ui-widget-overlay').remove();"))
                # clicl to buy button
                self.navigateur.execute_script("{}".format("$('.a-btn.new-invest.invest-btn.growth').click();"))
                time.sleep(1)
                # click to submit button
                self.navigateur.execute_script("{}".format("$('.a-submit').click();"))
                time.sleep(1)
                # click to x hide popup
                self.navigateur.execute_script("{}".format("$('.ui-button-icon.ui-icon.ui-icon-closethick').click();"))
                time.sleep(1)
                # confirm notification
                self.navigateur.execute_script("{}".format("$('.a-btn.a-btn-blue.a-btn-ok').click();"))

        elif action == "stop_trading":
            print("stop trading for {}".format(currency), end = "\r")
            self.execute("click_to_currency('{}')".format(currency))
            time.sleep(1)
            self.navigateur.execute_script("{}".format("$('.a-btn.a-btn-neg.a-btn-big.invest-close').click();"))
            time.sleep(1)
            self.navigateur.execute_script("{}".format("$('.a-btn.a-btn-blue.invest-close-ok').click();"))
            time.sleep(1)
            self.navigateur.execute_script("{}".format("$('.ui-button-icon.ui-icon.ui-icon-closethick').click();"))
            print("stop trading for {} {}Done{}".format(currency, bcolors.OKGREEN, bcolors.ENDC))

        elif action == None:
            currency.click()
            time.sleep(1)
            # close x popup
            self.navigateur.execute_script("{}".format("$('.ui-button-icon.ui-icon.ui-icon-closethick').click();"))

        if self.test_action == True:
            self.test_action = False

    def output(self):

        if self.console != None:
            #pass
            self.console.clear()
        else:
            self.console = Console()

        self.table = Table(show_header=True, header_style="bold magenta")
        self.table.add_column("Date refresh", justify="center")
        self.table.add_column("Product", style="dim", justify="center", width=22)
        self.table.add_column("Status", style="dim", justify="center")
        self.table.add_column("Price", justify="center")
        self.table.add_column("Product % \ntoday", justify="center")
        self.table.add_column("product \nearn €", justify="center")
        self.table.add_column("Earn pourcent", justify="center")
        self.table.add_column("Earn max \n(Earn reward)", justify="center")
        self.table.add_column("Signal", justify="center")
        self.table.add_column("Computer Predict", justify="center")
        self.table.add_column("Probability", justify="center")



        for key, value in self.data_trading.items():

            if value['percent_gain_currency'] >= 0:
                percent_gain_currency = "[bold green] {} %".format(value['percent_gain_currency'])
            else:
                percent_gain_currency = "[bold red] {} %".format(value['percent_gain_currency'])

            if value['profit_currency'] >= 0:
                profit_currency = "[bold green] {} €".format(value['profit_currency'])
            else:
                profit_currency = "[bold red] {} €".format(value['profit_currency'])
            #
            if value['mise_percent'] >= 0:
                mise_percent = "[bold green] {} %".format(value['mise_percent'])
            else:
                mise_percent = "[bold red] {} %".format(value['mise_percent'])
            #
            if value['max_high_mise'][1] >= 0:
                max_high_mise = "[bold green] {} € ({} €)".format(value['max_high_mise'][0], value['max_high_mise'][1])
            else:
                max_high_mise = "[bold red] {} € ({} €)".format(value['max_high_mise'][0], value['max_high_mise'][1])

            if value['invest_type'] == "buy":
                invest_type = "[bold green]buy[/ bold green]"
            elif value['invest_type'] == "sell":
                invest_type = "[bold red]sell[/ bold red]"
            elif value['invest_type'] == "simu-sell":
                invest_type = "[bold orange]simu sell[/ bold orange]"
            elif value['invest_type'] == "simu-buy":
                invest_type = "[bold orange]simu buy[/ bold orange]"

            # if value['trade_status'] == False:
            #     self.table.add_row(value['date'], "{} [{}]".format(key, invest_type), "[red]❌", value['value_currency'],  percent_gain_currency,  profit_currency, mise_percent, max_high_mise, "{} {}".format(value['get_signal'], value['signal_info']))
            # else:
            #     self.table.add_row(value['date'], "{} [{}]".format(key, invest_type), "[green]✅", value['value_currency'],  percent_gain_currency,  profit_currency, mise_percent, max_high_mise, "{} {}".format(value['get_signal'], value['signal_info']))
            if value['trade_status'] == "Open":
                self.table.add_row(value['date'], "{} [{}]".format(key, invest_type), "[green]✅", value['value_currency'], percent_gain_currency,  profit_currency, mise_percent, max_high_mise, "", "Short buy: {} sell: {} neutre: {}\nLong buy: {} sell: {} neutre: {}".format(value['predict_action'][0]['buy'], value['predict_action'][0]['sell'], value['predict_action'][0]['neutre'], value['predict_action'][1]['buy'], value['predict_action'][1]['sell'], value['predict_action'][1]['neutre']), value['probability'])

            if  value['trade_status'] == "Closed":
                self.table.add_row(value['date'], "{} [{}]".format(key, invest_type), "[red]❌", value['value_currency'], percent_gain_currency,  profit_currency, mise_percent, max_high_mise, "", "Short buy: {} sell: {} neutre: {}\nLong buy: {} sell: {} neutre: {}".format(value['predict_action'][0]['buy'], value['predict_action'][0]['sell'], value['predict_action'][0]['neutre'], value['predict_action'][1]['buy'], value['predict_action'][1]['sell'], value['predict_action'][1]['neutre']), value['probability'])

        text = """
         _ _ _               _               _           _
        | (_) |             | |             | |         | |
        | |_| |__   ___ _ __| |_ _____  __  | |__   ___ | |_
        | | | '_ \ / _ \ '__| __/ _ \ \/ /  | '_ \ / _ \| __|
        | | | |_) |  __/ |  | ||  __/>  <   | |_) | (_) | |_
        |_|_|_.__/ \___|_|   \__\___/_/\_\  |_.__/ \___/ \__|
        Version: {}
        Dev by {}
        """.format(__version__, __author__)

        self.console.print(text, self.table)
        time.sleep(0.001)

    def stop(self):
        print("__exit__")
        self.navigateur.close()
