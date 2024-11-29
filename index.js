import { chromium, firefox } from "playwright-core";
import { solve } from "recaptcha-solver";

const EXAMPLE_PAGE = "https://filemoon.in/download/twt0zg0f130o";

async function main() {
    const browser = await firefox.launch({ headless: false });
    const page = await browser.newPage();

    try {
        await page.goto(EXAMPLE_PAGE);

        console.time("solve reCAPTCHA");
        await solve(page);
        console.log("solved!");
        console.timeEnd("solve reCAPTCHA");

        await page.click("#F1");

        page.on("close", async () => {
            await browser.close();
            process.exit(0);
        });


    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        await browser.close();
        process.exit(0);
    }
}

main();