import re
import os
import sys
import logging
import configparser
import argparse
import sqlite3
from datetime import datetime
from typing import List, Dict, Union, Optional
import pandas as pd
from persiantools.jdatetime import JalaliDate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import unittest

# -------------------- تنظیمات اولیه --------------------
# ثبت فونت فارسی
try:
    pdfmetrics.registerFont(TTFont('B_Nazanin', 'fonts/B_Nazanin.ttf'))
    FONT_NAME = 'B_Nazanin'
except Exception as e:
    logging.warning(f'فونت فارسی یافت نشد: {str(e)}')
    FONT_NAME = 'Helvetica'

# تنظیمات لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# -------------------- پیکربندی --------------------
config = configparser.ConfigParser()
config.read('config.ini')

PATHS = {
    'input': config.get('PATHS', 'input', fallback='input.txt'),
    'output': config.get('PATHS', 'output', fallback='output.txt'),
    'editme': config.get('PATHS', 'editme', fallback='editme.txt'),
    'history': config.get('PATHS', 'history', fallback='history.txt'),
    'excel': config.get('PATHS', 'excel', fallback='invoice.xlsx'),
    'pdf': config.get('PATHS', 'pdf', fallback='invoice.pdf'),
    'db': config.get('PATHS', 'db', fallback='history.db')
}

# -------------------- کلاس دیتابیس --------------------
class DatabaseManager:
    """مدیریت ارتباط با دیتابیس SQLite"""
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
        
    def _create_tables(self):
        """ایجاد جداول مورد نیاز"""
        query = """
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            date TEXT NOT NULL
        );
        """
        self.conn.execute(query)
        self.conn.commit()
        
    def save_invoice(self, data: Dict):
        """ذخیره اطلاعات فاکتور در دیتابیس"""
        query = """
        INSERT INTO invoices (code, description, type, amount, date)
        VALUES (?, ?, ?, ?, ?)
        """
        self.conn.execute(query, (
            data['code'],
            data['description'],
            data['type'],
            data['amount'],
            data['date']
        ))
        self.conn.commit()
        
    def close(self):
        """بستن ارتباط با دیتابیس"""
        self.conn.close()

# -------------------- پردازش متن --------------------
def process_text(line: str) -> Optional[str]:
    """
    پردازش خط ورودی و استخراج کدهای مربوطه
    
    Args:
        line (str): خط ورودی از فایل
        
    Returns:
        Optional[str]: خط پردازش شده یا None در صورت عدم تطابق
    """
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "تمدید شد  ✅", "🟢"]):
        return None

    line = re.sub(r"\s+", " ", line).strip()

    # الگوهای تطابق
    GIG = "(گیگ|گیک|کیگ|گبگ|کیک)"
    SAD = r"صد[ .]?و?[ .]?"
    SHST = "(شصت|شصد)"
    SHST_R = "(شصت روز|شصد روز)"
    NVD_R = "نود روز"
    BIST = "بیست"

    mappings = [
        (rf"{SAD}پنجاه {GIG}", "✅  [195]"),
        (rf"{SAD}{BIST} {GIG}.*?({SAD}{BIST} روز)", "✅  [180]"),
        (rf"{SAD}{BIST} {GIG}.*?{NVD_R}", "✅  [165]"),
        (rf"{SAD}{BIST} {GIG}", "✅  [156]"),
        (rf"\bصد {GIG}\b.*?{NVD_R}", "✅  [150]"),
        (rf"\bصد {GIG}\b", "✅  [130]"),
        (rf"نود {GIG}.*?{NVD_R}", "✅  [135]"),
        (rf"نود {GIG}.*?({SHST_R})", "✅  [125]"),
        (rf"نود {GIG}", "✅  [117]"),
        (rf"هشتاد {GIG}(?!.*{SAD}هشتاد {GIG}).*?({SHST_R})", "✅  [110]"),
        (rf"هشتاد {GIG}(?!.*{SAD}هشتاد {GIG})", "✅  [104]"),
        (rf"هفتاد {GIG}", "✅  [91]"),
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG}).*?{NVD_R}", "✅  [105]"),
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG}).*?({SHST_R})", "✅  [90]"),
        (rf"{SHST} {GIG}(?!.*{SAD}{SHST} {GIG})", "✅  [78]"),
        (rf"پنجاه {GIG}(?!.*{SAD}پنجاه {GIG})", "✅  [65]"),
        (rf"چهل {GIG}(?!.*{SAD}چهل {GIG}).*?({SHST_R})", "✅  [70]"),
        (rf"چهل {GIG}(?!.*{SAD}چهل {GIG})", "✅  [55]"),
        (rf"سی {GIG}", "✅  [45]"),
        (rf"{BIST} {GIG}(?!.*{SAD}{BIST} {GIG})", "✅  [35]"),
        (rf"ده {GIG}", "✅  [25]")
    ]

    matched = False
    for pattern, replacement in mappings:
        if re.search(pattern, line):
            line = re.sub(r"✅", replacement, line)
            matched = True
            break

    #  قیمت دلخواه برای تمدید شد ✅
    if not matched and re.fullmatch(r"[\S ]+ تمدید شد ?✅", line):
        line = re.sub(r"✅", "✅  [75]", line)
        matched = True

    #  قیمت کانفیگ جدید 🟢
    if "🟢" in line:
        line = line.replace("🟢", " [75]  🟢")

    #  000000 خطوط نامفهوم
    if not matched:
        line = re.sub(r"✅", "✅  [000000]", line)

    return line + "\n" 

