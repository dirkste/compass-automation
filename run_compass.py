from core import driver_manager
from pages.login_page import LoginPage
from config.config_loader import get_config  # correct import
from utils.logger import log

def main():
    log.info("Starting Compass automation...")

    driver = driver_manager.get_or_create_driver()
    log.debug(f"Driver obtained: {driver}")

    login_page = LoginPage(driver)
    log.info("Login page loaded.")
    login_page.ensure_ready(
        get_config("username"),
        get_config("password"),
        get_config("login_id"),
    )
    log.info("Login page ready.")

    log.info("Automation run complete.")

if __name__ == "__main__":
    main()
