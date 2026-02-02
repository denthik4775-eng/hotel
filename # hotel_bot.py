
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiosqlite

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BOT_TOKEN = "--------------"
HOTEL_SITE = "-------------"
MANAGER_PHONE = "-------------"
YOUR_ADMIN_ID = ----------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

DB_PATH = "hotel_stats.db"

class BotStates(StatesGroup):
    waiting_search = State()

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, action TEXT, room_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏨 About Hotel", callback_data="about")],
        [InlineKeyboardButton(text="🛏️ Room Types", callback_data="rooms")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton(text="🌐 BOOK NOW", url="https://google.com")],
        [InlineKeyboardButton(text="📞 Contact", callback_data="contact")]
    ])

def rooms_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛋️ Studio • £89/night", callback_data="room_studio")],
        [InlineKeyboardButton(text="🛏️ One Bedroom • £129/night", callback_data="room_onebed")],
        [InlineKeyboardButton(text="👨‍👩‍👧 Two Bedroom • £179/night", callback_data="room_twobed")],
        [InlineKeyboardButton(text="🏰 Penthouse • £299/night", callback_data="room_penthouse")],
        [InlineKeyboardButton(text="◀️ Back", callback_data="main")]
    ])

def faq_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧹 Check-in/out times", callback_data="faq_checkin")],
        [InlineKeyboardButton(text="🚗 Parking", callback_data="faq_parking")],
        [InlineKeyboardButton(text="🌐 WiFi", callback_data="faq_wifi")],
        [InlineKeyboardButton(text="👨‍👩‍👧 Children policy", callback_data="faq_children")],
        [InlineKeyboardButton(text="◀️ Back", callback_data="main")]
    ])

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🏨 *Welcome to London Luxury Apartments!*\n\n"
        "*Modern apartments in the heart of London.*\n"
        "Book directly with us and **save up to 25%!**\n\n"
        "Choose what interests you:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query()
async def handle_all_callbacks(callback: CallbackQuery):
    data = callback.data
    
    if data == "about":
        text = (
            "🏨 *About London Luxury Apartments*\n\n"
            "✨ *Modern & Comfortable*\n"
            "📍 *Central London* - 5 min to Oxford Street\n"
            "🛎️ *24/7 Reception*\n"
            "🌐 *Free High-Speed WiFi*\n"
            "🧹 *Daily Cleaning*\n\n"
            "*Fully equipped kitchen • Smart TV • Netflix*"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 BOOK NOW", url="https://google.com")],
            [InlineKeyboardButton(text="◀️ Main Menu", callback_data="main")]
        ])
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    
    elif data == "rooms":
        text = "🛏️ *Choose apartment type*\n\n*All prices per night. Direct booking discount 25%*"
        kb = rooms_keyboard()
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    
    elif data == "faq":
        text = "❓ *Frequently Asked Questions*\n\nSelect topic:"
        kb = faq_keyboard()
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    
    # ✅ КОНТАКТ - ПРОСТОЙ ТЕКСТ БЕЗ Markdown + БЕЗ tel:
    elif data == "contact":
        text = """📞 Contact Us 24/7

📱 Manager: +7 (999) 530-77-24
✉️ Email: booking@luxlondon.com
🌐 Website: https://google.com

💬 Direct booking = 25% discount!"""
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 BOOK NOW", url="https://google.com")],
            [InlineKeyboardButton(text="◀️ Main Menu", callback_data="main")]
        ])
        await callback.message.edit_text(text, reply_markup=kb)  # БЕЗ parse_mode!
    
    elif data == "main":
        text = "🏨 *London Luxury Apartments*\n\nWhat would you like to know?"
        kb = main_keyboard()
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    
    elif data.startswith("room_"):
        room_type = data.split("_")[1]
        rooms = {
            "studio": "🛋️ Studio Apartment • £89/night\n• 25m² • Queen bed • Kitchenette",
            "onebed": "🛏️ One Bedroom • £129/night\n• 45m² • King bed + sofa • Full kitchen", 
            "twobed": "👨‍👩‍👧 Two Bedroom • £179/night\n• 70m² • 2 bedrooms • Living room",
            "penthouse": "🏰 Penthouse • £299/night\n• 120m² • Rooftop terrace • Sauna"
        }
        text = f"{rooms.get(room_type, rooms['studio'])}\n\n✨ 25% discount direct booking"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 BOOK NOW", url="https://google.com")],
            [InlineKeyboardButton(text="📞 Contact", callback_data="contact")],
            [InlineKeyboardButton(text="◀️ Rooms", callback_data="rooms")],
            [InlineKeyboardButton(text="🏠 Main", callback_data="main")]
        ])
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    
    elif data.startswith("faq_"):
        faqs = {
            "faq_checkin": "🧹 Check-in: 15:00 | Check-out: 11:00\nEarly: +£30 | Late: +£50",
            "faq_parking": "🚗 Free private parking • 24/7 garage", 
            "faq_wifi": "🌐 Free unlimited WiFi • 500 Mbps",
            "faq_children": "👨‍👩‍👧 Children 0-6 FREE"
        }
        text = faqs.get(data, "❓ Select question")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
            [InlineKeyboardButton(text="🌐 BOOK NOW", url="https://google.com")],
            [InlineKeyboardButton(text="🏠 Main", callback_data="main")]
        ])
        await callback.message.edit_text(text, reply_markup=kb)
    
    await callback.answer()

async def save_stat(user_id: int, action: str):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO stats (user_id, action) VALUES (?, ?)", (user_id, action))
            await db.commit()
    except:
        pass

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != YOUR_ADMIN_ID:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT action, COUNT(*) FROM stats GROUP BY action")
        stats = await cursor.fetchall()
    text = "📊 Statistics:\n" + "\n".join([f"• {a}: {c}" for a, c in stats]) if stats else "No stats"
    await message.answer(text)

async def main():
    await init_db()
    commands = [
        BotCommand(command="start", description="🏨 Welcome"),
        BotCommand(command="stats", description="📊 Statistics")
    ]
    await bot.set_my_commands(commands)
    print("🚀 Bot started! ✅ Contact WORKS!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
