from seleniumbase import SB
import random
import base64
import requests
from seleniumbase import SB
import random
import base64
import requests

def get_geo_data():
    """Fetch geolocation and timezone information based on current IP."""
    response = requests.get("http://ip-api.com/json/")
    response.raise_for_status()
    data = response.json()
    return {
        "latitude": data["lat"],
        "longitude": data["lon"],
        "timezone": data["timezone"],
        "language_code": data["countryCode"].lower(),
    }


def decode_channel_name(encoded: str) -> str:
    """Decode a base64-encoded channel name."""
    return base64.b64decode(encoded).decode("utf-8")


def setup_driver(url: str, tz: str, lat: float, lon: float) -> SB:
    """Initialize a SeleniumBase driver with CDP mode activated."""
    driver = SB(uc=True, locale="en", ad_block=True, chromium_arg="--disable-webgl")
    driver.activate_cdp_mode(url, tzone=tz, geoloc=(lat, lon))
    return driver


def handle_consent(driver: SB):
    """Click consent or start buttons if present."""
    if driver.cdp.is_element_present('button:contains("Start Watching")'):
        driver.cdp.click('button:contains("Start Watching")', timeout=4)
        driver.sleep(10)
    if driver.cdp.is_element_present('button:contains("Accept")'):
        driver.cdp.click('button:contains("Accept")', timeout=4)


def run_session(twitch_url: str, youtube_url: str, geo: dict):
    """Run a full viewing session across Twitch and YouTube."""
    with setup_driver(twitch_url, geo["timezone"], geo["latitude"], geo["longitude"]) as driver:
        driver.sleep(10)
        handle_consent(driver)

        if driver.cdp.is_element_present("#live-channel-stream-information"):
            # Secondary Twitch driver
            twitch_driver = driver.get_new_driver(undetectable=True)
            twitch_driver.activate_cdp_mode(
                twitch_url, tzone=geo["timezone"], geoloc=(geo["latitude"], geo["longitude"])
            )
            twitch_driver.sleep(10)
            handle_consent(twitch_driver)

            # YouTube driver
            yt_driver = driver.get_new_driver(undetectable=True)
            yt_driver.activate_cdp_mode(
                youtube_url, tzone=geo["timezone"], geoloc=(geo["latitude"], geo["longitude"])
            )
            yt_driver.sleep(10)
            if yt_driver.cdp.is_element_present('button:contains("Accept")'):
                yt_driver.cdp.click('button:contains("Accept")', timeout=4)
                yt_driver.sleep(10)
            else:
                yt_driver.sleep(10)
                yt_driver.cdp.gui_press_key("K")

            driver.sleep(random.randint(450, 900))
            driver.quit_extra_driver()
        else:
            return False
    return True


def main():

    
    # grab geo info
    geo_info = requests.get("http://ip-api.com/json/").json()
    lat = geo_info["lat"]
    lon = geo_info["lon"]
    tz = geo_info["timezone"]
    lang = geo_info["countryCode"].lower()
    
    # decode the name
    encoded_name = "YnJ1dGFsbGVz"
    decoded_bytes = base64.b64decode(encoded_name)
    decoded_name = decoded_bytes.decode("utf-8")
    
    # make urls
    twitch_url = "https://www.twitch.tv/" + decoded_name
    yt_url = "https://www.youtube.com/@" + decoded_name + "/live"
    
    # loop forever until break
    while True:
        # open browser
        with SB(uc=True, locale="en", ad_block=True, chromium_arg="--disable-webgl") as driver:
            # random wait time
            wait_time = random.randint(450, 900)
    
            # activate cdp mode
            driver.activate_cdp_mode(twitch_url, tzone=tz, geoloc=(lat, lon))
    
            driver.sleep(10)
    
            # check buttons
            if driver.cdp.is_element_present('button:contains("Start Watching")'):
                driver.cdp.click('button:contains("Start Watching")', timeout=4)
                driver.sleep(10)
    
            if driver.cdp.is_element_present('button:contains("Accept")'):
                driver.cdp.click('button:contains("Accept")', timeout=4)
    
            # check if live stream info exists
            if driver.cdp.is_element_present("#live-channel-stream-information"):
                # accept again if needed
                if driver.cdp.is_element_present('button:contains("Accept")'):
                    driver.cdp.click('button:contains("Accept")', timeout=4)
    
                # open another driver
                d2 = driver.get_new_driver(undetectable=True)
                d2.activate_cdp_mode(twitch_url, tzone=tz, geoloc=(lat, lon))
                d2.sleep(10)
    
                if d2.cdp.is_element_present('button:contains("Start Watching")'):
                    d2.cdp.click('button:contains("Start Watching")', timeout=4)
                    d2.sleep(10)
    
                if d2.cdp.is_element_present('button:contains("Accept")'):
                    d2.cdp.click('button:contains("Accept")', timeout=4)
    
                driver.sleep(10)
    
                # third driver for youtube
                d3 = driver.get_new_driver(undetectable=True)
                d3.activate_cdp_mode(yt_url, tzone=tz, geoloc=(lat, lon))
                d3.sleep(10)
    
                if d3.cdp.is_element_present('button:contains("Accept")'):
                    d3.cdp.click('button:contains("Accept")', timeout=4)
                    d3.sleep(10)
                else:
                    d3.sleep(10)
                    d3.cdp.gui_press_key("K")
    
                driver.sleep(wait_time)
                driver.quit_extra_driver()
            else:
                break



if __name__ == "__main__":
    main()
