"""Render an order receipt as a PNG, entirely on the server.

Why server-side: the image is only worth sending if its prices come from
the database. An image drawn in the browser would carry whatever price the
page happened to hold, which is exactly the value a customer can edit.

Why the reshaping dance: this Pillow build has no Raqm/HarfBuzz, so
ImageDraw cannot shape Arabic itself. arabic_reshaper converts the text to
Arabic Presentation Forms-B and python-bidi puts it in visual order, then
Pillow draws the already-shaped string. That only works with a font that
covers the presentation-forms block, which is why the bundled font is IBM
Plex Sans Arabic (140/144) rather than Cairo (89/144, missing the isolated
letterforms).

The layout is a light card so it stays readable in sunlight and on paper,
which is where a delivery rider actually reads it.
"""
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path(__file__).resolve().parent / 'assets' / 'fonts'
REGULAR = FONT_DIR / 'IBMPlexSansArabic-Regular.ttf'
SEMIBOLD = FONT_DIR / 'IBMPlexSansArabic-SemiBold.ttf'

WIDTH = 760
PAD = 30
CARD = 22          # inset of the white panels from the page edge
INNER = CARD + 18  # text inset inside a panel

PAPER = '#f2f0ee'
PANEL = '#ffffff'
BRAND = '#8c1518'      # the brand's deep red; white on it is 9.39:1
BRAND_SOFT = '#fbe9ea'
INK = '#222222'
MUTED = '#555555'
FAINT = '#7a736f'
RULE = '#e4e0dd'
# The brand yellow cannot be read on paper at this size, so amounts that are
# still to be confirmed use it darkened to 4.9:1 instead.
GOLD = '#8a6a00'


@lru_cache(maxsize=24)
def _font(bold, size):
    return ImageFont.truetype(str(SEMIBOLD if bold else REGULAR), size)


def ar(text):
    """Shape Arabic for a renderer that cannot shape it itself."""
    return get_display(arabic_reshaper.reshape(str(text)))


def _money(amount, currency):
    quantised = f'{amount:.2f}'.rstrip('0').rstrip('.')
    return f'{quantised} {currency}'


def _wrap(text, limit):
    """Wrap on whole words; the receipt has no hyphenation to fall back on."""
    words = str(text).split()
    lines, current = [], ''
    for word in words:
        candidate = f'{current} {word}'.strip()
        if len(candidate) > limit and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or ['']


