const { chromium, firefox } = require("playwright-core");
const { solve } = require("recaptcha-solver");


async function mulung(url, page) {
    await page.goto(EXAMPLE_PAGE);
    await solve(page);

    let downloadUrl = null;
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
}
async function main() {
    const EXAMPLE_PAGE = process.argv[2];
    if (!EXAMPLE_PAGE) {
        console.error("Please provide a URL as an argument.");
        process.exit(1);
    }

    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();

    try {
        await mulung(EXAMPLE_PAGE, page)

    } catch (error) {
        await mulung(EXAMPLE_PAGE, page)

    } 
}

main();