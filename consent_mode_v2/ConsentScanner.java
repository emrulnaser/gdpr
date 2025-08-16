import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.JavascriptExecutor;

public class ConsentScanner {
    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("Please provide a URL to scan.");
            return;
        }
        String url = args[0];

        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless");
        WebDriver driver = new ChromeDriver(options);

        try {
            driver.get(url);
            Thread.sleep(10000); // Wait for dynamic content to load

            JavascriptExecutor js = (JavascriptExecutor) driver;

            String[] signals = {"ad_storage", "analytics_storage", "ad_user_data", "ad_personalization"};
            for (String signal : signals) {
                Object result = js.executeScript(
                    "var status = 'not found'; " +
                    "var dataLayer = window.dataLayer || (window.google_tag_manager && window.google_tag_manager.dataLayer); " +
                    "if (dataLayer) { " +
                    "  for (var i = 0; i < dataLayer.length; i++) { " +
                    "    var item = dataLayer[i]; " +
                    "    if (item && item.event === 'consent') { " +
                    "      if (item.consent && item.consent.update && item.consent.update['" + signal + "']) { " +
                    "        status = item.consent.update['" + signal + "']; " +
                    "        break; " +
                    "      } else if (item.consent && item.consent.default && item.consent.default['" + signal + "']) { " +
                    "        status = item.consent.default['" + signal + "']; " +
                    "      } " +
                    "    } " +
                    "  } " +
                    "} " +
                    "return status;"
                );
                System.out.println(signal + ": " + result.toString());
            }

        } catch (Exception e) {
            System.out.println("Error running Java scanner: " + e.getMessage());
        } finally {
            driver.quit();
        }
    }
}