import os
import time

import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

driver = None  # Global driver instance


@pytest.fixture(autouse=True)
def setup(request, browser, url):
    """
    Fixture to initialize the WebDriver based on the selected browser and navigate to the given URL.
    """
    global driver
    if browser == "chrome":
        driver = webdriver.Chrome(ChromeDriverManager().install())
    elif browser == "firefox":
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    elif browser == "edge":
        driver = webdriver.Edge(EdgeChromiumDriverManager().install())
    else:
        raise ValueError(f"Browser '{browser}' is not supported!")

    driver.get(url)  # Navigate to the specified URL
    driver.maximize_window()  # Maximize the browser window
    request.cls.driver = driver  # Attach the driver instance to the test class
    yield
    if driver:
        driver.close()  # Close the browser after the test


def pytest_addoption(parser):
    """
    Adds custom command-line options to pytest.
    """
    parser.addoption("--browser", help="Browser to run tests on (chrome, firefox, edge)", required=True)
    parser.addoption("--url", help="URL to test", required=True)


@pytest.fixture(scope="class", autouse=True)
def browser(request):
    """
    Returns the browser type specified in the pytest command line arguments.
    """
    return request.config.getoption("--browser")


@pytest.fixture(scope="class", autouse=True)
def url(request):
    """
    Returns the URL specified in the pytest command line arguments.
    """
    return request.config.getoption("--url")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    Hook to add a screenshot and additional HTML to the pytest HTML report on test failure.
    """
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    if report.when == "call":  # During the execution phase of the test
        extra.append(pytest_html.extras.url("http://www.rcvacademy.com/"))  # Add example link
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # On test failure, add a screenshot to the report
            report_directory = os.path.dirname(item.config.option.htmlpath)
            file_name = f"{int(time.time() * 1000)}.png"
            destination_file = os.path.join(report_directory, file_name)
            if driver:
                driver.save_screenshot(destination_file)
            if file_name:
                html = (
                    f'<div><img src="{file_name}" alt="screenshot" style="width:300px;height:200px" '
                    f'onclick="window.open(this.src)" align="right"/></div>'
                )
                extra.append(pytest_html.extras.html(html))
        report.extra = extra


def pytest_html_report_title(report):
    """
    Customizes the title of the pytest HTML report.
    """
    report.title = "RCV Academy Automation Report"
