# مدعی هستش که بهینه شدست
import re
import argparse
import logging
import unicodedata
from datetime import datetime
from persiantools.jdatetime import JalaliDate

def process_text(line, compiled_mappings):
    """
    پردازش یک خط متن و اعمال تغییرات بر اساس الگوهای تعریف‌شده.

    پارامترها:
    line (str): خط متنی که باید پردازش شود.
    compiled_mappings (list): لیستی از الگوهای کامپایل‌شده و جایگزین‌ها.

    خروجی:
    str یا None: خط پردازش‌شده یا None اگر شرایط لازم را نداشته باشد.
    """
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "تمدید شد  ✅", "🟢"]):
        return None

    line = unicodedata.normalize('NFC', line)  # نرمال‌سازی یونیکد
    line = re.sub(r"\s+", " ", line).strip()

    matched = False

    for pattern, replacement in compiled_mappings:
        if pattern.search(line):
            line = re.sub(r"✅", replacement, line)
            matched = True
            break

    #  قیمت دلخواه برای تمدید شد ✅
    if not matched and re.fullmatch(r"[\S ]+ تمدید شد ?✅", line):
        line = re.sub(r"✅", "✅  [75]", line)
        matched = True

    # قیمت کانفیگ جدید 🟢
    if "🟢" in line and not matched:
        line = line.replace("🟢", " [75]  🟢")
        matched = True

    # 000000 خطوط نامفهوم
    if not matched:
        line = re.sub(r"✅", "✅  [000000]", line)

    return line + "\n"

def extract_dates(input_path, history_path, output_path):
    """
    استخراج تاریخ‌ها از فایل ورودی و ذخیره آن‌ها در فایل تاریخچه.

    پارامترها:
    input_path (str): مسیر فایل ورودی.
    history_path (str): مسیر فایل تاریخچه.
    output_path (str): مسیر فایل خروجی.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        logging.error(f"فایل ورودی در مسیر {input_path} پیدا نشد.")
        return

    content = "".join(lines)
    dates = re.findall(r"\[(\d{2})-([A-Za-z]{3})-(\d{2}) (\d{2}:\d{2})\]", content)

    month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                 "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

    converted_dates = []
    miladi_dates = []
    for day, month, year, time in dates:
        try:
            year_full = int("20" + year)
            month_num = month_map[month]
            day = int(day)

            miladi_date = datetime(year_full, int(month_num), day)
            shamsi_date = JalaliDate(miladi_date).strftime("%Y/%m/%d")
            miladi_dates.append(miladi_date)

            converted_dates.append(
                f"__________________\n"
                f"{day} {month} {year_full}\n"
                f"{day}-{month_num}-{year_full} {time}\n"
                f"{shamsi_date}\n"
                f"__________________\n")
        except Exception as e:
            logging.warning(f"خطا در پردازش تاریخ: {e}")
            continue

    with open(history_path, "w", encoding="utf-8") as file:
        file.writelines(converted_dates)

    if miladi_dates:
        first_date = miladi_dates[0]
        last_date = miladi_dates[-1]
        date_diff = (last_date - first_date).days
        first_shamsi = JalaliDate(first_date).strftime("%Y/%m/%d")
        last_shamsi = JalaliDate(last_date).strftime("%Y/%m/%d")

        with open(output_path, "a", encoding="utf-8") as file:
            file.write("____________________________________\n")
            file.write("📅\n")
            file.write("این گزارش از تاریخ:\n")
            file.write(f"{first_shamsi}\n")
            file.write(f"{first_date.strftime('%d %b %Y')}\n")
            file.write("تا تاریخ:\n")
            file.write(f"{last_shamsi}\n")
            file.write(f"{last_date.strftime('%d %b %Y')}\n")
            file.write(f"فاصله زمانی: {date_diff} روز\n")

def calculate_sum_from_output(output_path, MANDEH, current_date_str):
    """
    محاسبه مجموع اعداد از فایل خروجی و نوشتن نتایج در همان فایل.

    پارامترها:
    output_path (str): مسیر فایل خروجی.
    MANDEH (int): مبلغ مانده قبلی.
    current_date_str (str): تاریخ فعلی به صورت رشته.
    """
    try:
        with open(output_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        logging.error(f"فایل خروجی در مسیر {output_path} پیدا نشد.")
        return

    numbers = [int(num) for num in re.findall(r"\[(\d+)\]", content)]
    total_sum = sum(numbers)

    with open(output_path, "a", encoding="utf-8") as file:
        file.write("____________________________________\n")
        file.write("📝\n")
        file.write(f"مبلغ این فاکتور: `{total_sum}`\n")
        file.write(f"مبلغ مانده از قبل: `{MANDEH}`\n\n")
        file.write(f"در تاریخ:  {current_date_str}\n")
        file.write(f"جمع کل مانده حساب شما:  `{int(MANDEH) + total_sum}` هزار تومان")
        file.write("\n.")

def read_lines_from_file(file_path):
    """
    خواندن خطوط از یک فایل.

    پارامترها:
    file_path (str): مسیر فایل.

    خروجی:
    list: لیستی از خطوط فایل.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        logging.error(f"فایل در مسیر {file_path} پیدا نشد.")
        return []

