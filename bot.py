# -*- coding: utf-8 -*-
"""
Reyma bonus-card bot.

Сценарий:
  /start -> выбор языка -> главное меню (кнопки)
  "Моя карта" / /card         -> если Telegram уже привязан — фото-карта + закреп
  "Зарегистрироваться" / /register ->
      сначала телефон -> поиск в базе (mock_db.py):
        нашли существующего клиента  -> привязали карту, ФИО/email повторно не спрашиваем
        не нашли                     -> имя -> email -> согласия (один пост с кнопками) -> создание карты
  "Язык" / /language          -> сменить язык в любой момент
  "Поддержка" / /help         -> контакты
  /cancel                     -> прервать регистрацию

Данные — временно в mock_db.py (в памяти процесса, сбрасываются при рестарте).
Когда будет решён вопрос с 1С, find_by_phone / create_card в mock_db.py
меняются на реальные запросы — остальной код бота трогать не нужно.

ЗАПУСК:
  1. pip install -r requirements.txt
  2. export REYMA_BOT_TOKEN="<токен из BotFather>"
  3. python bot.py
"""

import logging
import os
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import mock_db
from card_image import FONT_SCRIPT, LOGO_PATH, render_card
from locales import LANG_LABELS, LANGS, t

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("reyma_bot")

# --- состояния для регистрации (ConversationHandler) ---
# Телефон теперь первый шаг: карты привязаны к номеру, значит именно он
# определяет, есть ли у человека карта, до того как спрашивать что-то ещё.
ASK_PHONE, ASK_NAME, ASK_EMAIL, ASK_CONSENT = range(4)

PHONE_RE = re.compile(r"^\+374\d{8}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def lang_of(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "ru")


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    rows = [
        [t("menu_card", lang), t("menu_register", lang)],
        [t("menu_language", lang), t("menu_support", lang)],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def language_inline_keyboard() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(LANG_LABELS[code], callback_data=f"lang:{code}") for code in LANGS]
    return InlineKeyboardMarkup([[b] for b in buttons])


def consent_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Один пост с двумя вариантами согласия + кнопки-ссылки на документы
    (пока заглушки, см. ТЗ п.2.3)."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(t("btn_consent_all", lang), callback_data="consent:all")],
            [InlineKeyboardButton(t("btn_consent_privacy_only", lang), callback_data="consent:privacy_only")],
            [
                InlineKeyboardButton(t("btn_doc_privacy", lang), callback_data="doc:privacy"),
                InlineKeyboardButton(t("btn_doc_terms", lang), callback_data="doc:terms"),
            ],
        ]
    )


def check_assets_on_startup() -> None:
    """См. ТЗ п.2.4: если assets/ не полностью выгружена на GitHub, карта
    не рендерится молча. Логируем явно, чтобы это было видно в логах Railway."""
    if not os.path.exists(LOGO_PATH):
        logger.error(
            "Не найден файл логотипа: %s — рендер карты будет падать, пока assets/ не выгружена в репозиторий",
            LOGO_PATH,
        )
    if not os.path.exists(FONT_SCRIPT):
        logger.error(
            "Не найден файл шрифта: %s — рендер карты будет падать, пока assets/ не выгружена в репозиторий",
            FONT_SCRIPT,
        )


# ---------------------------------------------------------------- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        t("choose_language", lang_of(context)),
        reply_markup=language_inline_keyboard(),
    )


async def on_language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":", 1)[1]
    context.user_data["lang"] = lang
    await query.edit_message_text(t("welcome", lang))
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=t("welcome", lang),
        reply_markup=main_menu_keyboard(lang),
    )


async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(t("choose_language", lang_of(context)), reply_markup=language_inline_keyboard())


# ------------------------------------------------------------- Моя карта ---
async def show_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = lang_of(context)
    tg_id = update.effective_user.id
    record = mock_db.find_by_telegram_id(tg_id)
    if not record:
        await update.message.reply_text(t("not_registered", lang))
        return
    await send_card_and_pin(update, context, record, lang)


async def send_card_and_pin(update: Update, context: ContextTypes.DEFAULT_TYPE, record, lang: str) -> None:
    """Баг из ТЗ п.2.4: раньше падение render_card/send_photo проходило
    молча после текста "карта готова". Теперь оборачиваем в try/except с
    логированием и понятным сообщением пользователю."""
    chat_id = update.effective_chat.id

    try:
        # Картинка карты — всегда на английском, независимо от языка
        # интерфейса (подписи в чате вокруг неё остаются на выбранном языке).
        image = render_card(record.card_number, record.bonus_balance, record.full_name, "en")
    except Exception:
        logger.exception("Не удалось сгенерировать изображение карты (card_number=%s)", record.card_number)
        await context.bot.send_message(chat_id=chat_id, text=t("card_render_error", lang))
        return

    caption = t("card_caption", lang, number=record.card_number, balance=record.bonus_balance)
    try:
        msg = await context.bot.send_photo(chat_id=chat_id, photo=image, caption=caption)
    except Exception:
        logger.exception("Не удалось отправить фото карты (card_number=%s)", record.card_number)
        await context.bot.send_message(chat_id=chat_id, text=t("card_render_error", lang))
        return

    try:
        await context.bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id, disable_notification=True)
    except Exception as exc:  # в личных чатах pin работает, но на всякий случай не роняем бота
        logger.warning("Не удалось закрепить сообщение: %s", exc)

    # ТЗ п.2.4: короткий текст про правила использования/накопления бонусов,
    # отдельным сообщением сразу после фото карты.
    await context.bot.send_message(chat_id=chat_id, text=t("bonus_rules", lang))


