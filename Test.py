import re

def process_text(line, counts):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
        return None

    # شرط ده گیگ (اولویت اول)
    if "ده گیگ" in line:
        line = re.sub(r"✅", "✅  [25]", line)
        counts['total'] += 1
        return line

    # شرط بیست گیگ
    if "بیست گیگ" in line and not any(phrase in line for phrase in ["صد و بیست گیگ", "صدوبیست گیگ"]):
        line = re.sub(r"✅", "✅  [35]", line)
        counts['total'] += 1
        return line

    # شرط سی گیگ
    if "سی گیگ" in line:
        line = re.sub(r"✅", "✅  [45]", line)
        counts['total'] += 1
        return line

    # شرط جدید چهل گیگ <-- اضافه شد
    if "چهل گیگ" in line and not any(phrase in line for phrase in ["صد و چهل گیگ", "صدو چهل گیگ", "صدوچهل گیگ"]):
        if any(day in line for day in ["شصد روز", "شصت روز"]):
            line = re.sub(r"✅", "✅  [70]", line)
        else:
            line = re.sub(r"✅", "✅  [55]", line)
        counts['total'] += 1
        return line

    # بقیه شرایط اصلی
    if "شصد گیگ" in line:
        if "سی روز" in line:
            line = line.replace("✅", "✅  [78]")
        elif "شصد روز" in line:
            line = line.replace("✅", "✅  [90]")
        elif "نود روز" in line:
            line = line.replace("✅", "✅  [105]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "هفتاد گیگ" in line:
        if "سی روز" in line:
            line = line.replace("✅", "✅  [91]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "هشتاد گیگ" in line:
        if "سی روز" in line:
            line = line.replace("✅", "✅  [104]")
        elif "شصد روز" in line:
            line = line.replace("✅", "✅  [110]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "نود گیگ" in line:
        if "سی روز" in line:
            line = line.replace("✅", "✅  [117]")
        elif "شصد روز" in line:
            line = line.replace("✅", "✅  [125]")
        elif "نود روز" in line:
            line = line.replace("✅", "✅  [135]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "صد گیگ" in line:
        if "سی روز" in line or "شصد روز" in line:
            line = line.replace("✅", "✅  [130]")
        elif "نود روز" in line:
            line = line.replace("✅", "✅  [150]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "صد و بیست گیگ" in line:
        if "سی روز" in line or "شصد روز" in line:
            line = line.replace("✅", "✅  [156]")
        elif "نود روز" in line:
            line = line.replace("✅", "✅  [165]")
        else:
            line = line.replace("✅", "✅  [000000]")
    
    if "صد و پنجاه گیگ" in line:
        if "سی روز" in line or "شصد روز" in line or "نود روز" in line:
            line = line.replace("✅", "✅  [195]")
        else:
            line = line.replace("✅", "✅  [000000]")

    # دیکشنری replacements بدون کلیدهای ده گیگ، بیست گیگ و سی گیگ <-- تغییر
    replacements = {
        "پنجاه گیگ": "✅  [65]",
        "صدو بیست گیگ": "✅  [000000]",
        "صدو پنجاه گیگ": "✅  [000000]"
    }
    
    modified = False
    needs_review = False
    for key, value in replacements.items():
        if key in line:
            line = re.sub(r"✅", value, line)
            modified = True
            if "000000" in value:
                needs_review = True
    
    if "🟢" in line:
        line = line.replace("🟢", "🟢  [000000]")
        needs_review = True
        modified = True
    
    if modified:
        counts['total'] += 1
    
    if needs_review:
        counts['needs_review'] += 1

    counts['total_checkmarks'] += line.count("✅")
    counts['total_green'] += line.count("🟢")
    
    return line

# بقیه کد بدون تغییر (تابع main و ...)

# بقیه کد بدون تغییر می‌ماند (تابع main و ...)

# بخش replacements حذف شد تا تداخلی ایجاد نشود

def main():
    input_path = "D:\\AVIDA\\CODE\\Invoice\\Input.txt"
    output_path = "D:\\AVIDA\\CODE\\Invoice\\Output.txt"
    editme_path = "D:\\AVIDA\\CODE\\Invoice\\EditMe.txt"

    counts = {
        "total": 0,
        "needs_review": 0,
        "sum": 0,
        "actual_total": 0,
        "total_checkmarks": 0,
        "total_green": 0
    }
    processed_lines = []
    review_lines = []
    
    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    for line in lines:
        processed_line = process_text(line, counts)
        if processed_line:
            processed_lines.append(processed_line)
            
            if "[000000]" in processed_line:
                review_lines.append(processed_line)
            
            matches = re.findall(r"\\[(\\d+)\\]", processed_line)
            for match in matches:
                if match != "000000":
                    counts['sum'] += int(match)
    
    counts['actual_total'] = counts['total']
    
    processed_lines.append(f"\nتعداد کل ✅: {counts['total_checkmarks']}\n")
    processed_lines.append(f"تعداد کل 🟢: {counts['total_green']}\n")
    processed_lines.append(f"مجموع رکوردها: {counts['total_checkmarks'] + counts['total_green']}\n")
    processed_lines.append(f"تعداد رکوردهایی که نیاز به بررسی دارد: {counts['needs_review']} عدد\n")
    
    with open(output_path, "w", encoding="utf-8") as file:
        file.writelines(processed_lines)
    
    with open(editme_path, "w", encoding="utf-8") as file:
        file.writelines(review_lines)
        file.write(f"\nتعداد رکوردهایی که نیاز به بررسی دارد: {counts['needs_review']} عدد\n")
    
    with open(output_path, "a", encoding="utf-8") as file:
        file.write(f"جمع کل: {counts['sum']} هزار تومان\n")
    
if __name__ == "__main__":
    main()
