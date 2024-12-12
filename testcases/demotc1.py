import selenium
from selenium import webdriver

class DemoExplicitwait():
    def demo_exp_wait(selfself):
        driver=webdriver.Chrome()
        wait=webdriverwait(driver,10)
        driver.get("https://www.yatra.com/")
        driver.maximize_window()
        depart_from=wait.util(EC.element_to_be_clickable((by.Xpath,"")))