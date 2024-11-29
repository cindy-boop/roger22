const { chromium } = require("playwright-core");
const { solve } = require("recaptcha-solver");


function isValidDownloadUrl(url) {
    const regex = /^https:\/\/[a-z0-9]{8}\.[a-z0-9]{5}\.[a-z0-9]{5}\.cdn\d{3}\.com\/download\/$/;
    return regex.test(url);
}

async function mulung(url, page) {
    await page.goto(url);
    await solve(page);

    let downloadUrl = null;

    while (true) {
        try {
            // Log the current page content for debugging (optional)
            console.log("Current page content:", await page.content());

            // Extract the download URL
            downloadUrl = await page.evaluate(() => {
                const linkElement = document.querySelector('a.button[download]'); // Update selector as needed
                return linkElement ? linkElement.href : null;
            });

            if (downloadUrl) {
                if (isValidDownloadUrl(downloadUrl)){
                    console.log(downloadUrl);
                }
                return downloadUrl; // Return the download URL if found
            } else {
                console.log("Download URL not found, refreshing...");
                await page.reload({ waitUntil: 'networkidle' });
                await page.waitForTimeout(2000); // Wait for 2 seconds before checking again
            }
        } catch (error) {
            console.error("An error occurred while checking for the download link:", error);

            // Check if the page title indicates a not found page
            const title = await page.title();
            if (title.includes("Not Found")) {
                console.error("Download page not found. Skipping...");
                break; // Exit the loop if the page is not found
            }

            // Optional: Wait before retrying, adjust as needed
            await page.waitForTimeout(5000); // Wait for 5 seconds before retrying
        }
    }
}

async function main() {
    const EXAMPLE_PAGE = process.argv[2];
    if (!EXAMPLE_PAGE) {
        console.error("Please provide a URL as an argument.");
        process.exit(1);
    }

    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();

    // Keep calling mulung until it returns a valid download URL
    while (true) {
        try {
            const downloadUrl = await mulung(EXAMPLE_PAGE, page);
            if (downloadUrl) {
                if (isValidDownloadUrl(downloadUrl)){
                    console.log(downloadUrl);
                }
                
                break; // Exit the loop if a valid download URL is found
            }
        } catch (error) {
            console.error("An error occurred while trying to get the download URL:", error);
            console.log("Retrying...");
            await page.waitForTimeout(2000); // Adjust as needed
        }
    }

    await browser.close();
}

main();