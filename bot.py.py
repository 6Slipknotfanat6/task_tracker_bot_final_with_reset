
import csv
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8091126446:AAGjottNjz-FEHLUJul2v6ToTawF-I1zAJM"
DATA_FILE = "reports.csv"
STEPS = [
    "Дата:",
    "Чаты просмотрены:",
    "Написал Артисту 1:",
    "Написал Артисту 2:",
    "Написал Артисту 3:",
    "Написал Артисту 4:",
    "Написал Артисту 5:",
    "Ответы в чатах:",
    "Отгружено релизы:",
    "Питчинг:",
    "Контракты составлены и отправлены:",
    "Идет процесс согласование с артистами:",
    "Бэк-каталог сделано:",
    "Дополнительно (текст):"
]

menu_keyboard = ReplyKeyboardMarkup(
    [["/start", "/submit"], ["/progress", "/total"], ["/export", "/cancel"]],
    resize_keyboard=True
)

user_reports = {}
user_states = {}

def load_reports():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline='', encoding='utf-8') as f:
        return list(csv.reader(f))

def save_report(user_id, report):
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id] + report)

def get_user_reports(user_id):
    return [row for row in load_reports() if row[0] == str(user_id)]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states[update.effective_user.id] = 0
    user_reports[update.effective_user.id] = []
    await update.message.reply_text(
        f"Добро пожаловать! Начинаем отчёт.\n{STEPS[0]}",
        reply_markup=menu_keyboard
    )

async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = 0
    user_reports[user_id] = []
    await update.message.reply_text(f"{STEPS[0]}", reply_markup=menu_keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        await update.message.reply_text("Введите /start для начала отчёта.", reply_markup=menu_keyboard)
        return

    state = user_states[user_id]
    user_reports[user_id].append(update.message.text)
    state += 1

    if state < len(STEPS):
        user_states[user_id] = state
        await update.message.reply_text(f"{STEPS[state]}", reply_markup=menu_keyboard)
    else:
        save_report(user_id, user_reports[user_id])
        del user_states[user_id]
        del user_reports[user_id]
        await update.message.reply_text("Спасибо! Отчёт сохранён.", reply_markup=menu_keyboard)

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reports = get_user_reports(update.effective_user.id)
    await update.message.reply_text(f"Вы отправили {len(reports)} отчётов.", reply_markup=menu_keyboard)

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Всего дней: {len(load_reports())}", reply_markup=menu_keyboard)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_states:
        del user_states[user_id]
        del user_reports[user_id]
    await update.message.reply_text("Отчёт отменён.", reply_markup=menu_keyboard)

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(DATA_FILE):
        await update.message.reply_text("Файл ещё не создан.", reply_markup=menu_keyboard)
        return
    await update.message.reply_document(document=open(DATA_FILE, 'rb'))

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != 371113327:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        await update.message.reply_text("Все отчёты удалены.")
    else:
        await update.message.reply_text("Файл отчётов и так пуст.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("submit", submit))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