# ------------------------------------------------------------ Регистрация ---
async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вход и по кнопке «Зарегистрироваться», и по команде /register.
    Первым и единственным вопросом — телефон (см. ТЗ п.2.1)."""
    await update.message.reply_text(t("ask_phone", lang_of(context)))
    return ASK_PHONE


async def register_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    phone = update.message.text.strip().replace(" ", "")
    if not PHONE_RE.match(phone):
        await update.message.reply_text(t("phone_invalid", lang))
        return ASK_PHONE

    tg_id = update.effective_user.id
    existing = mock_db.find_by_phone(phone)

    if existing:
        # Уже есть карта с офлайн-оформления — ФИО и email повторно не спрашиваем.
        record = mock_db.link_telegram(phone, tg_id)
        await update.message.reply_text(t("found_existing", lang))
        await send_card_and_pin(update, context, record, lang)
        return ConversationHandler.END

    context.user_data["reg_phone"] = phone
    await update.message.reply_text(t("no_card_ask_name", lang))
    return ASK_NAME


async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["reg_name"] = update.message.text.strip()
    await update.message.reply_text(t("ask_email", lang_of(context)))
    return ASK_EMAIL


async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    email = update.message.text.strip()
    if not EMAIL_RE.match(email):
        await update.message.reply_text(t("email_invalid", lang))
        return ASK_EMAIL
    context.user_data["reg_email"] = email
    await update.message.reply_text(t("consent_intro", lang), reply_markup=consent_keyboard(lang))
    return ASK_CONSENT


async def register_doc_placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Кнопки-ссылки на документы — пока заглушки (см. ТЗ п.2.3), контент
    допишем отдельно. Показываем всплывающее уведомление и остаёмся на
    этом же шаге, не трогая уже отправленный пост с согласиями."""
    query = update.callback_query
    await query.answer(text=t("doc_placeholder_alert", lang_of(context)), show_alert=True)
    return ASK_CONSENT


async def register_consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Объединённый хендлер для обоих вариантов согласия из одного поста
    (см. ТЗ п.2.3): 'Согласна на всё' и 'Только обработка данных'."""
    lang = lang_of(context)
    query = update.callback_query
    await query.answer()

    marketing_consent = query.data == "consent:all"
    chosen_label = t("btn_consent_all", lang) if marketing_consent else t("btn_consent_privacy_only", lang)
    await query.edit_message_text(f"{t('consent_intro', lang)}\n\n✅ {chosen_label}")

    phone = context.user_data["reg_phone"]
    name = context.user_data["reg_name"]
    email = context.user_data["reg_email"]
    tg_id = update.effective_user.id

    record = mock_db.create_card(phone, name, email, tg_id, lang, marketing_consent)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=t("created_new", lang))
    await send_card_and_pin(update, context, record, lang)

    for key in ("reg_phone", "reg_name", "reg_email"):
        context.user_data.pop(key, None)
    return ConversationHandler.END


async def register_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    for key in ("reg_phone", "reg_name", "reg_email"):
        context.user_data.pop(key, None)
    await update.message.reply_text(t("cancelled", lang_of(context)), reply_markup=main_menu_keyboard(lang_of(context)))
    return ConversationHandler.END


# ------------------------------------------------------------- Поддержка ---
async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(t("support_text", lang_of(context)))


# --------------------------------------------------------- сборка приложения ---
def build_app() -> Application:
    token = os.environ.get("REYMA_BOT_TOKEN")
    if not token:
        raise SystemExit("Не найден токен: export REYMA_BOT_TOKEN=\"<токен из BotFather>\"")

    check_assets_on_startup()

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_language_chosen, pattern=r"^lang:"))

    # ловим кнопки главного меню по тексту на любом из трёх языков
    card_labels = [t("menu_card", l) for l in LANGS]
    lang_labels = [t("menu_language", l) for l in LANGS]
    support_labels = [t("menu_support", l) for l in LANGS]
    register_labels = [t("menu_register", l) for l in LANGS]

    # Вариант А из ТЗ п.2.5: /card /language /help — реальные команды,
    # ведущие к тем же функциям, что и кнопки нижней панели. Слэши — для тех,
    # кто печатает, кнопки — для тех, кто тыкает, оба пути рабочие.
    app.add_handler(MessageHandler(filters.Text(card_labels), show_card))
    app.add_handler(CommandHandler("card", show_card))

    app.add_handler(MessageHandler(filters.Text(lang_labels), show_language_menu))
    app.add_handler(CommandHandler("language", show_language_menu))

    app.add_handler(MessageHandler(filters.Text(support_labels), show_support))
    app.add_handler(CommandHandler("help", show_support))

    conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text(register_labels), register_start),
            CommandHandler("register", register_start),
        ],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_phone)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
            ASK_CONSENT: [
                CallbackQueryHandler(register_consent, pattern=r"^consent:(all|privacy_only)$"),
                CallbackQueryHandler(register_doc_placeholder, pattern=r"^doc:"),
            ],
        },
        fallbacks=[CommandHandler("cancel", register_cancel)],
    )
    app.add_handler(conv)

    return app


if __name__ == "__main__":
    application = build_app()
    logger.info("Reyma bot запущен (polling)...")
    application.run_polling()