def write_lines_to_file(file_path, lines):
    """
    نوشتن خطوط در یک فایل.

    پارامترها:
    file_path (str): مسیر فایل.
    lines (list): لیستی از خطوط برای نوشتن.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(lines)

def main():
    parser = argparse.ArgumentParser(description='پردازش اطلاعات صورتحساب.')
    parser.add_argument('--input', default='Input.txt', help='مسیر فایل ورودی')
    parser.add_argument('--output', default='Output.txt', help='مسیر فایل خروجی')
    parser.add_argument('--editme', default='EditMe.txt', help='مسیر فایل EditMe')
    parser.add_argument('--history', default='History.txt', help='مسیر فایل تاریخچه')
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    editme_path = args.editme
    history_path = args.history

    # تنظیمات لاگینگ
    logging.basicConfig(level=logging.INFO)
    logging.info("Start processing")

    GIG = "(گیگ|گیک|کیگ|گبگ|کیک)"
    SAD = r"صد[ .]?و?[ .]?"
    SHST = "(شصت|شصد)"
    SHST_R = "(شصت روز|شصد روز)"
    NVD_R = "نود روز"
    BIST = "بیست"

    mappings = [
        (rf"{SAD}پنجاه {GIG}", "✅  [195]"),  # 150G
        (rf"{SAD}{BIST} {GIG}.*?({SAD}{BIST} روز)", "✅  [180]"),  # 120G  120R
        (rf"{SAD}{BIST} {GIG}.*?{NVD_R}", "✅  [165]"),  # 120G  90R
        (rf"{SAD}{BIST} {GIG}", "✅  [156]"),  # 120G   30R 60R
        (rf"\bصد {GIG}\b.*?{NVD_R}", "✅  [150]"),  # 100G  90R
        (rf"\bصد {GIG}\b", "✅  [130]"),  # 100G  30R 60R
        (rf"نود {GIG}.*?{NVD_R}", "✅  [135]"),  # 90G  90R
        (rf"نود {GIG}.*?({SHST_R})", "✅  [125]"),  # 90G  60R
        (rf"نود {GIG}", "✅  [117]"),  # 90G
        (rf"هشتاد {GIG}(?!.*{SAD}هشتاد {GIG}).*?({SHST_R})", "✅  [110]"),  # 80G  60R
        (rf"هشتاد {GIG}(?!.*{SAD}هشتاد {GIG})", "✅  [104]"),  # 80G
        (rf"هفتاد {GIG}", "✅  [91]"),  # 70G
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG}).*?{NVD_R}", "✅  [105]"),  # 60G  90R
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG}).*?({SHST_R})", "✅  [90]"),  # 60G  60R
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG})", "✅  [78]"),  # 60G
        (rf"پنجاه {GIG}(?!.*{SAD}پنجاه {GIG})", "✅  [65]"),  # 50G
        (rf"چهل {GIG}(?!.*{SAD}چهل {GIG}).*?({SHST_R})", "✅  [70]"),  # 40G  60R
        (rf"چهل {GIG}(?!.*{SAD}چهل {GIG})", "✅  [55]"),  # 40G
        (rf"سی {GIG}", "✅  [45]"),  # 30G
        (rf"{BIST} {GIG}(?!.*{SAD}{BIST} {GIG})", "✅  [35]"),  # 20G
        (rf"ده {GIG}", "✅  [25]")  # 10G
    ]

    compiled_mappings = [(re.compile(pattern), replacement) for pattern, replacement in mappings]

    processed_lines = []
    review_lines = []

    total_checkmarks = 0
    total_green_marks = 0

    lines = read_lines_from_file(input_path)

    checkmark_phrases = ["تمدید شد ✅", "تمدید شد✅", "تمدید شد  ✅"]

    for line in lines:
        total_checkmarks += sum(line.count(phrase) for phrase in checkmark_phrases)
        total_green_marks += line.count("🟢")

        processed_line = process_text(line, compiled_mappings)
        if processed_line:
            processed_lines.append(processed_line)
            if "[000000]" in processed_line:
                review_lines.append(processed_line)

    output_content = [
        " 🧮  صورتحساب شما:\n",
        "____________________________________\n\n"
    ]
    output_content.extend(processed_lines)
    output_content.extend([
        "____________________________________\n",
        "📊\n",
        f"✅ تعداد تمدیدی ها:  {total_checkmarks} عدد \n",
        f"🟢 تعداد خرید های جدید:  {total_green_marks} عدد \n",
        f"تعداد کل سفارشات:  {total_checkmarks + total_green_marks} عدد \n"
    ])

    write_lines_to_file(output_path, output_content)
    write_lines_to_file(editme_path, review_lines + [f"\nتعداد کل 🟢: {total_green_marks} عدد\n"])

    extract_dates(input_path, history_path, output_path)

    # محاسبه تاریخ شمسی فعلی
    shamsi_today = JalaliDate.today()
    current_date_str = f"{shamsi_today.year}/{shamsi_today.month}/{shamsi_today.day}"

    # دریافت ورودی مانده قبلی از کاربر با اعتبارسنجی
    while True:
        MANDEH = input("Mandeh Ghabli: ")
        try:
            MANDEH = int(MANDEH)
            break
        except ValueError:
            print("Lotfan addade sahih vared konid:")

    calculate_sum_from_output(output_path, MANDEH, current_date_str)

    logging.info("Processing completed.")

if __name__ == "__main__":
    main()
