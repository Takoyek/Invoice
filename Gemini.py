import re
from datetime import datetime
from persiantools.jdatetime import JalaliDate

# دیکشنری پیکربندی قیمت ها بر اساس نوع بسته و مدت زمان
price_config = {
    "ده گیگ": {"default": 25},
    "بیست گیگ": {"default": 35},
    "سی گیگ": {"default": 45},
    "چهل گیگ": {"default": 55, "شصت روز": 70},
    "پنجاه گیگ": {"default": 65},
    "شصت گیگ": {"default": 78, "شصت روز": 90, "نود روز": 105},
    "هفتاد گیگ": {"default": 91},
    "هشتاد گیگ": {"default": 104, "شصت روز": 110},
    "نود گیگ": {"default": 117, "شصت روز": 120, "نود روز": 135},
    "صد گیگ": {"default": 130, "نود روز": 150},
    "صد و بیست گیگ": {"default": 156, "نود روز": 165, "صد و بیست روز": 180},
    "صد و پنجاه گیگ": {"default": 195},
}

def process_text(line):
    """
    پردازش یک خط متن و افزودن قیمت بر اساس نوع بسته و مدت زمان.

    اگر خط شامل کلمات کلیدی تمدید و نوع بسته باشد، قیمت مربوطه را به انتهای علامت ✅ اضافه می‌کند.
    در صورتی که نوع بسته تشخیص داده نشود، قیمت [000000] اضافه می‌شود تا برای بررسی دستی مشخص شود.
    """
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
        return None

    for package, prices in price_config.items():
        if package in line and not any(phrase in line for phrase in [f"صد و {package}", f"صدو {package}", f"صدو{package}"]): # جلوگیری از تداخل با بسته‌های بالاتر
            price = prices.get("default") # قیمت پیش فرض
            for day_keyword, day_price in prices.items():
                if day_keyword != "default" and day_keyword in line:
                    price = day_price # قیمت مخصوص روز
                    break # اگر قیمت روز پیدا شد، از حلقه داخلی خارج شو
            if price is not None:
                return re.sub(r"✅", f"✅  [{price}]", line)

    if "🟢" in line: # هنوز هم علامت سبز را جداگانه بررسی میکنیم
        return line.replace("🟢", "🟢  [000000]")
    elif any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅"]): # اگر هیچ کدام از بسته های بالا نبود ولی تمدید شده بود
        return re.sub(r"✅", "✅ [000000]", line) # برای بررسی دستی علامت بزن

    return line

def extract_dates(input_file_path, history_file_path, output_file_path):
    """
    استخراج تاریخ‌ها از فایل ورودی، تبدیل به شمسی و نوشتن در فایل تاریخچه و فایل خروجی.
    """
    with open(input_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    dates = re.findall(r"\[(\d{2})-([A-Za-z]{3})-(\d{2}) (\d{2}:\d{2})\]", "".join(lines))

    month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                 "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

    converted_dates = []
    miladi_dates = []
    for day, month, year, time in dates:
        year_full = int("20" + year)
        month_num = month_map[month]
        day = int(day)

        miladi_date = datetime(year_full, int(month_num), day)
        shamsi_date = JalaliDate(miladi_date).strftime("%Y/%m/%d")
        miladi_dates.append(miladi_date)

        converted_dates.append(f"--------------------------------\n{day} {month} {year_full}\n{day}-{month_num}-{year_full} {time}\n{shamsi_date}\n--------------------------------\n")

    with open(history_file_path, "w", encoding="utf-8") as file:
        file.writelines(converted_dates)

    if miladi_dates:
        first_date = miladi_dates[0]
        last_date = miladi_dates[-1]
        date_diff = (last_date - first_date).days
        first_shamsi = JalaliDate(first_date).strftime("%Y/%m/%d")
        last_shamsi = JalaliDate(last_date).strftime("%Y/%m/%d")

        with open(output_file_path, "a", encoding="utf-8") as file:
            file.write("\n________________________________________\n")
            file.write("این گزارش از تاریخ:\n")
            file.write("----------------------\n")
            file.write(f"{first_date.strftime('%d %b %Y')}\n")
            file.write(f"{first_shamsi}\n")
            file.write("----------------------\n")
            file.write("تا تاریخ:\n")
            file.write("----------------------\n")
            file.write(f"{last_date.strftime('%d %b %Y')}\n")
            file.write(f"{last_shamsi}\n")
            file.write("----------------------\n")
            file.write(f"فاصله زمانی: {date_diff} روز\n")
            file.write("________________________________________\n")

def calculate_sum_from_output(output_file_path):
    """
    محاسبه مجموع قیمت ها از فایل خروجی.
    """
    with open(output_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    numbers = [int(num) for num in re.findall(r"\[(\d+)\]", content)]
    total_sum = sum(numbers)

    with open(output_file_path, "a", encoding="utf-8") as file:
        file.write("________________________________________\n")
        file.write(f"جمع کل: {total_sum} هزار تومان\n")

def main():
    """
    تابع اصلی اسکریپت.
    """
    input_file_path = "D:\\AVIDA\\CODE\\Invoice\\Input.txt"
    output_file_path = "D:\\AVIDA\\CODE\\Invoice\\Output.txt"
    review_file_path = "D:\\AVIDA\\CODE\\Invoice\\EditMe.txt" # نام متغیر خواناتر شد
    history_file_path = "D:\\AVIDA\\CODE\\Invoice\\History.txt" # نام متغیر خواناتر شد

    processed_lines = []
    review_lines = []

    total_checkmarks = 0
    total_green_marks = 0

    with open(input_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        total_checkmarks += line.count("✅")
        total_green_marks += line.count("🟢")

        processed_line = process_text(line)
        if processed_line:
            processed_lines.append(processed_line)
            if "[000000]" in processed_line:
                review_lines.append(processed_line)

    with open(output_file_path, "w", encoding="utf-8") as file:
        file.writelines(processed_lines)
        file.write("\n\n")
        file.write("________________________________________\n")
        file.write("________________________________________\n")
        file.write("________________________________________\n")
        file.write(f"تعداد کل ✅: {total_checkmarks} عدد\n")
        file.write(f"تعداد کل 🟢: {total_green_marks} عدد\n")
        file.write("----------------------\n")
        file.write(f"تعداد کل رکوردها: {total_checkmarks + total_green_marks} عدد\n")
        file.write("________________________________________")

    with open(review_file_path, "w", encoding="utf-8") as file: # نام متغیر خواناتر شد
        file.writelines(review_lines)
        file.write(f"\nتعداد کل 🟢: {total_green_marks} عدد\n")

    extract_dates(input_file_path, history_file_path, output_file_path) # نام متغیرها خواناتر شد
    calculate_sum_from_output(output_file_path) # نام متغیر خواناتر شد

if __name__ == "__main__":
    main()