import base64
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def setup_chrome_options():
    """Configure Chrome options for optimal PDF generation"""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Enable PDF viewing
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": os.getcwd(),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "print.always_print_as_image": False,
        },
    )
    return options


def save_pdf(driver, url, output_path):
    """Generate PDF from URL using Chrome's built-in PDF printer"""
    print(f"Processing: {url}")

    try:
        driver.get(url)
        time.sleep(2)  # Allow page to load

        # Configure print settings
        print_settings = {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True,
            "paperWidth": 8.27,  # A4 width
            "paperHeight": 11.69,  # A4 height
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
            "scale": 1.0,
        }

        # Generate PDF using Chrome's DevTools Protocol
        result = driver.execute_cdp_cmd("Page.printToPDF", print_settings)

        # Decode base64 data and save PDF
        pdf_data = base64.b64decode(result["data"])
        with open(output_path, "wb") as file:
            file.write(pdf_data)

        return True

    except Exception as e:
        print(f"Error generating PDF for {url}: {str(e)}")
        return False


def merge_pdfs(input_files, output_file):
    """Merge multiple PDFs using PyPDF2"""
    try:
        from PyPDF2 import PdfMerger

        merger = PdfMerger()

        for pdf in input_files:
            if os.path.exists(pdf):
                merger.append(pdf)

        merger.write(output_file)
        merger.close()
        return True

    except Exception as e:
        print(f"Error merging PDFs: {str(e)}")
        return False


def main():
    # Create temp directory
    temp_dir = "temp_pdfs"
    os.makedirs(temp_dir, exist_ok=True)

    # Setup Chrome
    options = setup_chrome_options()
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        # Generate URLs
        base_url = "https://haystack.deepset.ai/advent-of-haystack/day-"
        urls = [f"{base_url}{i}" for i in range(1, 11)]
        urls = ["https://haystack.deepset.ai/blog/agentic-rag-in-deepset-studio"]
        # Store PDF paths
        pdf_files = []

        # Generate individual PDFs
        for i, url in enumerate(urls, 1):
            pdf_path = os.path.join(temp_dir, f"day_{i}.pdf")
            if save_pdf(driver, url, pdf_path):
                pdf_files.append(pdf_path)

        # Merge PDFs
        if pdf_files:
            if merge_pdfs(pdf_files, "merged_haystack.pdf"):
                print("Successfully created merged_haystack.pdf")
            else:
                print("Failed to merge PDFs")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        driver.quit()

        # Cleanup
        for pdf in pdf_files:
            try:
                if os.path.exists(pdf):
                    os.remove(pdf)
            except Exception as e:
                print(f"Error removing {pdf}: {str(e)}")

        try:
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error removing temp directory: {str(e)}")


if __name__ == "__main__":
    main()
