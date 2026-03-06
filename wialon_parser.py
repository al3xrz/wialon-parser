from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import asyncio
import aiohttp
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import settings
import logging


buffer = []

logger = logging.getLogger("wialon_parser")


def get_buffer():
    return buffer


async def get_sid(main_url: str, login: str, password: str) -> str | None:
    logging.info(f"MAIN_URL={settings.MAIN_URL} LOGIN={settings.LOGIN}")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # без GUI
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")  # обязательно в Linux/Docker
        chrome_options.add_argument("--disable-dev-shm-usage")  # уменьшает ошибки памяти /dev/shm
        
        # Создание драйвера через менеджер
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(main_url)
        user_input = driver.find_element(By.ID, "user")
        user_input.clear()
        user_input.send_keys(login)
        password_input = driver.find_element(By.ID, "passw")
        password_input.clear()
        password_input.send_keys(password)
        submit_input = driver.find_element(By.ID, "submit")
        submit_input.click()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "logo")))
        cookies = driver.get_cookies()
        # pprint(cookies)
        sid_cookie = next(
            filter(lambda x: x["name"] == "sessions", cookies), None)
        await asyncio.sleep(0.5)
        if sid_cookie:
            return sid_cookie["value"]
    except Exception as e:
        logger.error(f"Ошибка при получении нового sid: {e}")
        await asyncio.sleep(10)
        raise Exception("Ошибка получения sid")
    finally:
        driver.quit()


async def get_objects():
    sid = ""
    url = f"{settings.MAIN_URL}/wialon/ajax.html"
    # загружаем sid из файла
    try:
        with open("./last_sid.json", "r", encoding="utf-8") as sid_file:
            sid_item = json.load(sid_file)
            sid = sid_item["value"]
    except FileNotFoundError:
        logger.warning("SID файл не найден")
    except:
        logger.warning("Сохраненный sid не найден")

    async with aiohttp.ClientSession() as session:
        while True:
            params = {
                "svc": "core/search_items",
                "params": json.dumps({
                    "spec": {
                        "itemsType": "avl_unit",
                        "propName": "sys_name",
                        "propValueMask": "*",
                        "sortType": "sys_name"
                    },
                    "force": 1,
                    "flags": 0x1 + 0x256 + 0x512,  # базовые данные + позиции + треки
                    "from": 0,
                    "to": 0
                }, ensure_ascii=False),
                "sid": sid
            }

            try:
                async with session.get(url, params=params, timeout=settings.SESSION_TIMEOUT) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
            except Exception as e:
                print(f"Ошибка запроса: {e}")
                await asyncio.sleep(settings.SLEEP_TIME)
                continue

            global buffer
            if "items" in data:
                buffer.clear()
                buffer.extend(data["items"])
                logging.info(f"Данные обновлены {datetime.now()}. Емкость буфера: {len(buffer)}")
            if "error" in data:
                logger.info("sid устарел, получаем новый")
                try:
                    sid = await get_sid(main_url=settings.MAIN_URL, login=settings.LOGIN, password=settings.PASSWORD)
                    logger.info(f"новый sid = {sid}")
                    with open("./last_sid.json", "w", encoding="utf-8") as sid_file:
                        json.dump({"value": sid}, sid_file)
                except Exception as e:
                    continue

            await asyncio.sleep(settings.SLEEP_TIME)
