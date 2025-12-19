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
    geo = get_geo_data()
    channel_name = decode_channel_name("YnJ1dGFsbGVz")
    twitch_url = f"https://www.twitch.tv/{channel_name}"
    youtube_url = f"https://www.youtube.com/@{channel_name}/live"

    while run_session(twitch_url, youtube_url, geo):
        continue


if __name__ == "__main__":
    main()
