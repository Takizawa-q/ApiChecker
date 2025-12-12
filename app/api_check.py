import asyncio
import time

from config import config
from logger import log
from req_session import RequestSession

ERROR_MESSAGES = [
    "Input should be a valid dictionary or object to extract fields from",]


class WbConApiClient():
    def __init__(self, mail: str, password: str):
        self.session = RequestSession(verify=False)
        self.endpoints_status = {}
        self.mail = mail
        self.password = password
        self.default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.params = {"email": self.mail, "password": self.password}

    async def _request(self, method: str, endpoint: str, *args, **kwargs):
        """Generic request method for all HTTP methods"""
        if endpoint not in self.endpoints_status:
            self.endpoints_status[endpoint] = {"status": None, "time": 0}

        # Extract and remove keys from kwargs if present
        expected_keys = kwargs.pop('keys', None)
        check_empty_string = kwargs.pop('check_empty_string', False)
        extra_headers = kwargs.pop('extra_headers', {})
        is_binary = kwargs.pop('is_binary', False)

        # Get the session method (get, post, etc.)
        session_method = getattr(self.session, method.lower())

        # Merge headers
        headers = {**self.default_headers, **extra_headers}
        start_time = time.time()
        try:
            r = await session_method(
                url=endpoint,
                headers=headers,
                params=self.params,
                timeout=60,
                *args,
                **kwargs
            )
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.endpoints_status[endpoint]["time"] = elapsed_time
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                self.endpoints_status[endpoint]["status"] = "Timeout"
                log.warning(f"Timeout: {endpoint.split('/')[2]}")
            elif "connection" in error_msg:
                self.endpoints_status[endpoint]["status"] = "Connection Error"
                log.warning(f"ConnErr: {endpoint.split('/')[2]}")
            else:
                self.endpoints_status[endpoint]["status"] = f"Error: {str(e)[:50]}"
                log.error(f"{endpoint.split('/')[2]}: {str(e)[:50]}")
            return
        elapsed_time = time.time() - start_time
        self.endpoints_status[endpoint]["time"] = elapsed_time

        # Binary response (video, file) - just check it has content
        if is_binary:
            if len(r.content) > 0:
                self.endpoints_status[endpoint]["status"] = "Success"
            else:
                self.endpoints_status[endpoint]["status"] = "Пустой файл"
            return

        # Check for error messages in response text
        if "failed to receive" in r.text.lower():
            self.endpoints_status[endpoint]["status"] = "Error: Failed to receive"
            return

        # Check for rate limit error
        if "rate limit exceeded" in r.text.lower():
            self.endpoints_status[endpoint]["status"] = "Rate limit exceeded"
            return
        
        print(r.text[1:200])
        if r.status_code != 200:
            self.endpoints_status[endpoint]["status"] = r.status_code
            return
        # Try to parse JSON response
        try:
            response_data = r.json()
        except:
            if "not found" not in r.text.lower():
                self.endpoints_status[endpoint]["status"] = "Success"
                return

        # Check for expected keys in response
        if expected_keys:
            for key in expected_keys:
                if key not in str(response_data):
                    self.endpoints_status[endpoint]["status"] = f"Нет ключа: {key}"
                    return
                # Check if key value is empty list or empty dict
                if isinstance(response_data, dict) and key in response_data:
                    value = response_data[key]
                    if isinstance(value, (list, dict)) and len(value) == 0:
                        self.endpoints_status[endpoint]["status"] = f"Пустой: {key}"
                        return
                    # Check if value is empty string
                    if check_empty_string and isinstance(value, str) and value == "":
                        self.endpoints_status[endpoint]["status"] = "Пустой ответ"
                        return
                    # Check if results contain items with total=0
                    if key == "results" and isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and item.get("total") == 0:
                                self.endpoints_status[endpoint]["status"] = f"Пустой: {key}"
                                return

        self.endpoints_status[endpoint]["status"] = "Success"

    async def get(self, endpoint, *args, **kwargs):
        return await self._request("get", endpoint, *args, **kwargs)

    async def post(self, endpoint, *args, **kwargs):
        return await self._request("post", endpoint, *args, **kwargs)


