import pytest, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield d
    d.quit()

TESTS = [
    # SauceDemo
    dict(
        name="SauceDemo",
        url="https://www.saucedemo.com/",
        steps=lambda d, w: (
            d.find_element(By.ID, "user-name").send_keys("standard_user"),
            d.find_element(By.ID, "password").send_keys("secret_sauce"),
            d.find_element(By.ID, "login-button").click(),
        ),
        asserts=lambda d, w: (
            w.until(EC.url_contains("/inventory.html")),
            w.until(EC.presence_of_element_located((By.CLASS_NAME, "inventory_list")))
        )
    ),
    # The Internet (Herokuapp)
    dict(
        name="TheInternet",
        url="https://the-internet.herokuapp.com/login",
        steps=lambda d, w: (
            d.find_element(By.ID, "username").send_keys("tomsmith"),
            d.find_element(By.ID, "password").send_keys("SuperSecretPassword!"),
            d.find_element(By.CSS_SELECTOR, "button[type='submit']").click(),
        ),
        asserts=lambda d, w: (
            w.until(EC.visibility_of_element_located((By.ID, "flash"))),
        )
    ),
    # PracticeTestAutomation (flaky → retry simples)
    dict(
        name="PracticeTestAutomation",
        url="https://practicetestautomation.com/practice-test-login/",
        steps=lambda d, w: (
            d.find_element(By.ID, "username").send_keys("student"),
            d.find_element(By.ID, "password").send_keys("Password123"),
            d.find_element(By.ID, "submit").click(),
        ),
        asserts=lambda d, w: (
            w.until(EC.title_contains("Logged In Successfully")),
        ),
        retry=2  # tenta recarregar em caso de 502/timeout
    ),
    # OrangeHRM (case sensitive)
    dict(
        name="OrangeHRM",
        url="https://opensource-demo.orangehrmlive.com/",
        steps=lambda d, w: (
            d.find_element(By.NAME, "username").send_keys("Admin"),
            d.find_element(By.NAME, "password").send_keys("admin123"),
            d.find_element(By.CSS_SELECTOR, "button[type='submit']").click(),
        ),
        asserts=lambda d, w: (
            w.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "aside.oxd-sidepanel"))),
            w.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Dashboard')]")))
        )
    ),
]

@pytest.mark.parametrize("case", TESTS, ids=[c["name"] for c in TESTS])
def test_logins(case, driver):
    wait = WebDriverWait(driver, 15)
    attempts = 1 + case.get("retry", 0)

    last_err = None
    for _ in range(attempts):
        try:
            driver.get(case["url"])
            case["steps"](driver, wait)
            case["asserts"](driver, wait)
            return  # sucesso
        except Exception as e:
            last_err = e
            time.sleep(2)  # pequeno backoff
            driver.refresh()
    pytest.fail(f"Falhou no caso {case['name']}: {last_err}")