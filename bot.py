import asyncio
from dataclasses import dataclass
from typing import Dict, List

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====== НАСТРОЙКИ ======
BOT_TOKEN = "8244244464:AAEpOfX5vyMYmBa9VJIWFo81M3QySw-tajY"
ADMIN_ID = 5937465269  # твой Telegram user id

PAYMENT_TEXT = (
    "✅ ТУТ ТИПА ОПЛАТААА\n"
    "— Перевод на карту: XXXX XXXX XXXX XXXX\n"
    "— Или крипта кошель xxxxx\n"
   
)

# ====== ТОВАРЫ (пример) ======
@dataclass
class Product:
    id: str
    name: str
    price: int
    desc: str

PRODUCTS: List[Product] = [
    Product(id="p1", name="Тут мог быть твой товар 1", price=10, desc="Описание товара 1"),
    Product(id="p2", name="Тут мог быть твой товар 2", price=25, desc="Описание товара 2"),
    Product(id="p3", name="Тут мог быть твой товар 3", price=40, desc="Описание товара 3"),
    Product(id="p3", name="Тут мог быть твой товар 4", price=50, desc="Описание товара 4"),
    Product(id="p3", name="Тут мог быть твой товар 5", price=65, desc="Описание товара 5"),
    Product(id="p3", name="Тут мог быть твой товар 6", price=70, desc="Описание товара 6"),
    Product(id="p3", name="Тут мог быть твой товар 7", price=100, desc="Описание товара 7"),
]

# Корзина в памяти: user_id -> {product_id: qty}
carts: Dict[int, Dict[str, int]] = {}

# ====== КНОПКИ ======
def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Каталогогог", callback_data="catalog")
    kb.button(text="🧺 Корзина", callback_data="cart")
    kb.button(text="ℹ️ Контакты", callback_data="contacts")
    kb.adjust(2, 1)
    return kb.as_markup()

def catalog_kb():
    kb = InlineKeyboardBuilder()
    for p in PRODUCTS:
        kb.button(text=f"{p.name} — {p.price}$", callback_data=f"product:{p.id}")
    kb.button(text="⬅️ Назад", callback_data="back:menu")
    kb.adjust(1)
    return kb.as_markup()

def product_kb(product_id: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ В корзинууу", callback_data=f"add:{product_id}")
    kb.button(text="🧺 Корзина", callback_data="cart")
    kb.button(text="⬅️ Каталог", callback_data="catalog")
    kb.adjust(1, 1, 1)
    return kb.as_markup()

def cart_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Оформить заказ", callback_data="checkout")
    kb.button(text="🧾 Оплатить", callback_data="pay")
    kb.button(text="🗑 Очистить корзину", callback_data="clear")
    kb.button(text="⬅️ Меню", callback_data="back:menu")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()

def checkout_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить заказ", callback_data="confirm")
    kb.button(text="⬅️ В корзину", callback_data="cart")
    kb.adjust(1)
    return kb.as_markup()

# ====== УТИЛИТЫ ======
def get_product(pid: str) -> Product | None:
    for p in PRODUCTS:
        if p.id == pid:
            return p
    return None

def cart_text(user_id: int) -> str:
    cart = carts.get(user_id, {})
    if not cart:
        return "🧺 Корзина пуста."
    lines = ["🧺 Твоя корзина:"]
    total = 0
    for pid, qty in cart.items():
        p = get_product(pid)
        if not p:
            continue
        subtotal = p.price * qty
        total += subtotal
        lines.append(f"• {p.name} × {qty} = {subtotal}€")
    lines.append(f"\n💰 Итого: {total}€")
    return "\n".join(lines)

# ====== БОТ ======
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Это типа магаз газ газ 👇\nВыбирай действие:",
        reply_markup=main_menu_kb()
    )

@dp.callback_query(F.data == "catalog")
async def show_catalog(call: CallbackQuery):
    await call.message.edit_text("🛍 Каталог товаров:", reply_markup=catalog_kb())
    await call.answer()

@dp.callback_query(F.data.startswith("product:"))
async def show_product(call: CallbackQuery):
    pid = call.data.split(":", 1)[1]
    p = get_product(pid)
    if not p:
        await call.answer("Товар не найден", show_alert=True)
        return
    text = f"📦 {p.name}\n💶 Цена: {p.price}$\n\n📝 {p.desc}"
    await call.message.edit_text(text, reply_markup=product_kb(pid))
    await call.answer()

@dp.callback_query(F.data.startswith("add:"))
async def add_to_cart(call: CallbackQuery):
    pid = call.data.split(":", 1)[1]
    if not get_product(pid):
        await call.answer("Товар не найден", show_alert=True)
        return
    user_id = call.from_user.id
    carts.setdefault(user_id, {})
    carts[user_id][pid] = carts[user_id].get(pid, 0) + 1
    await call.answer("Добавлено в корзину ✅")

@dp.callback_query(F.data == "cart")
async def show_cart(call: CallbackQuery):
    await call.message.edit_text(cart_text(call.from_user.id), reply_markup=cart_kb())
    await call.answer()

@dp.callback_query(F.data == "clear")
async def clear_cart(call: CallbackQuery):
    carts[call.from_user.id] = {}
    await call.message.edit_text("🧺 Корзина очищена.", reply_markup=cart_kb())
    await call.answer()

@dp.callback_query(F.data == "pay")
async def pay_fake(call: CallbackQuery):
    # Никаких платежей — просто текст
    await call.answer()
    await call.message.answer(PAYMENT_TEXT)

@dp.callback_query(F.data == "checkout")
async def checkout(call: CallbackQuery):
    user_id = call.from_user.id
    if not carts.get(user_id):
        await call.answer("Корзина пуста", show_alert=True)
        return
    await call.message.edit_text(
        "✅ Оформление заказа.\n"
        "Если все верно — нажми «Подтвердить заказ».",
        reply_markup=checkout_kb()
    )
    await call.answer()

@dp.callback_query(F.data == "confirm")
async def confirm_order(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    cart = carts.get(user_id, {})
    if not cart:
        await call.answer("Корзина пуста", show_alert=True)
        return

    # Сообщение админу
    username = call.from_user.username
    who = f"@{username}" if username else f"id:{user_id}"
    order_text = cart_text(user_id)
    admin_msg = f"🆕 Новый заказ от {who}\n\n{order_text}"

    await bot.send_message(ADMIN_ID, admin_msg)

    # Очистить корзину
    carts[user_id] = {}

    await call.message.edit_text(
        "🎉 Заказ отправлен!\n"
        "Мы свяжемся с тобой. Если нужно — нажми «Оплатить» и следуй инструкции.",
        reply_markup=main_menu_kb()
    )
    await call.answer("Заказ подтверждён ✅")

@dp.callback_query(F.data == "contacts")
async def contacts(call: CallbackQuery):
    await call.message.edit_text(
        "📩 Контакты:\n"
        "— Менеджер: @pl44ll\n"
        "— Время ответа: ноль часов нахуй \n",
        reply_markup=main_menu_kb()
    )
    await call.answer()

@dp.callback_query(F.data == "back:menu")
async def back_menu(call: CallbackQuery):
    await call.message.edit_text("Выбирай действие:", reply_markup=main_menu_kb())
    await call.answer()

async def main():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


