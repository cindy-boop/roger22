const { chromium, firefox } = require("playwright-core");
const { solve } = require("recaptcha-solver");

async function main() {
    const EXAMPLE_PAGE = process.argv[2];
    if (!EXAMPLE_PAGE) {
        console.error("Please provide a URL as an argument.");
        process.exit(1);
    }

    const browser = await firefox.launch({ headless: false });
    const page = await browser.newPage();

    try {
        await page.goto(EXAMPLE_PAGE);
        await solve(page);

        // Submit the form
        await page.$eval("#F1", form => form.submit());

        // Wait for navigation after form submission
        await page.waitForNavigation({ waitUntil: 'networkidle' });

        let downloadUrl = null;
        
        // Loop until the download URL appears
        while (!downloadUrl) {
            // Extract the download URL
            downloadUrl = await page.evaluate(() => {
                const linkElement = document.querySelector('a.button[download]'); // Update selector as needed
                return linkElement ? linkElement.href : null;
            });

            if (!downloadUrl) {
                console.log("Download URL not found, refreshing...");
                await page.reload({ waitUntil: 'networkidle' });
                await page.waitForTimeout(2000); // Wait for 2 seconds before checking again
            }
        }
        console.log(downloadUrl);

    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        await browser.close();
        process.exit(0);
    }
}

main();