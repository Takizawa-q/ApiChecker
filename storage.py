import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Set

import aiofiles


class ProcessedTriggersStorage:

    def __init__(self, file_path: str | Path = "data/processed_triggers.json"):
        """
        Args:
            file_path: Путь к JSON файлу
        """
        self.file_path = Path(file_path)
        self.data: dict = {}
        # Создаем директорию если не существует
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    async def init(self):
        """Загрузка данных из файла"""
        if self.file_path.exists():
            async with aiofiles.open(self.file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                self.data = json.loads(content)
        else:
            self.data = {"processed_triggers": {}}
            await self._save()

    async def close(self):
        """Сохранение данных в файл при закрытии"""
        await self._save()

    async def _save(self):
        """Внутренний метод для сохранения данных"""
        async with aiofiles.open(self.file_path, 'w', encoding='utf-8') as f:
            content = json.dumps(self.data, ensure_ascii=False, indent=2)
            await f.write(content)

    async def mark_as_processed(self, trigger_id: int, uin: str = None, alert_id: int = None):
        """
        Отмечает триггер как обработанный

        Args:
            trigger_id: ID триггера
            uin: UIN созданного инцидента (опционально)
            alert_id: ID алерта (опционально)
        """
        self.data["processed_triggers"][str(trigger_id)] = {
            "processed_at": datetime.now().isoformat(),
            "uin": uin,
            "alert_id": alert_id
        }
        await self._save()

    async def is_processed(self, trigger_id: int) -> bool:
        """
        Проверяет, был ли триггер обработан

        Args:
            trigger_id: ID триггера

        Returns:
            True если триггер уже обработан
        """
        return str(trigger_id) in self.data.get("processed_triggers", {})

    async def get_processed_triggers(self) -> Set[int]:
        """
        Получает все обработанные trigger_id

        Returns:
            Set с ID обработанных триггеров
        """
        return {int(tid) for tid in self.data.get("processed_triggers", {}).keys()}

    async def get_uin_by_trigger_id(self, trigger_id: int) -> Optional[str]:
        """
        Получает UIN по trigger_id

        Args:
            trigger_id: ID триггера

        Returns:
            UIN или None
        """
        trigger_data = self.data.get(
            "processed_triggers", {}).get(str(trigger_id))
        return trigger_data.get("uin") if trigger_data else None

    async def get_alert_id_by_trigger_id(self, trigger_id: int) -> Optional[int]:
        """
        Получает alert_id по trigger_id

        Args:
            trigger_id: ID триггера

        Returns:
            alert_id или None
        """
        trigger_data = self.data.get(
            "processed_triggers", {}).get(str(trigger_id))
        return trigger_data.get("alert_id") if trigger_data else None

    async def clear_old_records(self, days: int = 30):
        """
        Удаляет старые записи (старше указанного количества дней)

        Args:
            days: Количество дней для хранения
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        triggers_to_remove = []

        for trigger_id, data in self.data.get("processed_triggers", {}).items():
            processed_at = datetime.fromisoformat(data["processed_at"])
            if processed_at < cutoff_date:
                triggers_to_remove.append(trigger_id)

        for trigger_id in triggers_to_remove:
            del self.data["processed_triggers"][trigger_id]

        if triggers_to_remove:
            await self._save()
            return len(triggers_to_remove)
        return 0

    async def get_stats(self) -> dict:
        """
        Получает статистику по обработанным триггерам

        Returns:
            Словарь со статистикой
        """
        processed = self.data.get("processed_triggers", {})
        total = len(processed)

        with_uin = sum(1 for v in processed.values() if v.get("uin"))

        return {
            "total_processed": total,
            "with_uin": with_uin,
            "without_uin": total - with_uin
        }



if __name__ == "__main__":
    import asyncio
