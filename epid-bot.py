import io
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8607456459:AAE7st_VDAItYSEJKfA817x6Aji5Vmc-9c4"


# ===== ЭПИДКРИВАЯ =====
def epidemic_curve(df):
    counts = df['date_onset'].value_counts().sort_index()

    plt.figure()
    counts.plot(kind='bar')
    plt.title("Epidemic Curve")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf


# ===== ТАБЛИЦА 2x2 + RR =====
def table_2x2(df):

    table = pd.crosstab(df['exposed'], df['disease'])

    a = table.loc[1,1]
    b = table.loc[1,0]
    c = table.loc[0,1]
    d = table.loc[0,0]

    rr = (a/(a+b)) / (c/(c+d))
    or_val = (a*d)/(b*c)

    text = f"""
ТАБЛИЦА 2x2

        Disease+   Disease-
Exposed     {a}          {b}
Unexposed   {c}          {d}

Attack rate exposed = {a/(a+b):.2f}
Attack rate unexposed = {c/(c+d):.2f}

RR = {rr:.2f}
OR = {or_val:.2f}
"""

    return text


# ===== ОБРАБОТКА ФАЙЛА =====
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    file = await update.message.document.get_file()
    file_path = "data.xlsx"
    await file.download_to_drive(file_path)

    df = pd.read_excel(file_path)

    # 📈 Эпидкривая
    img = epidemic_curve(df)
    await update.message.reply_photo(img)

    # 📊 Таблица 2x2
    result = table_2x2(df)
    await update.message.reply_text(result)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

app.run_polling()