class _Sheet:
    """A tall scratch image cropped to its content once drawing is done."""

    def __init__(self, width=WIDTH):
        self.width = width
        self.image = Image.new('RGB', (width, 3200), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.y = 0

    # ── text ──────────────────────────────────────────────────────────────
    def rtl(self, text, size=19, bold=False, fill=INK, x=None, dy=0):
        self.draw.text(
            (self.width - INNER if x is None else x, self.y + dy),
            ar(text), font=_font(bold, size), fill=fill, anchor='ra',
        )

    def ltr(self, text, size=19, bold=False, fill=INK, x=INNER, dy=0):
        self.draw.text(
            (x, self.y + dy), ar(text), font=_font(bold, size), fill=fill, anchor='la',
        )

    def centre(self, text, size=15, bold=False, fill=MUTED, dy=0):
        self.draw.text(
            (self.width // 2, self.y + dy), ar(text),
            font=_font(bold, size), fill=fill, anchor='ma',
        )

    # ── shapes ────────────────────────────────────────────────────────────
    def panel(self, height, radius=16, fill=PANEL, outline=RULE):
        self.draw.rounded_rectangle(
            [(CARD, self.y), (self.width - CARD, self.y + height)],
            radius=radius, fill=fill, outline=outline, width=1,
        )

    def rule(self, inset=INNER, colour=RULE):
        self.draw.line(
            [(inset, self.y), (self.width - inset, self.y)], fill=colour, width=1,
        )

    def leader(self, start_x, end_x, colour='#cfc8bf'):
        """The dotted run between a label and its amount."""
        for x in range(int(start_x), int(end_x), 7):
            self.draw.ellipse([(x, self.y), (x + 1.6, self.y + 1.6)], fill=colour)

    def badge(self, cx, cy, radius=15, fill=BRAND):
        """A filled disc with a tick — the 'issued by the system' mark."""
        self.draw.ellipse(
            [(cx - radius, cy - radius), (cx + radius, cy + radius)], fill=fill,
        )
        self.draw.line(
            [(cx - radius * 0.42, cy + radius * 0.04),
             (cx - radius * 0.10, cy + radius * 0.38),
             (cx + radius * 0.46, cy - radius * 0.34)],
            fill='#ffffff', width=3, joint='curve',
        )

    def section(self, title):
        """A section heading with the small brand marker beside it."""
        self.draw.rounded_rectangle(
            [(self.width - INNER - 5, self.y + 3), (self.width - INNER, self.y + 21)],
            radius=2, fill=BRAND,
        )
        self.rtl(title, size=19, bold=True, fill=BRAND, x=self.width - INNER - 14)
        self.y += 30

    def finish(self, bottom=0):
        height = self.y + bottom
        return self.image.crop((0, 0, self.width, height))


def _field_rows(order):
    rows = [('الاسم', order.customer_name or '—'), ('رقم الجوال', order.phone or '—')]
    if order.source == 'cashier':
        rows.append(('عدد الزبائن', str(order.customer_count)))
        rows.append(('رقم الطاولة', order.table_number or '—'))
    if order.fulfillment == 'delivery':
        rows.append(('العنوان', order.address or '—'))
    rows.append(('طريقة الاستلام', order.get_fulfillment_display()))
    rows.append(('وقت الطلب', order.created_at.strftime('%d/%m/%Y — %H:%M')))
    return rows


def render_order(order):
    """Return the receipt for one order as PNG bytes."""
    currency = order.currency or '₪'
    lines = list(order.lines.all())
    sheet = _Sheet()

    # ── Header band ───────────────────────────────────────────────────────
    sheet.draw.rounded_rectangle(
        [(CARD, 16), (WIDTH - CARD, 138)], radius=18, fill=BRAND,
    )
    sheet.y = 44
    sheet.rtl(order.restaurant_name or 'فرايز ستيشن', size=30, bold=True, fill='#ffffff')
    sheet.y = 86
    sheet.rtl('تأكيد الطلب', size=17, fill='#f0c9c7')
    # A white disc with the tick drawn back in the brand colour.
    sheet.draw.ellipse(
        [(INNER - 4, 51), (INNER + 48, 103)], fill='#ffffff',
    )
    sheet.draw.line(
        [(INNER + 8, 78), (INNER + 18, 89), (INNER + 36, 65)],
        fill=BRAND, width=5, joint='curve',
    )

    # ── Order number ──────────────────────────────────────────────────────
    sheet.y = 158
    sheet.panel(64, radius=14, fill=BRAND_SOFT, outline='#f0d6d4')
    sheet.y = 178
    sheet.rtl(f'رقم الطلب:  {order.code}', size=26, bold=True, fill=BRAND)
    sheet.y = 222

    sheet.centre('هذا الطلب مُعتمد من النظام وأسعاره محسوبة على الخادم', size=13, fill=MUTED)
    sheet.y = 252

    # ── Customer ──────────────────────────────────────────────────────────
    field_rows = _field_rows(order)
    wrapped = [(label, _wrap(value, 52)) for label, value in field_rows]
    body_height = sum(26 * len(chunks) for _, chunks in wrapped)
    sheet.panel(body_height + 66)
    sheet.y += 20
    sheet.section('بيانات العميل')

    for label, chunks in wrapped:
        sheet.rtl(f'{label}:', size=15, fill=FAINT)
        for chunk in chunks:
            sheet.rtl(chunk, size=16, x=WIDTH - INNER - 118)
            sheet.y += 26
    sheet.y += 18

    # ── Items ─────────────────────────────────────────────────────────────
    rows_height = 38 * len(lines)
    notes_chunks = _wrap(order.notes, 60) if order.notes else []
    notes_height = (24 * len(notes_chunks) + 20) if notes_chunks else 0
    sheet.panel(rows_height + notes_height + 108)
    sheet.y += 20
    sheet.section('تفاصيل الطلب')

    name_x = WIDTH - INNER - 12
    qty_x = int(WIDTH * 0.40)
    price_x = INNER + 12

    sheet.draw.rounded_rectangle(
        [(INNER, sheet.y - 2), (WIDTH - INNER, sheet.y + 32)], radius=7, fill=BRAND,
    )
    sheet.rtl('الصنف', size=15, bold=True, fill='#ffffff', x=name_x, dy=6)
    sheet.draw.text((qty_x, sheet.y + 6), ar('الكمية'), font=_font(True, 15),
                    fill='#ffffff', anchor='ma')
    sheet.ltr('السعر', size=15, bold=True, fill='#ffffff', x=price_x, dy=6)
    sheet.y += 44

    for index, line in enumerate(lines):
        sheet.rtl(line.name_ar, size=16, x=name_x)
        sheet.draw.text((qty_x, sheet.y), ar(str(line.quantity)), font=_font(False, 16),
                        fill=INK, anchor='ma')
        if line.is_priced:
            sheet.ltr(_money(line.line_total, currency), size=16, bold=True, x=price_x)
        else:
            sheet.ltr(line.price_note or 'يحدد عند التأكيد', size=13, fill=GOLD, x=price_x)
        sheet.y += 26
        if index < len(lines) - 1:
            sheet.rule(inset=INNER, colour='#f0ece6')
        sheet.y += 12

    if notes_chunks:
        sheet.y += 4
        sheet.draw.rounded_rectangle(
            [(INNER, sheet.y - 6), (WIDTH - INNER, sheet.y + 24 * len(notes_chunks) + 6)],
            radius=8, fill='#faf7f2',
        )
        for position, chunk in enumerate(notes_chunks):
            prefix = 'ملاحظات: ' if position == 0 else ''
            sheet.rtl(f'{prefix}{chunk}', size=15, fill=MUTED, x=WIDTH - INNER - 10)
            sheet.y += 24
        sheet.y += 12
    sheet.y += 22

    # ── Summary ───────────────────────────────────────────────────────────
    priced_total = sum(line.line_total for line in lines if line.is_priced)
    summary_rows = []
    # A subtotal identical to the total tells the reader nothing, so it only
    # appears when something else is in play.
    if order.has_unpriced_lines:
        summary_rows.append(('المجموع الفرعي', _money(priced_total, currency)))
        summary_rows.append(('عروض تُسعّر عند التأكيد', 'يحددها المطعم'))

    sheet.panel(len(summary_rows) * 30 + 128)
    sheet.y += 20
    sheet.section('ملخص الحساب')

    for label, value in summary_rows:
        sheet.rtl(f'{label}:', size=16, fill=MUTED)
        sheet.ltr(value, size=16, x=price_x)
        label_width = _font(False, 16).getlength(ar(f'{label}:'))
        value_width = _font(False, 16).getlength(ar(value))
        sheet.leader(price_x + value_width + 12, WIDTH - INNER - label_width - 12, )
        sheet.y += 30

    sheet.y += 10
    total_top = sheet.y
    sheet.draw.rounded_rectangle(
        [(INNER, total_top), (WIDTH - INNER, total_top + 58)], radius=12, fill=BRAND,
    )
    sheet.y = total_top + 16
    sheet.rtl('الإجمالي النهائي:', size=19, bold=True, fill='#ffffff', x=WIDTH - INNER - 16)
    sheet.ltr(_money(order.total, currency), size=25, bold=True, fill='#ffffff', x=price_x + 4)
    sheet.y = total_top + 78

    # ── Footer ────────────────────────────────────────────────────────────
    sheet.centre(f'حالة الطلب: {order.get_status_display()}', size=16, bold=True, fill=INK)
    sheet.y += 28
    sheet.centre(f'يرجى الاحتفاظ برقم الطلب {order.code} عند الاستفسار', size=13, fill=MUTED)
    sheet.y += 24
    sheet.centre(f'شكرًا لطلبكم من {order.restaurant_name or "فرايز ستيشن"}', size=13, fill=BRAND)
    sheet.y += 30

    buffer = BytesIO()
    sheet.finish().save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()