class CheckEndpoints():

    def __init__(self, api_client: WbConApiClient):
        self.api_client = api_client


async def check_endpoints():
    """Check all endpoints and return status dict"""
    wbcon_api = WbConApiClient(
        mail=config.email,
        password=config.password
    )
    RESPONSES = {
        "https://01-wb-pr-quota.wbcon.su/quota": {
            "method": "post",
            "json": {
                "query_": {
                    "507": ["dst"],
                    "206348": ["src", "dst"],
                    "333333": ["src"]
                },
            },
            "keys": ["src", "dst"]

        },
        "https://01-wb-pr-quota.wbcon.su/stats": {
            "method": "post",
            "json": {
                "query_": {
                    "507": ["dst"],
                    "206348": ["src", "dst"],
                    "333333": ["src"]
                }
            },
            "keys": ["src", "dst"]
        },
        "https://01-na.wbcon.su/all_items": {
            "method": "get",
        },
        "https://01-na.wbcon.su/last_info": {
            "method": "post",
            "json": {
                "item": "Mesh системы"
            }
        },
        "https://01-na.wbcon.su/all_info": {
            "method": "post",
            "json": {
                "item": "Mesh системы"
            }
        },
        "https://01-wb-price-segments.wbcon.su/items/": {
            "method": "get",
            "keys": ["predmet"]
        },
        f"https://01-wb-price-segments.wbcon.su/get/?cat_id=5655": {
            "method": "get",
            "keys": ["parse_time"],
        },
        "https://01-wb-category-searches.wbcon.su/items/": {
            "method": "get",
            "keys": ["predmet"]
        },
        "https://01-wb-category-searches.wbcon.su/get/?cat_id=644": {
            "method": "get",
            "keys": ["item_id", "predmet"]
        },
        "https://01-sellers.wbcon.su/inn?inn=9701197351": {
            "method": "get",
            "keys": ["inn"]
        },
        f"https://01-sellers.wbcon.su/ogrn?ogrn=321392600050191": {
            "method": "get",
            "keys": ["ogrn"]
        },
        "https://01-pvz.wbcon.su/get_all": {
            "method": "get",
            "keys": ["total", "ids"]
        },
        "https://01-pvz.wbcon.su/get/?id=22": {
            "method": "get",
            "keys": ["id", "locale"]
        },
        "https://01-comsa.wbcon.su/get": {
            "method": "get",
            "keys": ["category", "predmet"]
        },
        "https://01-comsa.wbcon.su/get_logistics_by_period?period=2025-11-25": {
            "method": "get",
            "keys": ["warehouse"]
        },
        "https://01-prices.wbcon.su/get?articles=539926571": {
            "method": "get",
            "keys": ["539926571"],
            "headers": {"wbtoken": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwOTA0djEiLCJ0eXAiOiJKV1QifQ.eyJhY2MiOjMsImVudCI6MSwiZXhwIjoxNzgwMDM5MTIzLCJmb3IiOiJzZWxmIiwiaWQiOiIwMTlhYzZjMC1lYjljLTc5ZTEtODUxZC0zMWJkOWY5YWNkMmIiLCJpaWQiOjExNjA5OTE4LCJvaWQiOjI1NjI0OCwicyI6MTA3Mzc1Nzk1MCwic2lkIjoiODlmOWQ2YTUtMTM4NS00MzJlLWJkN2YtNTE4MTViYzg1MWVkIiwidCI6ZmFsc2UsInVpZCI6MTE2MDk5MTh9.D3RJ0vQaBx4qyaZIwYAfEgAIUE2pv9TOIzmKf0md4y9hHvZbgNG9C6jFoLaLt5XWfln0KzrUW3muIpJ7RNidSg"}
        },

        "https://01-prices.wbcon.su/get?articles=141120711;171007032;170095992": {
            "method": "get",
            "keys": ["141120711"],
            "headers": {"wbtoken": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwOTA0djEiLCJ0eXAiOiJKV1QifQ.eyJhY2MiOjMsImVudCI6MSwiZXhwIjoxNzgwMDM5MTIzLCJmb3IiOiJzZWxmIiwiaWQiOiIwMTlhYzZjMC1lYjljLTc5ZTEtODUxZC0zMWJkOWY5YWNkMmIiLCJpaWQiOjExNjA5OTE4LCJvaWQiOjI1NjI0OCwicyI6MTA3Mzc1Nzk1MCwic2lkIjoiODlmOWQ2YTUtMTM4NS00MzJlLWJkN2YtNTE4MTViYzg1MWVkIiwidCI6ZmFsc2UsInVpZCI6MTE2MDk5MTh9.D3RJ0vQaBx4qyaZIwYAfEgAIUE2pv9TOIzmKf0md4y9hHvZbgNG9C6jFoLaLt5XWfln0KzrUW3muIpJ7RNidSg"}
        },
        "https://01-img.wbcon.su/get?article=36685165": {
            "method": "get",
            "keys": ["article"]
        },
        "https://01-rc.wbcon.su/get?article=36685165": {
            "method": "get",
            "keys": ["images_urls", "article"]
        },
        "https://01-wb-video.wbcon.su/get?article=445051493": {
            "method": "get",
            "is_binary": True
        },
        "https://01-fbphoto.wbcon.su/get?article=4737767": {
            "method": "get",
            "keys": ["article", "photos", "total"]
        },
        "https://01-fb.wbcon.su/create_task_fb": {
            "method": "post",
            "json": {"article": 117220345},
            "keys": ["created", "task_id"]
        },
        "https://01-fb.wbcon.su/task_status?task_id=1": {
            "method": "get",
            "keys": ["is_ready"]
        },
        "https://01-fb.wbcon.su/get_results_fb?task_id=1": {
            "method": "get",
            "keys": ["feedback_count", "feedbacks"]
        },
        "https://01-ais.wbcon.su/put": {
            "method": "post",
            "json": {
                "article_url": "https://www.wildberries.ru/catalog/266119079/detail.aspx",
                "geo": "msk",
                "search_query": "Детские игрушки"
            },
            "keys": ["article", "exists"]
        },
        "https://01-sa-day.wbcon.su/get_one/": {
            "method": "post",
            "json": {
                "date": "2025-11-29",
                "query": "кинетический песок"
            },
            "keys": ["search_words", "parse_date", "results"]
        },
        "https://01-sa.wbcon.su/get_one/": {
            "method": "post",
            "json": {
                "date": "2025-11-29",
                "query": "кинетический песок"
            },
            "keys": ["search_words", "parse_date", "results"]
        },
        "https://01-sa-day.wbcon.su/get_all/": {
            "method": "post",
            "json": {
                "date": "2025-11-29",
            },
            "keys": ["parse_date", "results"]
        },
        "https://01-cl.wbcon.su/get_similar/?search_query=женское платье черное": {
            "method": "get",
            "keys": ["searchQuery", "normalQuery", "totalMonthCount", "totalWeekCount", "similarSearches"]
        },
        "https://01-cl.wbcon.su/get_cluster/?search_query=женское платье черное": {
            "method": "get",
            "keys": ["searchQuery", "normalQuery"]
        },
        "https://01-500search.wbcon.su/get/": {
            "method": "post",
            "json": {
                "query": "кинетический песок"
            },
            "keys": ["query", "urls"]
        },
        "https://01-apis.wbcon.su/put": {
            "method": "post",
            "json": {
                "article": 124302872,
                "geo": "msk",
                "search_query": "носки"
            },
            # "keys": ["article", "position", "exists"]
        },
        "https://01-apis-ads.wbcon.su/find": {
            "method": "post",
            "json": {
                "article": "70416789",
                "geo": "msk",
                "search_query": "ковер"
            },
            "keys": ["article", "position", "exists"]
        },
        "https://01-coef.wbcon.su/get_coef": {
            "method": "post",
            "json": {
                "wh_id": 507,
                "delivery_date": "2024-03-30",
                "delivery_type": "koroba"
            },
            "keys": ["coef"]
        },
        "https://01-wbsug.wbcon.su/get?search_word=худи": {
            "method": "get",
            "keys": ["search_word", "total", "suggestions"]
        },
        "https://01-wbsim.wbcon.su/get?search_word=худи": {
            "method": "get",
            "keys": ["search_word", "total", "similars"]
        },
        "https://01-total.wbcon.su/put": {
            "method": "post",
            "json": {
                "search_query": "платье"
            },
            "keys": ["results"]
        },
        "https://01-barcode.wbcon.su/put": {
            "method": "post",
            "json": {
                "type": "pdf",
                "viewBarcode": True,
                "product": {
                    "barcode": "A205851764",
                    "name": "Классический костюм тройка деловой",
                    "width": 800,
                    "height": 400
                }
            },
            "keys": ["link"],
        },
        "https://01-qr.wbcon.su/put": {
            "method": "post",
            "json": {
                "type": "pdf",
                "viewBarcode": True,
                "product": {
                    "barcode": "A205851764",
                    "name": "Классический костюм тройка деловой",
                    "width": 800
                }
            },
            "keys": ["link"]
        },
        "https://01-etiketka.wbcon.su/put": {
            "method": "post",
            "json": {
                "viewBarcode": True,
                "barcode": "45896325",
                "name": "Обувь Кроссовки",
                "article": "4589633258",
                "manuf_name": "ООО Белвест",
                "brand": "БелвестОбувь",
                "size": "44",
                "color": "brown",
                "font_size": 16,
                "field_free": "Ботинки зимние меховые для мужчин",
                "width": 58,
                "height": 60
            },
            "keys": ["link"]
        },
        "https://01-oz.wbcon.su/put": {
            "method": "post",
            "json": {
                "article": 563429170
            },
            "keys": ["name"],
            "check_empty_string": True
        },
        "https://01-price-ozon.wbcon.su/put": {
            "method": "post",
            "json": {
                "article": 563429170
            },
            "keys": ["name"],
            "check_empty_string": True
        },
        "https://01-ozimg.wbcon.su/put": {
            "method": "post",
            "json": {
                "article": 563429170
            },
            "keys": ["article", "images_list"],
            "check_empty_string": True
        },
        "https://01-wb-seasons.wbcon.su/items": {
            "method": "get"},
        "https://01-wb-seasons.wbcon.su/get/?cat_id=5655": {
            "method": "get",
        }
    }
    # Первая итерация - оригинальные URL с 01-

    async def cents(api, data):
        method_name = data.get("method", None)
        _json = data.get("json", None)
        keys = data.get("keys", None)
        check_empty_string = data.get("check_empty_string", False)
        extra_headers = data.get("headers", {})
        is_binary = data.get("is_binary", False)
        method = getattr(wbcon_api, method_name)
        await method(api, json=_json, keys=keys, check_empty_string=check_empty_string, extra_headers=extra_headers, is_binary=is_binary)

    async def demo(api, data):
        if "01-" in api:
            api_without_prefix = api.replace("01-", "")
            # Для apis.wbcon.su DEMO версия использует /find вместо /put
            if "apis.wbcon.su/put" in api_without_prefix:
                api_without_prefix = api_without_prefix.replace(
                    "/put", "/find")
            method_name = data.get("method", None)
            _json = data.get("json", None)
            keys = data.get("keys", None)
            check_empty_string = data.get("check_empty_string", False)
            extra_headers = data.get("headers", {})
            is_binary = data.get("is_binary", False)
            method = getattr(wbcon_api, method_name)
            await method(api_without_prefix, json=_json, keys=keys, check_empty_string=check_empty_string, extra_headers=extra_headers, is_binary=is_binary)
    tasks = []
    for api, data in RESPONSES.items():
        tasks.append(asyncio.create_task(cents(api, data)))
        tasks.append(asyncio.create_task(demo(api, data))) 

    await asyncio.gather(*tasks)
    return wbcon_api.endpoints_status
