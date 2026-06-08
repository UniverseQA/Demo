from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.webdriver import WebDriver

class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    def find_element(self, locator: tuple[str, str]):
        return self.wait.until(EC.presence_of_element_with_locator(locator))

    def click(self, locator: tuple[str, str]) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.find_element(locator).text
