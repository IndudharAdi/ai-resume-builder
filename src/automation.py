from dataclasses import dataclass
from typing import Dict, Optional

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
except ImportError:
    webdriver = None
    By = None


@dataclass
class ApplicationData:
    name: str
    email: str
    phone: str
    cover_letter: str
    resume_path: str
    extras: Optional[Dict[str, str]] = None


def submit_application(url: str, data: ApplicationData):
    if webdriver is None:
        raise RuntimeError("selenium is not installed. Install requirements first.")

    driver = webdriver.Chrome()
    driver.get(url)

    try:
        driver.find_element(By.NAME, "name").send_keys(data.name)
        driver.find_element(By.NAME, "email").send_keys(data.email)
        driver.find_element(By.NAME, "phone").send_keys(data.phone)
        driver.find_element(By.NAME, "cover_letter").send_keys(data.cover_letter)
        driver.find_element(By.NAME, "resume").send_keys(data.resume_path)

        if data.extras:
            for field, value in data.extras.items():
                try:
                    driver.find_element(By.NAME, field).send_keys(value)
                except Exception:
                    continue

        driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()
    finally:
        driver.quit()
