# -*- coding: utf-8 -*-
"""
МОК базы бонусных карт — временная замена 1С, пока нет реального доступа.

Ключ — телефон в формате E.164 (+374...). Это тот же ключ, которым карты
сейчас идентифицируются в текущей (не-Telegram) системе, поэтому переход
на реальный источник данных (1С через API, либо периодический экспорт)
не потребует менять эту логику — только заменить функции ниже на реальные
запросы.

ВАЖНО: это демонстрационные данные для теста сценария, не реальные клиенты.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import itertools

_NEXT_CARD_NUMBER = itertools.count(30001)  # диапазон демо-карт, не пересекается с реальными


@dataclass
class CardRecord:
    phone_e164: str
    full_name: str
    email: str
    card_number: int
    bonus_balance: int
    language_pref: str = "ru"
    telegram_user_id: Optional[int] = None
    source: str = "telegram"
    privacy_consent: bool = False
    marketing_consent: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    synced_1c_id: Optional[str] = None  # пусто, пока нет интеграции


# "Уже существующие" карты — как будто выгружены из 1С/текущей системы бонусов.
# Пригодится, чтобы продемонстрировать сценарий "нашли существующего клиента".
_DB: dict[str, CardRecord] = {
    "+37477123456": CardRecord(
        phone_e164="+37477123456",
        full_name="Անի Հակոբյան",
        email="ani.hakobyan@example.com",
        card_number=26745,
        bonus_balance=300,
        synced_1c_id="1C-00012",
    ),
    "+37493112233": CardRecord(
        phone_e164="+37493112233",
        full_name="Мария Петросян",
        email="maria.p@example.com",
        card_number=27310,
        bonus_balance=1450,
        synced_1c_id="1C-00087",
    ),
}

# telegram_user_id -> phone, для быстрого поиска "своей" карты после привязки
_TG_INDEX: dict[int, str] = {}


def find_by_phone(phone_e164: str) -> Optional[CardRecord]:
    return _DB.get(phone_e164)


def find_by_telegram_id(tg_id: int) -> Optional[CardRecord]:
    phone = _TG_INDEX.get(tg_id)
    return _DB.get(phone) if phone else None


def link_telegram(phone_e164: str, tg_id: int) -> CardRecord:
    record = _DB[phone_e164]
    record.telegram_user_id = tg_id
    _TG_INDEX[tg_id] = phone_e164
    return record


def create_card(
    phone_e164: str,
    full_name: str,
    email: str,
    tg_id: int,
    language_pref: str,
    marketing_consent: bool,
) -> CardRecord:
    record = CardRecord(
        phone_e164=phone_e164,
        full_name=full_name,
        email=email,
        card_number=next(_NEXT_CARD_NUMBER),
        bonus_balance=0,
        language_pref=language_pref,
        telegram_user_id=tg_id,
        source="telegram",
        privacy_consent=True,
        marketing_consent=marketing_consent,
    )
    _DB[phone_e164] = record
    _TG_INDEX[tg_id] = phone_e164
    return record
