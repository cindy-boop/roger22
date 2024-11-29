import undetected_chromedriver as uc
import bs4, time, os, subprocess, requests, logging

from telethon import TelegramClient, types, events

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Replace these with your own values
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

def ini_logger(title: str) -> logging.Logger:
    class CustomFormatter(logging.Formatter):
        GREEN = "\033[32m"
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        )

        FORMATS = {
            logging.DEBUG: grey + format + reset,
            logging.INFO: GREEN + format + reset,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
            logging.CRITICAL: bold_red + format + reset,
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)


    # create logger with 'spam_application'
    logger = logging.getLogger(title)
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    return logger

def get_page_source(url: str = "https://google.com"):
    # Set up the WebDriver for Firefox
    options = Options()
    options.add_argument("-private")
    # Uncomment the line below if you want to run in headless mode
    # options.add_argument("--headless")

    # Create a new instance of the Firefox driver
    d = webdriver.Firefox(service=FirefoxService(), options=options)
    # d = uc.Chrome(version_main=129)
    d.get(url)
    try:
        WebDriverWait(d, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    except Exception as e:
        print(f"An error occurred: {e}")

    return d


def read_urls(file_path):
    """Read URLs from a file and return a list."""
    with open(file_path, "r") as file:
        return file.read().splitlines()


def get_download_url(urls):
    """Extract the download URL and telegram URL from the list of URLs."""
    download_url = [u for u in urls if "filemoon.in" in u]
    telegram_url = [u for u in urls if "telegram.php" in u]
    return download_url, telegram_url


def slug_exists(slug):
    """Check if the slug already exists in the database."""
    response = requests.get(
        f"https://kv-for-slug.caileespaney-totucosag.workers.dev/get?key={slug}"
    )
    return True if response.status_code == 200 and response.json() else False


def store_slug(slug):
    """Store the slug in the database after a successful download."""

    params = {"value": slug}
    requests.put(
        f"https://kv-for-slug.caileespaney-totucosag.workers.dev/set?key={slug}",
        json=params,
    )


def download_files(download_urls, slugs, driver):
    """Download the files using the given download URLs."""

    log = ini_logger('DOWNLOAD')
    for download_url, slug in zip(download_urls, slugs):
        filemoon_download_url = download_url.replace("filemoon.in", "filemoon.sx")
        driver.get(filemoon_download_url)
        driver.set_window_size(667, 667)

        while True:
            try:
                # Check if the page title indicates a not found page
                if "Not Found" in driver.title:
                    log.error(f"Download page not found for {slug}. Skipping.")
                    break

                # Wait until the download link is present
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "a.button[download]")
                    )
                )

                log.info(f"Download link appeared for {slug}.")
                download_link = element.get_attribute("href")
                filename = f"{slug}.mp4"

                # Execute the download command
                result = os.system(
                    f"bash mcurl.sh -s 8 -o '{filename}' '{download_link}'"
                )

                if result == 0:
                    log.info(f"Downloaded: {filename}")
                    store_slug(slug)  # Store the slug after successful download
                    # Start the upload script
                    process = subprocess.Popen(["python", "upload.py", filename])

                    # Wait for a short time to check if the process has started
                    time.sleep(1)  # Adjust the sleep time as necessary

                    # Check if the process is still running
                    if process.poll() is None:
                        log.info("Upload script started successfully.")
                    else:
                        time.sleep(5)
                        log.error("Failed to start upload script.")
                        break
                        # Handle the error as needed

                    # Continue with the rest of your code here

                else:
                    log.error(f"Download failed for {slug} with status: {result}")
                    store_slug(slug)

                break  # Exit the loop if the element is found
            except Exception as e:
                log.warning(f"Lagi nungguin download link nya {slug}")


def download():
    urls = read_urls("downlinks.txt")
    driver = get_page_source()  # Assuming this initializes your Selenium WebDriver

    download_urls = []
    slugs = []

    for i, url_line in enumerate(urls, start=1):
        urls = url_line.split(",")
        slug = urls[0]

        # Check if the slug already exists
        if slug_exists(slug):
            print(f"Skipping {slug} (already downloaded).")
            continue

        download_url, telegram_url = get_download_url(urls)

        if telegram_url:
            print(f"Skipping {slug} (Telegram URL found).")
            continue

        if download_url:
            print(f"Processing {slug} ({i}/{len(urls)})...")
            download_urls.append(download_url[0])  # Store the first valid download URL
            slugs.append(slug)  # Store the corresponding slug

            # Check if we have collected 7 URLs
            if len(download_urls) >= 7:
                print(
                    f"Collected {len(download_urls)} download URLs. Starting downloads..."
                )
                download_files(download_urls, slugs, driver)
                # Reset the lists after downloading
                download_urls = []
                slugs = []
        else:
            print(f"No valid download link found for {slug}.")

    # Check if there are any remaining URLs to download after the loop
    if download_urls:
        print(f"Starting downloads for the last batch of {len(download_urls)} URLs...")
        download_files(download_urls, slugs, driver)


# Example of how to call the function
if __name__=="__main__":
    download()
    # store_slug('32018')