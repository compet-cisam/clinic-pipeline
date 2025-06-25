from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from typing import Optional
from logger_config import get_logger


class Scraper:
    PATIENT_MENU_XPATH = '//*[@id="menu-collapse"]/li[3]/a'
    NEXT_PAGE_XPATH = (
        '//*[@id="app-patient-search"]/div/div[2]/div/div[5]/'
        "div/ngb-pagination/ul/li[10]/a"
    )
    TOTAL_PATIENTS_XPATH = (
        '//*[@id="app-patient-search"]/div/div[2]/div/div[3]/div[2]/div/div[1]/div/span'
    )
    BUTTON_XPATH = (
        '//*[@id="app-patient-search"]/div/div[2]/div/div[4]/'
        "div[1]/div/div[4]/div/div/button"
    )
    FILTER_INPUT_XPATH = '//*[@id="filterMode-1"]'
    DATE_HOUR_XPATH = '//*[@id="timeline"]/article/div[2]/div[2]/span/span[1]'
    MEDICAL_CARE_XPATH = (
        "/html/body/app-root/app-layout/div/section/app-ehra/div/"
        "div[4]/as-split/as-split-area/div/app-summary/div/div/"
        "inv-cli-timeline/div/section/article/div[2]/div[2]/"
        "span/span[3]"
    )

    def __init__(self, url: str, username: str, password: str, headless: bool = False):
        self.url = url
        self.username = username
        self.password = password
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.headless = headless
        self.logger = get_logger()

    def _setup_driver(self) -> None:
        """Initialize the Chrome WebDriver with options."""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=0")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            self.logger.error(f"Failed to create Chrome driver: {e}")
            self.logger.error(
                "Make sure Chrome and chromedriver are properly installed"
            )
            raise

    def login(self) -> bool:
        """
        Navigate to the URL and perform login.
        Returns True if login is successful, False otherwise.
        """
        try:
            if not self.driver:
                self._setup_driver()

            self.driver.get(self.url)

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            username_field = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[placeholder="Login"]')
                )
            )
            username_field.clear()
            username_field.send_keys(self.username)

            password_field = self.driver.find_element(
                By.CSS_SELECTOR, 'input[placeholder="Senha"]'
            )
            password_field.clear()
            password_field.send_keys(self.password)

            login_button = self.driver.find_element(
                By.CSS_SELECTOR, 'button[type="submit"]'
            )
            login_button.click()

            # Wait for login to complete - wait for URL to change or specific element
            try:
                self.wait.until(lambda driver: driver.current_url != self.url)
            except TimeoutException:
                # If URL doesn't change, wait for page to be ready
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        except TimeoutException:
            self.logger.error("Timeout waiting for login elements")
            return False
        except NoSuchElementException as e:
            self.logger.error(f"Could not find login element: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False

        return True

    def scrape_data(self, css_selector: str = None, xpath: str = None) -> list:
        """
        Scrape data from the current page using CSS selector or XPath.
        Returns a list of text content from matching elements.
        """
        if not self.driver:
            self.logger.error("Driver not initialized. Please login first.")
            return []

        try:
            elements = []

            if css_selector:
                elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
            elif xpath:
                elements = self.driver.find_elements(By.XPATH, xpath)
            else:
                self.logger.error("Please provide either css_selector or xpath")
                return []

            data = [
                element.text.strip() for element in elements if element.text.strip()
            ]
            return data

        except Exception as e:
            self.logger.error(f"Error scraping data: {e}")
            return []

    def navigate_to(self, url: str) -> bool:
        """Navigate to a specific URL."""
        try:
            if not self.driver:
                self._setup_driver()

            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {e}")
            return False

    def click_element(self, css_selector: str = None, xpath: str = None) -> bool:
        """Click an element by CSS selector or XPath."""
        try:
            if css_selector:
                element = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                )
            elif xpath:
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            else:
                self.logger.error("Please provide either css_selector or xpath")
                return False

            element.click()
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )
            return True

        except Exception as e:
            self.logger.warning(f"Error clicking element: {e}, trying with javascript")
            try:
                if css_selector:
                    element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
                elif xpath:
                    element = self.driver.find_element(By.XPATH, xpath)
                else:
                    self.logger.error("Please provide either css_selector or xpath")
                    return False
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e2:
                self.logger.error(f"Error clicking element with javascript: {e2}")
                return False

    def fill_form_field(
        self, value: str, css_selector: str = None, xpath: str = None
    ) -> bool:
        """Fill a form field with the given value."""
        try:
            if css_selector:
                element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                )
            elif xpath:
                element = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            else:
                self.logger.error("Please provide either css_selector or xpath")
                return False

            element.clear()
            element.send_keys(value)
            return True

        except Exception as e:
            self.logger.error(f"Error filling form field: {e}")
            return False

    def wait_for_element(
        self, css_selector: str = None, xpath: str = None, timeout: int = 10
    ) -> bool:
        """Wait for an element to be present on the page."""
        try:
            wait = WebDriverWait(self.driver, timeout)

            if css_selector:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                )
            elif xpath:
                wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            else:
                self.logger.error("Please provide either css_selector or xpath")
                return False

            return True

        except TimeoutException:
            self.logger.error("Timeout waiting for element")
            return False

    def get_page_source(self) -> str:
        """Get the current page source."""
        if self.driver:
            return self.driver.page_source
        return ""

    def take_screenshot(self, filename: str) -> bool:
        """Take a screenshot and save it to the specified filename."""
        try:
            if self.driver:
                self.driver.save_screenshot(filename)
                self.logger.info(f"Screenshot saved as {filename}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return False

    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed successfully")

    @staticmethod
    def cleanup_chrome_processes():
        """Kill any lingering Chrome processes that might be causing conflicts."""
        import subprocess

        logger = get_logger()

        try:
            # Kill Chrome processes
            subprocess.run(["pkill", "-f", "chrome"], check=False)
            subprocess.run(["pkill", "-f", "chromium"], check=False)
            logger.info("Chrome processes cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Chrome processes: {e}")

    @staticmethod
    def cleanup_temp_dirs():
        """Clean up temporary Chrome directories."""
        import tempfile
        import os
        import shutil
        import glob

        logger = get_logger()
        temp_dir = tempfile.gettempdir()
        chrome_dirs = glob.glob(os.path.join(temp_dir, "chrome_selenium_*"))

        for dir_path in chrome_dirs:
            try:
                shutil.rmtree(dir_path)
                logger.info(f"Cleaned up: {dir_path}")
            except Exception as e:
                logger.warning(f"Could not clean up {dir_path}: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close the browser."""
        self.close()

    def extract_patient_data(self) -> list:
        """
        Extract patient data following the workflow from t.txt.
        Returns a list of patient data dictionaries.
        """
        if not self.driver:
            self.logger.error("Driver not initialized. Please login first.")
            return []

        patient_data = []

        try:
            if not self.wait_for_spa_load():
                self.logger.warning(
                    "Failed to load SPA, attempting extraction anyway..."
                )

            if not self.navigate_to_patient_search():
                self.logger.error("Failed to navigate to patient search page")
                return []

            try:
                wait = WebDriverWait(self.driver, 15)
                total_patients_element = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="app-patient-search"]/div/div[2]/div/div[3]'
                            "/div[2]/div/div[1]/div/span",
                        )
                    )
                )
                total_patients_text = total_patients_element.text
                self.logger.info(f"Total patients found: {total_patients_text}")
            except TimeoutException:
                self.logger.warning("Could not find total patients element")
                # Try alternative approaches or return empty
                return []

            patient_menu = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="menu-collapse"]/li[3]/a')
                )
            )
            patient_menu.click()

            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )

            button = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="app-patient-search"]/div/div[2]/div/div[4]'
                        "/div[1]/div/div[4]/div/div/button",
                    )
                )
            )
            button.click()

            filter_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="filterMode-1"]'))
            )
            filter_input.click()

            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )

            try:
                date_hour_element = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="timeline"]/article/div[2]/div[2]/span/span[1]',
                        )
                    )
                )
                date_hour = date_hour_element.text
            except TimeoutException:
                date_hour = "Not found"
                self.logger.warning("Date/Hour element not found")

            try:
                medical_care_element = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/app-layout/div/section/app-ehra/div/"
                            "div[4]/as-split/as-split-area/div/app-summary/div/div/"
                            "inv-cli-timeline/div/section/article/div[2]/div[2]/"
                            "span/span[3]",
                        )
                    )
                )
                medical_care = medical_care_element.text
                self.logger.debug(f"Medical Care: {medical_care}")
            except TimeoutException:
                medical_care = "Not found"
                self.logger.warning("Medical care element not found")

            # Store the extracted data
            patient_record = {
                "total_patients": total_patients_text,
                "date_hour": date_hour,
                "medical_care": medical_care,
                "extraction_timestamp": self._get_current_timestamp(),
            }

            patient_data.append(patient_record)

        except TimeoutException as e:
            self.logger.error(f"Timeout while extracting patient data: {e}")
        except Exception as e:
            self.logger.error(f"Error extracting patient data: {e}")

        return patient_data

    def extract_all_patients_data(self) -> list:
        """
        Extract data for all patients by iterating through pages and patients.
        Implements pagination to get all available patient data.

        FIXME not yet useful

        """
        if not self.driver:
            self.logger.error("Driver not initialized. Please login first.")
            return []

        all_patient_data = []
        current_page = 1
        max_pages = 100  # Safety limit to prevent infinite loops

        try:
            self.logger.info("Starting comprehensive patient data extraction...")

            if not self.wait_for_spa_load():
                self.logger.warning(
                    "Failed to load SPA, attempting extraction anyway..."
                )

            if not self.navigate_to_patient_search():
                self.logger.error("Failed to navigate to patient search page")
                return []

            total_patients = self.get_total_patients_count()
            self.logger.info(f"Total patients available: {total_patients}")

            while current_page <= max_pages:
                self.logger.info(f"--- Processing page {current_page} ---")

                patient_elements = self.get_patient_elements_on_page()

                if not patient_elements:
                    self.logger.warning(
                        "No patient elements found on current page, stopping..."
                    )
                    break

                self.logger.info(
                    f"Found {len(patient_elements)} patient elements on "
                    f"page {current_page}"
                )

                for i in range(len(patient_elements)):
                    try:
                        self.logger.info(
                            f"Processing patient {i + 1} on page {current_page}"
                        )

                        current_patient_elements = self.get_patient_elements_on_page()

                        if i >= len(current_patient_elements):
                            self.logger.warning(
                                f"Patient {i + 1} no longer available, skipping..."
                            )
                            continue

                        patient_element = current_patient_elements[i]
                        patient_data = self.extract_single_patient_data(
                            patient_element, current_page, i + 1
                        )

                        if patient_data:
                            patient_data["total_patients"] = total_patients
                            patient_data["page_number"] = current_page
                            patient_data["patient_index_on_page"] = i + 1
                            all_patient_data.append(patient_data)
                            self.logger.info(
                                f"Successfully extracted data for patient {i + 1}"
                            )
                        else:
                            self.logger.error(
                                f"Failed to extract data for patient {i + 1}"
                            )

                    except Exception as e:
                        self.logger.error(
                            f"Error processing patient {i + 1} on "
                            f"page {current_page}: {e}"
                        )
                        try:
                            self.navigate_back_to_patient_list()
                        except Exception:
                            pass
                        continue

                if not self.navigate_to_next_page():
                    self.logger.info(
                        "No more pages available or failed to navigate to next page"
                    )
                    break

                current_page += 1

            self.logger.info(
                f"Extraction completed! Total patient records extracted: "
                f"{len(all_patient_data)}"
            )
            self.logger.info(f"Processed {current_page} pages")

        except Exception as e:
            self.logger.error(f"Error in extract_all_patients_data: {e}")

        return all_patient_data

    def get_total_patients_count(self) -> str:
        """Get the total number of patients from the page."""
        try:
            wait = WebDriverWait(self.driver, 15)
            total_patients_element = wait.until(
                EC.presence_of_element_located((By.XPATH, self.TOTAL_PATIENTS_XPATH))
            )
            total_patients_text = total_patients_element.text
            self.logger.info(f"Total patients found: {total_patients_text}")
            return total_patients_text
        except TimeoutException:
            self.logger.warning("Could not find total patients element")
            return "Unknown"

    def get_patient_elements_on_page(self) -> list:
        pass  # FIXME not yet implemented

    def get_patient_clickable_elements(self) -> list:
        """
        Get clickable patient elements (not the navigation menu item).
        These are the actual patient records that can be clicked to view details.

        FIXME
        """
        pass

    def extract_single_patient_data(
        self, patient_element, page_num: int, patient_num: int
    ) -> dict:
        """
        Extract data for a single patient.
        Returns a dictionary with the patient's data or None if extraction fails.
        """
        try:
            self.logger.info(f"Clicking on patient {patient_num} on page {page_num}")

            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.element_to_be_clickable(patient_element))
            patient_element.click()

            self._wait_for_page_ready()

            try:
                # Check if we need to click on patient menu
                patient_menu = wait.until(
                    EC.element_to_be_clickable((By.XPATH, self.PATIENT_MENU_XPATH))
                )
                patient_menu.click()
                self._wait_for_page_ready()
            except TimeoutException:
                self.logger.debug("Patient menu already active or not found")

            button = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.BUTTON_XPATH))
            )
            button.click()

            filter_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.FILTER_INPUT_XPATH))
            )
            filter_input.click()

            self._wait_for_page_ready()

            try:
                date_hour_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, self.DATE_HOUR_XPATH))
                )
                date_hour = date_hour_element.text
                self.logger.debug(f"Date/Hour: {date_hour}")
            except TimeoutException:
                date_hour = "Not found"
                self.logger.warning("Date/Hour element not found")

            try:
                medical_care_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, self.MEDICAL_CARE_XPATH))
                )
                medical_care = medical_care_element.text
                self.logger.debug(f"Medical Care: {medical_care}")
            except TimeoutException:
                medical_care = "Not found"
                self.logger.warning("Medical care element not found")

            patient_record = {
                "date_hour": date_hour,
                "medical_care": medical_care,
                "extraction_timestamp": self._get_current_timestamp(),
            }

            if not self.navigate_back_to_patient_list():
                self.logger.warning("Could not navigate back to patient list")

            return patient_record

        except Exception as e:
            self.logger.error(f"Error extracting data for patient {patient_num}: {e}")
            try:
                self.navigate_back_to_patient_list()
            except Exception:
                pass
            return None

    def navigate_to_next_page(self) -> bool:
        """
        Navigate to the next page using the pagination button.
        Returns True if successful, False if no next page or navigation failed.
        """
        try:
            wait = WebDriverWait(self.driver, 10)

            # Scroll to make sure pagination is visible
            try:
                pagination_xpath = (
                    '//*[@id="app-patient-search"]/div/div[2]/div/'
                    "div[5]/div/ngb-pagination"
                )
                pagination_container = self.driver.find_element(
                    By.XPATH, pagination_xpath
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    pagination_container,
                )
                # Wait a moment for scroll to complete
                wait.until(lambda driver: True)  # Short wait
            except Exception:
                self.logger.warning("Could not scroll to pagination, trying anyway...")

            next_button_selectors = [
                self.NEXT_PAGE_XPATH,  # Original XPath
                "//a[@aria-label='Next']",  # Common pagination pattern
                "//a[contains(text(), 'Next')]",  # Text-based
                # Bootstrap pagination next button
                "//a[contains(@class, 'page-link') and contains(text(), '›')]",
                # Last page link in ngb-pagination
                "//ngb-pagination//a[contains(@class, 'page-link')][last()]",
                "//li[contains(@class, 'page-item')][last()]//a",  # Last pagination item
            ]

            next_page_button = None
            for selector in next_button_selectors:
                try:
                    button = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if button.is_displayed() and button.is_enabled():
                        next_page_button = button
                        self.logger.debug(
                            f"Found next page button using selector: {selector}"
                        )
                        break
                except TimeoutException:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {e}")
                    continue

            if not next_page_button:
                self.logger.warning("Could not find next page button")
                return False

            # Check if the button is enabled (not disabled)
            button_class = next_page_button.get_attribute("class")
            parent_class = ""
            try:
                parent_element = next_page_button.find_element(By.XPATH, "..")
                parent_class = parent_element.get_attribute("class") or ""
            except Exception:
                pass

            button_disabled = button_class and "disabled" in button_class
            parent_disabled = parent_class and "disabled" in parent_class
            if button_disabled or parent_disabled:
                self.logger.info("Next page button is disabled - no more pages")
                return False

            self.logger.info("Clicking next page button...")

            # Try JavaScript click if regular click fails
            try:
                next_page_button.click()
            except Exception as e:
                self.logger.warning(
                    f"Regular click failed: {e}. Trying JavaScript click..."
                )
                self.driver.execute_script("arguments[0].click();", next_page_button)

            # Wait for the new page to load
            self._wait_for_page_ready()

            # Wait for patient elements to be present on new page
            wait.until(EC.presence_of_element_located((By.ID, "app-patient-search")))

            self.logger.info("Successfully navigated to next page")
            return True

        except TimeoutException:
            self.logger.info(
                "Next page button not found or not clickable - assuming last page"
            )
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to next page: {e}")
            return False

    def _wait_for_page_ready(self):
        """Helper method to wait for page to be completely loaded."""
        return self.wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for data extraction."""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def wait_for_spa_load(self, timeout=15):
        """Wait for Single Page Application to fully load after login."""
        self.logger.info("Waiting for SPA to load...")

        try:
            wait = WebDriverWait(self.driver, timeout)

            wait.until(EC.presence_of_element_located((By.TAG_NAME, "app-root")))
            self.logger.debug("App root found!")

            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "app-root")))

            self.take_screenshot("spa_loading_debug.png")

            try:
                wait.until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, "loading"))
                )
            except TimeoutException:
                pass  # Loading indicator might not exist

            try:
                wait.until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, "spinner"))
                )
            except TimeoutException:
                pass  # Spinner might not exist

            self.logger.info("SPA fully loaded!")
            return True

        except TimeoutException:
            self.logger.error("App root not found within timeout")
            self.take_screenshot("spa_loading_debug.png")
            return False

    def navigate_to_patient_search(self):
        """Navigate to the patient search page if not already there."""
        self.logger.info("Attempting to navigate to patient search...")

        try:
            wait = WebDriverWait(self.driver, 10)
            menu_collapse = wait.until(
                EC.presence_of_element_located((By.ID, "menu-collapse"))
            )
            self.logger.debug("Found navigation menu")

            menu_items = menu_collapse.find_elements(By.TAG_NAME, "li")
            self.logger.debug(f"Found {len(menu_items)} menu items")

            if len(menu_items) >= 3:
                patient_menu_link = menu_items[2].find_element(By.TAG_NAME, "a")
                self.logger.info("Clicking on patient menu...")
                patient_menu_link.click()

                try:
                    wait = WebDriverWait(self.driver, 10)
                    wait.until(
                        EC.presence_of_element_located((By.ID, "app-patient-search"))
                    )
                    self.logger.info("Successfully navigated to patient search!")
                    return True
                except TimeoutException:
                    self.logger.warning(
                        "Patient search app still not found after navigation"
                    )
                    return False
            else:
                self.logger.error("Not enough menu items found")
                return False

        except TimeoutException:
            self.logger.error("Navigation menu not found")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to patient search: {e}")
            return False

    def navigate_back_to_patient_list(self) -> bool:
        """
        Navigate back to the patient search/list page after extracting patient data.
        Returns True if successful, False otherwise.
        """
        try:
            wait = WebDriverWait(self.driver, 10)

            try:
                self.driver.back()
                self._wait_for_page_ready()

                wait.until(
                    EC.presence_of_element_located((By.ID, "app-patient-search"))
                )
                self.logger.info(
                    "Successfully navigated back using browser back button"
                )
                return True
            except TimeoutException:
                self.logger.warning(
                    "Browser back button didn't work, trying other approaches..."
                )

            try:
                if not self.navigate_to_patient_search():
                    self.logger.error("Could not navigate to patient search via menu")
                    return False
                self.logger.info("Successfully navigated back via patient search menu")
                return True
            except Exception as e:
                self.logger.error(f"Error navigating via menu: {e}")

            try:
                current_url = self.driver.current_url
                self.driver.get(current_url)
                self._wait_for_page_ready()

                # Wait for patient search to be available
                wait.until(
                    EC.presence_of_element_located((By.ID, "app-patient-search"))
                )
                self.logger.info("Successfully navigated back by reloading page")
                return True
            except Exception as e:
                self.logger.error(f"Error reloading page: {e}")

            return False

        except Exception as e:
            self.logger.error(f"Error in navigate_back_to_patient_list: {e}")
            return False
