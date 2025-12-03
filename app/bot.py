
from datetime import datetime

# Маппинг URL на человекочитаемые названия API
API_NAMES = {
    "wb-seasons.wbcon.su/items": "Аналитика по предметам ВБ.",
    "wb-seasons.wbcon.su/get": "Аналитика по категориям ВБ.",
    "wb-pr-quota.wbcon.su/quota": "Мониторинг квот Перераспределения",
    "wb-pr-quota.wbcon.su/stats": "Мониторинг квот (статистика)",
    "na.wbcon.su": "ПОЛНЫЙ Анализ ниш Wildberries",
    "wb-price-segments.wbcon.su": "Популярные ценовые сегменты",
    "wb-category-searches.wbcon.su": "Популярные запросы по выручке",
    "sellers.wbcon.su": "База поставщиков",
    "pvz.wbcon.su": "База ПВЗ Wildberries",
    "pvz.wbcon.su": "База ПВЗ Wildberries",
    "comsa.wbcon.su": "Комиссии / Проценты от базы",
    "prices.wbcon.su": "Цены, скидки, СПП",
    "img.wbcon.su": "Ссылки на фото в товаре",
    "rc.wbcon.su": "Ссылки на RICH-контент",
    "wb-video.wbcon.su": "Ссылки на видео в товаре",
    "fbphoto.wbcon.su": "Ссылки на фото в отзывах",
    "fb.wbcon.su": "Парсер отзывов",
    "ais.wbcon.su": "Проверка наличия товара в поиске",
    "search-queries.wbcon.su": "История поисковых запросов",
    "search-queries-yesterday.wbcon.su": "Количество поисковых запросов за день",
    "cl.wbcon.su": "Поисковые кластеры",
    "sa.wbcon.su": "Поисковые запросы",
    "sa-day.wbcon.su/get_one": "Поисковые запросы за \"за вчера\"",
    "sa-day.wbcon.su/get_all": "Все поисковые запросы за \"за вчера\"",
    "500search.wbcon.su": "Первые 500 позиций в поиске",
    "apis.wbcon.su": "Позиция в поиске",
    "apis-ads.wbcon.su": "Позиция товара в поиске + реклама",
    "coef.wbcon.su": "Коэффициент приемки WB",
    "wbsug.wbcon.su": "Парсер поисковых подсказок",
    "wbsim.wbcon.su": "Парсер похожих запросов",
    "total.wbcon.su": "Количество товаров в запросе",
    "barcode.wbcon.su": "Генератор штрихкодов",
    "qr.wbcon.su": "Генератор QR-кодов",
    "etiketka.wbcon.su": "Генератор этикеток",
    "oz.wbcon.su": "Данные по карточкам товара на OZON",
    "price-ozon.wbcon.su/put": "Парсер цены на Ozon ",
    "ozimg.wbcon.su": "Ссылки на фото в товаре OZON",
    # "": "Ссылки на видео в товаре OZON"
}


def get_api_name(url: str) -> tuple[str, str]:
    """
    Возвращает название API и короткий URL

    Returns:
        tuple: (название, короткий_url)
    """
    # Извлекаем короткий URL без протокола
    short_url = url.split("//")[1] if "//" in url else url

    # Ищем соответствие в маппинге
    for key, name in API_NAMES.items():
        if key in short_url:
            return name, short_url

    # Если не найдено в маппинге, возвращаем домен
    domain = short_url.split("/")[0]
    return domain, short_url