# -------------------- مدیریت تاریخ‌ها --------------------
def extract_dates(input_path: str, history_path: str, output_path: str) -> None:
    """
    استخراج و تبدیل تاریخ‌ها از متن
    
    Args:
        input_path (str): مسیر فایل ورودی
        history_path (str): مسیر ذخیره تاریخچه
        output_path (str): مسیر فایل خروجی
    """
    try:
        with open(input_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        logging.error(f"فایل {input_path} یافت نشد!")
        raise

    dates = re.findall(r"\[(\d{2})-([A-Za-z]{3})-(\d{2}) (\d{2}:\d{2})\]", content)
    month_map = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    converted_dates = []
    miladi_dates = []
    for day, month, year, time in dates:
        try:
            year_full = int(f"20{year}")
            month_num = month_map[month]
            miladi_date = datetime(year_full, int(month_num), int(day))
            shamsi_date = JalaliDate(miladi_date).strftime("%Y/%m/%d")
            miladi_dates.append(miladi_date)
            converted_dates.append(
                f"__________________\n"
                f"{day} {month} {year_full}\n"
                f"{day}-{month_num}-{year_full} {time}\n"
                f"{shamsi_date}\n"
                f"__________________\n"
            )
        except KeyError:
            logging.warning(f"ماه نامعتبر: {month}")
        except ValueError as e:
            logging.error(f"خطا در تبدیل تاریخ: {str(e)}")

    try:
        with open(history_path, "w", encoding="utf-8") as file:
            file.writelines(converted_dates)
    except IOError as e:
        logging.error(f"خطا در نوشتن تاریخچه: {str(e)}")

    if miladi_dates:
        try:
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
        except IndexError:
            logging.warning("تاریخ معتبری یافت نشد")

# -------------------- گزارشات مالی --------------------
def calculate_total(
    numbers: List[int], 
    discount: float = 0, 
    tax: float = 0
) -> float:
    """
    محاسبه جمع کل با در نظر گرفتن تخفیف و مالیات
    
    Args:
        numbers (List[int]): لیست اعداد
        discount (float): درصد تخفیف (بین 0 تا 1)
        tax (float): درصد مالیات (بین 0 تا 1)
        
    Returns:
        float: مبلغ نهایی
    """
    if not 0 <= discount <= 1 or not 0 <= tax <= 1:
        raise ValueError("مقادیر تخفیف و مالیات باید بین 0 و 1 باشند")
        
    total = sum(numbers)
    return total * (1 - discount) * (1 + tax)

# -------------------- خروجی اکسل --------------------
def export_to_excel(
    items: List[Dict],
    total_sum: float,
    mandeh: float,
    final_total: float,
    start_date: str,
    end_date: str,
    excel_path: str
) -> None:
    """
    تولید گزارش اکسل
    
    Args:
        items (List[Dict]): لیست آیتم‌ها
        total_sum (float): جمع کل
        mandeh (float): مانده قبلی
        final_total (float): جمع نهایی
        start_date (str): تاریخ شروع
        end_date (str): تاریخ پایان
        excel_path (str): مسیر ذخیره فایل اکسل
    """
    try:
        df = pd.DataFrame({
            'ردیف': range(1, len(items)+1,
            'کد': [item['code'] for item in items],
            'توضیحات': [item['description'] for item in items],
            'نوع': [item['type'] for item in items],
            'مبلغ': [item['amount'] for item in items],
            'تاریخ': [item['date'] for item in items]
        })
        
        total_row = pd.DataFrame({
            'ردیف': ['-'],
            'کد': ['جمع کل'],
            'توضیحات': ['-'],
            'نوع': ['-'],
            'مبلغ': [total_sum],
            'تاریخ': ['-']
        })
        
        df = pd.concat([df, total_row], ignore_index=True)
        df.to_excel(excel_path, index=False, engine='openpyxl')
        logging.info(f"فایل اکسل در {excel_path} ذخیره شد")
    except Exception as e:
        logging.error(f"خطا در تولید اکسل: {str(e)}")

# -------------------- خروجی PDF --------------------
def export_to_pdf(
    items: List[Dict],
    total_sum: float,
    mandeh: float,
    final_total: float,
    start_date: str,
    end_date: str,
    pdf_path: str
) -> None:
    """
    تولید گزارش PDF
    
    Args:
        items (List[Dict]): لیست آیتم‌ها
        total_sum (float): جمع کل
        mandeh (float): مانده قبلی
        final_total (float): جمع نهایی
        start_date (str): تاریخ شروع
        end_date (str): تاریخ پایان
        pdf_path (str): مسیر ذخیره فایل PDF
    """
    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # هدر
        c.setFont(FONT_NAME, 16)
        c.drawString(100, height-50, "گزارش صورتحساب")
        c.line(100, height-60, width-100, height-60)

        # اطلاعات تاریخ
        c.setFont(FONT_NAME, 12)
        c.drawString(100, height-100, f"تاریخ شروع: {start_date}")
        c.drawString(100, height-120, f"تاریخ پایان: {end_date}")

        # جدول اقلام
        y_position = height-150
        headers = ["ردیف", "کد", "توضیحات", "نوع", "مبلغ"]
        positions = [50, 100, 200, 350, 450]
        
        for header, pos in zip(headers, positions):
            c.drawString(pos, y_position, header)
        
        y_position -= 30
        
        for idx, item in enumerate(items, 1):
            c.drawString(50, y_position, str(idx))
            c.drawString(100, y_position, item['code'])
            c.drawString(200, y_position, item['description'][:30])
            c.drawString(350, y_position, item['type'])
            c.drawString(450, y_position, f"{item['amount']:,}")
            y_position -= 20
            
            if y_position < 100:
                c.showPage()
                y_position = height-50
                c.setFont(FONT_NAME, 12)

        # جمع‌کل
        c.setFont(FONT_NAME, 14)
        c.drawString(100, y_position-40, f"جمع فاکتور: {total_sum:,} تومان")
        c.drawString(100, y_position-70, f"مانده قبلی: {mandeh:,} تومان")
        c.drawString(100, y_position-100, f"جمع کل: {final_total:,} تومان")
        
        c.save()
        logging.info(f"فایل PDF در {pdf_path} ذخیره شد")
    except Exception as e:
        logging.error(f"خطا در تولید PDF: {str(e)}")

# -------------------- تست‌های واحد --------------------
class TestInvoiceSystem(unittest.TestCase):
    """تست‌های واحد برای سیستم صورتحساب"""
    
    def test_process_text(self):
        test_cases = [
            ("صد گیگ تمدید شد ✅", "✅  [130]\n"),
            ("نود گیگ تمدید شد ✅", "✅  [117]\n"),
            ("🟢 خرید جدید", " [000000]  🟢 خرید جدید\n")
        ]
        
        for input_line, expected in test_cases:
            with self.subTest(input_line=input_line):
                self.assertEqual(process_text(input_line), expected)
                
    def test_calculate_total(self):
        self.assertEqual(calculate_total([100, 200], 0.1, 0.09), 294.3)
        
# -------------------- واسط خط فرمان --------------------
def parse_args():
    parser = argparse.ArgumentParser(description='سیستم مدیریت صورتحساب')
    parser.add_argument('--mandeh', type=float, required=True, help='مانده قبلی')
    parser.add_argument('--discount', type=float, default=0, help='درصد تخفیف')
    parser.add_argument('--tax', type=float, default=0, help='درصد مالیات')
    return parser.parse_args()

# -------------------- تابع اصلی --------------------
def main():
    args = parse_args()
    db = DatabaseManager(PATHS['db'])
    
    try:
        # پردازش فایل ورودی
        with open(PATHS['input'], "r", encoding="utf-8") as file:
            lines = file.readlines()
            
        processed_lines = []
        items = []
        numbers = []
        
        for line in lines:
            # پردازش خط
            processed_line = process_text(line)
            if processed_line:
                processed_lines.append(processed_line)
                
                # استخراج اطلاعات برای دیتابیس
                if '[' in processed_line and '✅' in processed_line:
                    code = re.search(r'\[(\d+)\]', processed_line).group(1)
                    desc = re.sub(r'\[.*?\]', '', processed_line).replace('✅', '').strip()
                    amount = int(code)
                    numbers.append(amount)
                    
                    item_data = {
                        'code': code,
                        'description': desc,
                        'type': 'تمدیدی' if 'تمدید' in desc else 'جدید',
                        'amount': amount,
                        'date': JalaliDate.today().strftime("%Y/%m/%d")
                    }
                    db.save_invoice(item_data)
                    items.append(item_data)
        
        # محاسبات مالی
        total_sum = calculate_total(numbers, args.discount, args.tax)
        final_total = total_sum + args.mandeh
        
        # تولید گزارشات
        start_date = end_date = JalaliDate.today().strftime("%Y/%m/%d")
        
        export_to_excel(
            items=items,
            total_sum=total_sum,
            mandeh=args.mandeh,
            final_total=final_total,
            start_date=start_date,
            end_date=end_date,
            excel_path=PATHS['excel']
        )
        
        export_to_pdf(
            items=items,
            total_sum=total_sum,
            mandeh=args.mandeh,
            final_total=final_total,
            start_date=start_date,
            end_date=end_date,
            pdf_path=PATHS['pdf']
        )
        
        logging.info("پردازش با موفقیت انجام شد")
        
    except Exception as e:
        logging.error(f"خطای کلی: {str(e)}")
        sys.exit(1)
        
    finally:
        db.close()

if __name__ == "__main__":
    # اجرای تست‌ها اگر دستور --test داده شود
    if '--test' in sys.argv:
        unittest.main(argv=sys.argv[:1])
    else:
        main()