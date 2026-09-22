# -*- coding: utf-8 -*-
"""
Генератор фото-карты.

v3: минималистичный вариант "как визитки с Pinterest" — почти белый фон,
номер карты вписан от руки (шрифт NothingYouCouldDo), занимает почти всю
карту, и только мелкая печатная подпись сверху/снизу. Никакой заливки
цветом, один акцентный цвет как штрих. Цвета и логотип — из официальных
файлов бренда (REYMA_Corporate_Colors_RGB, REYMA_Logotype_RGB).
"""

import io
import os

from PIL import Image, ImageDraw, ImageFont

# --- официальные цвета Reyma (Pantone 7463/320/1797/Neutral Black) ---
NAVY = (18, 40, 70)      # PANTONE 7463 CP
TEAL = (0, 140, 160)     # PANTONE 320 CP
RED = (215, 40, 50)      # PANTONE 1797 CP
BLACK = (34, 34, 34)     # PANTONE NEUTRAL BLACK C
PAPER = (255, 255, 254)  # почти белый, не бежевый
WHITE = (255, 255, 255)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "reyma_logo.png")
FONT_SCRIPT = os.path.join(ASSETS_DIR, "NothingYouCouldDo-Regular.ttf")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_CONDENSED_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
FONT_CONDENSED = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"

W, H = 1000, 600


def _logo(max_width: int) -> Image.Image:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    ratio = max_width / logo.width
    return logo.resize((max_width, int(logo.height * ratio)), Image.LANCZOS)


def _tracked_text(draw, xy, text, font, fill, tracking=0):
    """Печатает текст вручную по буквам — чтобы дать printed-labels лёгкий
    трекинг (разрядку), как на минималистичных визитках."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        w = draw.textlength(ch, font=font)
        x += w + tracking


def render_card_handwritten(card_number: int, balance: int, name: str, lang: str = "en") -> io.BytesIO:
    """Минималистичный вариант: почти белый фон, номер карты — от руки,
    крупно, во всю карту. Единственный цветовой акцент — тонкая линия."""
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    top_label = {"hy": "ՌԵՅՄԱ ԲՈՆՈՒՍԱՅԻՆ ՔԱՐՏ", "ru": "REYMA БОНУСНАЯ КАРТА", "en": "REYMA BONUS CARD"}.get(lang, "REYMA BONUS CARD")
    font_top_label = ImageFont.truetype(FONT_BOLD, 16)
    _tracked_text(draw, (56, 50), top_label, font_top_label, NAVY, tracking=3)

    logo = _logo(96)
    img.paste(logo, (W - logo.width - 56, 42), logo)

    # номер карты — от руки, главный элемент
    number_text = str(card_number)
    font_hand = ImageFont.truetype(FONT_SCRIPT, 260)
    bbox = draw.textbbox((0, 0), number_text, font=font_hand)
    num_w, num_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    hand_layer = Image.new("RGBA", (num_w + 40, num_h + 40), (0, 0, 0, 0))
    hand_draw = ImageDraw.Draw(hand_layer)
    hand_draw.text((20 - bbox[0], 20 - bbox[1]), number_text, font=font_hand, fill=NAVY)
    hand_layer = hand_layer.rotate(-3, expand=True, resample=Image.BICUBIC)
    paste_x = (W - hand_layer.width) // 2
    paste_y = 190
    img.paste(hand_layer, (paste_x, paste_y), hand_layer)

    # тонкая акцентная линия под номером
    line_y = paste_y + hand_layer.height - 10
    draw.line([(56, line_y), (W - 56, line_y)], fill=RED, width=2)

    # нижняя строка — печатные подписи: имя слева, баланс справа
    name_label = {"hy": "ՔԱՐՏԻ ՏԵՐ", "ru": "ДЕРЖАТЕЛЬ", "en": "CARD HOLDER"}.get(lang, "CARD HOLDER")
    balance_label = {"hy": "ԲԱԼԱՆՍ", "ru": "БАЛАНС", "en": "BALANCE"}.get(lang, "BALANCE")

    font_small_label = ImageFont.truetype(FONT_BOLD, 14)
    font_small_value = ImageFont.truetype(FONT_REGULAR, 22)

    _tracked_text(draw, (56, line_y + 26), name_label, font_small_label, TEAL, tracking=2)
    draw.text((56, line_y + 46), name, font=font_small_value, fill=BLACK)

    balance_text = f"{balance}"
    bal_label_w = draw.textlength(balance_label + " " * len(balance_label), font=font_small_label)  # приблизительно, скорректируем ниже
    # считаем реальную ширину трекнутого лейбла и значения, чтобы прижать к правому краю
    def tracked_width(text, font, tracking):
        return sum(draw.textlength(ch, font=font) + tracking for ch in text) - tracking

    label_w = tracked_width(balance_label, font_small_label, 2)
    value_bbox = draw.textbbox((0, 0), balance_text, font=font_small_value)
    value_w = value_bbox[2] - value_bbox[0]

    _tracked_text(draw, (W - 56 - label_w, line_y + 26), balance_label, font_small_label, TEAL, tracking=2)
    draw.text((W - 56 - value_w, line_y + 46), balance_text, font=font_small_value, fill=BLACK)

    buf = io.BytesIO()
    buf.name = "reyma_card.png"
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# алиас по умолчанию — используется в bot.py
render_card = render_card_handwritten


def render_welcome_banner() -> io.BytesIO:
    """640x360 — формат, который просит BotFather для Welcome Picture.
    Минимализм: логотип по центру + "BONUS CARD" мелким текстом, без "in Telegram"."""
    w, h = 640, 360
    img = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(img)

    logo = _logo(320)
    img.paste(logo, ((w - logo.width) // 2, 110), logo)

    sub = "BONUS CARD"
    font_sub = ImageFont.truetype(FONT_BOLD, 20)
    sub_w = sum(draw.textlength(ch, font=font_sub) + 4 for ch in sub) - 4
    _tracked_text(draw, ((w - sub_w) / 2, 230), sub, font_sub, TEAL, tracking=4)

    draw.line([(w // 2 - 40, 210), (w // 2 + 40, 210)], fill=RED, width=2)

    buf = io.BytesIO()
    buf.name = "welcome.png"
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
