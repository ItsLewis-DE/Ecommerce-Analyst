from selenium import webdriver
import time

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
driver = webdriver.Chrome(options=options)

driver.get("https://www.topcv.vn")
time.sleep(10)

logs = driver.get_log("performance")
import json
for log in logs:
    log_json = json.loads(log["message"])["message"]
    if log_json["method"] == "Network.requestWillBeSent":
        url = log_json["params"]["request"]["url"]
        if "featured" in url or "api" in url:
            print(url)
driver.quit()