def format_status_message(endpoints_status: dict) -> list[str]:
    """Format endpoints status for Telegram messages with HTML

    Returns:
        list: [paid_message, demo_message, summary_message]
    """
    # Разделяем endpoints на платные (01-) и DEMO (без 01-)
    paid_endpoints = {}
    demo_endpoints = {}
    for endpoint, data in endpoints_status.items():
        if "01-" in endpoint:
            paid_endpoints[endpoint] = data
        else:
            demo_endpoints[endpoint] = data

    messages = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # === Сообщение 1: Платные API (50 копеек) ===
    if paid_endpoints:
        paid_success = sum(1 for data in paid_endpoints.values()
                           if data["status"] == "Success")
        paid_error = len(paid_endpoints) - paid_success
        paid_total = len(paid_endpoints)
        paid_uptime = (paid_success / paid_total *
                       100) if paid_total > 0 else 0
        paid_total_time = sum(data["time"] for data in paid_endpoints.values())

        msg = "💰 <b>50 копеек</b>\n"
        msg += f"📅 {timestamp}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "<blockquote>"
        for endpoint, data in paid_endpoints.items():
            api_name, short_url = get_api_name(endpoint)
            status = data["status"]
            req_time = data["time"]
            time_str = f"{req_time:.2f}s"

            if status == "Success":
                msg += f"✅ <a href='{endpoint}'>{api_name}</a> <code>{time_str}</code>\n"
            elif "rate limit" in str(status).lower():
                msg += f"⚠️ <a href='{endpoint}'>{api_name}</a> <code>{time_str}</code> - <i>{status}</i>\n"
            else:
                msg += f"❌ <a href='{endpoint}'>{api_name}</a> <code>{time_str}</code> - <i>{status}</i>\n"
        msg += "</blockquote>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"📊 ✅ {paid_success}  ❌ {paid_error}  📈 {paid_uptime:.1f}%\n"
        msg += f"⏱ <i>Сумма: {paid_total_time:.2f}s | Среднее: {paid_total_time/paid_total:.2f}s</i>"
        messages.append(msg)

    # === Сообщение 2: DEMO API ===
    if demo_endpoints:
        demo_success = sum(1 for data in demo_endpoints.values()
                           if data["status"] == "Success")
        demo_error = len(demo_endpoints) - demo_success
        demo_total = len(demo_endpoints)
        demo_uptime = (demo_success / demo_total *
                       100) if demo_total > 0 else 0
        demo_total_time = sum(data["time"] for data in demo_endpoints.values())

        msg = "🆓 <b>DEMO</b>\n"
        msg += f"📅 {timestamp}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "<blockquote>"
        for endpoint, data in demo_endpoints.items():
            api_name, short_url = get_api_name(endpoint)
            status = data["status"]
            req_time = data["time"]
            time_str = f"{req_time:.2f}s"

            if status == "Success":
                msg += f"✅ <a href='{endpoint}'>{api_name}</a> <code>{time_str}</code>\n"
            elif "rate limit" in str(status).lower():
                msg += f"⚠️ <a href='{endpoint}'>{api_name}</a> <code>{time_str}</code> - <i>{status}</i>\n"
            else:
                msg += f"❌ <a href='{endpoint}'>{api_name}</a> <code>{time_str}</code> - <i>{status}</i>\n"
        msg += "</blockquote>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"📊 ✅ {demo_success}  ❌ {demo_error}  📈 {demo_uptime:.1f}%\n"
        msg += f"⏱ <i>Сумма: {demo_total_time:.2f}s | Среднее: {demo_total_time/demo_total:.2f}s</i>"
        messages.append(msg)

    # === Сообщение 3: Общая статистика ===
    total_count = len(endpoints_status)
    success_count = sum(1 for data in endpoints_status.values()
                        if data["status"] == "Success")
    error_count = total_count - success_count
    uptime_percent = (success_count / total_count *
                      100) if total_count > 0 else 0
    total_time = sum(data["time"] for data in endpoints_status.values())
    max_time = max(data['time'] for data in endpoints_status.values())
    min_time = min(data['time'] for data in endpoints_status.values())
    avg_time = total_time / total_count if total_count > 0 else 0

    msg = "📊 <b>ОБЩАЯ СТАТИСТИКА</b>\n"
    msg += f"📅 {timestamp}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✅ Успешно: <b>{success_count}</b>\n"
    msg += f"❌ Ошибок: <b>{error_count}</b>\n"
    msg += f"📈 Uptime: <b>{uptime_percent:.1f}%</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"⏱ Сумма: <code>{total_time:.2f}s</code>\n"
    msg += f"📈 Макс: <code>{max_time:.2f}s</code>\n"
    msg += f"📉 Мин: <code>{min_time:.2f}s</code>\n"
    msg += f"Среднее: <code>{avg_time:.2f}s</code>"
    messages.append(msg)

    return messages
