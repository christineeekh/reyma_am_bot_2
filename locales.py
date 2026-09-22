# -*- coding: utf-8 -*-
"""
Тексты бота на трёх языках: армянский (hy), русский (ru), английский (en).
Всё, что видит пользователь, лежит здесь — чтобы менять формулировки,
не трогая логику в bot.py.

Ключи "bonus_rules" и часть текста "consent_intro" — черновые (см. ТЗ
п.2.4, п.2.3): логика их требует, финальный копирайтинг ещё не утверждён
и уточняется отдельно.
"""

LANGS = ["hy", "ru", "en"]

LANG_LABELS = {
    "hy": "🇦🇲 Հայերեն",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

T = {
    "choose_language": {
        "hy": "Ընտրեք լեզուն 👇",
        "ru": "Выберите язык 👇",
        "en": "Choose your language 👇",
    },
    "welcome": {
        "hy": "Բարի գալուստ Reyma-ի բոնուսային ծրագիր! 🧸\nԱյստեղ կարող եք ստուգել ձեր քարտը, բալանսը և ստանալ նորություններ։",
        "ru": "Добро пожаловать в бонусную программу Reyma! 🧸\nЗдесь вы можете посмотреть свою карту, баланс и получать новости.",
        "en": "Welcome to the Reyma loyalty program! 🧸\nHere you can check your card, balance and get updates.",
    },
    "menu_card": {
        "hy": "🎟 Իմ քարտը",
        "ru": "🎟 Моя карта",
        "en": "🎟 My card",
    },
    "menu_register": {
        "hy": "➕ Գրանցվել",
        "ru": "➕ Зарегистрироваться",
        "en": "➕ Register",
    },
    "menu_language": {
        "hy": "🌐 Լեզու",
        "ru": "🌐 Язык",
        "en": "🌐 Language",
    },
    "menu_support": {
        "hy": "💬 Օգնություն",
        "ru": "💬 Поддержка",
        "en": "💬 Support",
    },
    "not_registered": {
        "hy": "Դուք դեռ չունեք քարտ։ Սեղմեք «➕ Գրանցվել», որպեսզի ստանաք այն։",
        "ru": "У вас пока нет карты. Нажмите «➕ Зарегистрироваться», чтобы получить её.",
        "en": "You don't have a card yet. Tap “➕ Register” to get one.",
    },

    # --- регистрация: телефон первым шагом (см. ТЗ п.2.1, п.2.2) ---
    "ask_phone": {
        "hy": "Գրեք ձեր հեռախոսահամարը, որով ձևակերպված է քարտը (օր.՝ +37477123456)։\n\nԳործընթացը ցանկացած պահի կարող եք դադարեցնել՝ /cancel։",
        "ru": "Введите номер телефона, на который оформлена карта (например, +37477123456).\n\nПрервать регистрацию в любой момент можно командой /cancel.",
        "en": "Enter the phone number your card is registered to (e.g. +37477123456).\n\nYou can stop the registration anytime with /cancel.",
    },
    "phone_invalid": {
        "hy": "Ձևաչափը սխալ է։ Փորձեք կրկին, օր.՝ +37477123456",
        "ru": "Похоже, формат номера некорректный. Попробуйте ещё раз, например: +37477123456",
        "en": "That doesn't look like a valid number. Try again, e.g. +37477123456",
    },
    "no_card_ask_name": {
        "hy": "Դուք դեռ Reyma քարտ չունեք։ Ինչպե՞ս Ձեզ կոչել (անուն և ազգանուն, առանց հայրանվան)։",
        "ru": "У вас пока нет карты Reyma. Как вас зовут? (имя и фамилия, без отчества)",
        "en": "You don't have a Reyma card yet. What's your name? (first and last name)",
    },
    "ask_email": {
        "hy": "Գրեք ձեր էլ. փոստը՝",
        "ru": "Введите ваш email:",
        "en": "Enter your email:",
    },
    "email_invalid": {
        "hy": "Սա էլ. փոստի նման չէ։ Փորձեք կրկին։",
        "ru": "Это не похоже на email. Попробуйте ещё раз.",
        "en": "That doesn't look like an email. Try again.",
    },

    # --- согласия: один пост с кнопками (см. ТЗ п.2.3) ---
    "consent_intro": {
        "hy": "Մի քանի բառ, նախքան քարտը կպատրաստենք 🧸\n\nՔարտը վարելու համար մեզ անհրաժեշտ է մշակել Ձեր տվյալները (անուն, հեռախոս, էլ. փոստ)՝ սա ծրագրում մասնակցելու պարտադիր պայման է։ Բացի այդ, կարող ենք ուղարկել Reyma-ի նորություններ ու հատուկ առաջարկներ՝ սա կամընտիր է, կարող եք համաձայնվել կամ ոչ։\n\nԸնտրեք ստորև՝",
        "ru": "Ещё пара слов, прежде чем оформим карту 🧸\n\nЧтобы вести бонусную карту, нам нужно обрабатывать ваши данные (имя, телефон, email) — это обязательное условие участия в программе. Также мы можем присылать новости и специальные предложения Reyma — это уже по желанию, соглашаться необязательно.\n\nВыберите вариант ниже:",
        "en": "Just one more thing before we set up your card 🧸\n\nTo manage your bonus card, we need to process your data (name, phone, email) — this is a required part of joining the program. We can also send you Reyma news and special offers — that part is optional.\n\nPick an option below:",
    },
    "btn_consent_all": {
        "hy": "✅ Համաձայն եմ ամենի հետ",
        "ru": "✅ Согласна на всё",
        "en": "✅ Agree to everything",
    },
    "btn_consent_privacy_only": {
        "hy": "Միայն տվյալների մշակմանը",
        "ru": "Только обработка данных",
        "en": "Only data processing",
    },
    "btn_doc_privacy": {
        "hy": "📄 Գաղտնիության քաղաքականություն",
        "ru": "📄 Политика конфиденциальности",
        "en": "📄 Privacy policy",
    },
    "btn_doc_terms": {
        "hy": "📄 Ծրագրի պայմանները",
        "ru": "📄 Условия программы",
        "en": "📄 Program terms",
    },
    "doc_placeholder_alert": {
        "hy": "Տեքստը շուտով կավելացնենք 🙂",
        "ru": "Текст скоро добавим 🙂",
        "en": "Text coming soon 🙂",
    },

    "found_existing": {
        "hy": "Ձեր հեռախոսահամարով քարտ արդեն կա։ Կապեցինք այն ձեր Telegram-ին 👇",
        "ru": "По вашему номеру уже есть карта. Мы привязали её к вашему Telegram 👇",
        "en": "A card already exists for this number. We've linked it to your Telegram 👇",
    },
    "created_new": {
        "hy": "Ձեր նոր քարտը պատրաստ է 👇",
        "ru": "Ваша новая карта готова 👇",
        "en": "Your new card is ready 👇",
    },
    "card_caption": {
        "hy": "🎟 Ձեր Reyma քարտը\nՀամար՝ {number}\nԲալանս՝ {balance} բոնուս",
        "ru": "🎟 Ваша карта Reyma\nНомер: {number}\nБаланс: {balance} бонусов",
        "en": "🎟 Your Reyma card\nNumber: {number}\nBalance: {balance} bonus points",
    },

    # --- баг из ТЗ п.2.4: сообщение об ошибке рендера/отправки карты ---
    "card_render_error": {
        "hy": "Քարտը պատրաստել չհաջողվեց․ արդեն զբաղվում ենք այս հարցով։ Փորձեք մի քանի րոպեից՝ «Իմ քարտը» կոճակով։",
        "ru": "Не получилось подготовить карту — уже разбираемся. Попробуйте, пожалуйста, через пару минут командой «Моя карта».",
        "en": "We couldn't prepare your card — we're already looking into it. Please try again in a couple of minutes with “My card”.",
    },

    # --- ТЗ п.2.4: текст про правила использования/накопления бонусов ---
    # черновой текст, финальные условия программы утверждаются отдельно
    "bonus_rules": {
        "hy": "ℹ️ Ինչպես է աշխատում բոնուսային քարտը.\n— բոնուսները հաշվարկվում են Reyma խանութներում կատարված գնումների համար\n— բալանսը կարող եք ծախսել հաջորդ գնումների ժամանակ\n— քարտը կարող եք տեսնել ցանկացած պահի՝ «Իմ քարտը» կոճակով կամ /card հրամանով\n\n(տեքստը սևագիր է, վերջնական պայմանները կհաստատվեն առանձին)",
        "ru": "ℹ️ Как работает бонусная карта:\n— бонусы начисляются за покупки в магазинах Reyma\n— баланс можно потратить на следующие покупки\n— карту можно посмотреть в любой момент кнопкой «Моя карта» или командой /card\n\n(текст черновой, финальные условия программы утвердим отдельно)",
        "en": "ℹ️ How your bonus card works:\n— bonuses are earned on purchases at Reyma stores\n— your balance can be spent on future purchases\n— you can check your card anytime with “My card” or the /card command\n\n(draft text — final program terms to be confirmed separately)",
    },

    "support_text": {
        "hy": "Հարցերի դեպքում գրեք մեզ 📞 012 223 227 կամ այցելեք reyma.am",
        "ru": "По любым вопросам: 📞 012 223 227 или сайт reyma.am",
        "en": "Questions? 📞 012 223 227 or visit reyma.am",
    },
    "cancelled": {
        "hy": "Գրանցումը չեղարկվեց։",
        "ru": "Регистрация отменена.",
        "en": "Registration cancelled.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Достаёт строку по ключу и языку, с fallback на русский, и форматирует."""
    lang = lang if lang in LANGS else "ru"
    text = T[key].get(lang, T[key]["ru"])
    return text.format(**kwargs) if kwargs else text
