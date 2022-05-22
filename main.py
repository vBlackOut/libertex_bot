#!/usr/bin/python
# -*- coding: utf-8  -*-
import os
import psutil
import yaml
from tradebot import Trading

navigateur = None

if __name__ == '__main__':
    # Read YML file
    while True:
        try:
            navigateur = Trading()
        except KeyboardInterrupt:
            quit = input("Realy quit ? y/n\n")

            if quit == "y":
                exit()
                # PROCNAME = ["geckodriver", "Web Content", "WebExtensions", "python3", "firefox"] # or chromedriver or IEDriverServer
                # for proc in psutil.process_iter():
                #     # check whether the process name matches
                #     if proc.name() in PROCNAME:
                #         proc.kill()
                #         print("kill process success -", proc.name())
                #break

            if quit == "n" or quit == "":
                print("Reboot...")
        else:
            # reboot if error
            navigateur = Trading()
