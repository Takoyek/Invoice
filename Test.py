import re

def process_text(line, counts):
    # شمارش ✅ در تمام خطوط (حتی غیرقابل پردازش)
    counts['total_checkmarks'] += line.count("✅")
    
    # بررسی آیا خط قابل پردازش است
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
        return None
    
    # شمارش 🟢 فقط در خطوط قابل پردازش <-- تغییر کلیدی
    counts['total_green'] += line.count("🟢")
    
    # بقیه منطق پردازش
    if "ده گیگ" in line:
        line = re.sub(r"✅", "✅  [25]", line)
        counts['total'] += 1
        return line


    # اولویت ۱: ده گیگ
    if "ده گیگ" in line:
        line = re.sub(r"✅", "✅  [25]", line)
        counts['total'] += 1
        return line

    # اولویت ۲: بیست گیگ
    if "بیست گیگ" in line and not any(phrase in line for phrase in ["صد و بیست گیگ", "صدو بیست گیگ", "صدوبیست گیگ"]):
        line = re.sub(r"✅", "✅  [35]", line)
        counts['total'] += 1
        return line

    # اولویت ۳: سی گیگ
    if "سی گیگ" in line:
        line = re.sub(r"✅", "✅  [45]", line)
        counts['total'] += 1
        return line

    # اولویت ۴: چهل گیگ
    if "چهل گیگ" in line and not any(phrase in line for phrase in ["صد و چهل گیگ", "صدو چهل گیگ", "صدوچهل گیگ"]):
        if any(day in line for day in ["شصد روز", "شصت روز"]):
            line = re.sub(r"✅", "✅  [70]", line)
        else:
            line = re.sub(r"✅", "✅  [55]", line)
        counts['total'] += 1
        return line

    # اولویت ۵: پنجاه گیگ
    if "پنجاه گیگ" in line and not any(phrase in line for phrase in ["صد و پنجاه گیگ", "صدو پنجاه گیگ", "صدوپنجاه گیگ"]):
        line = re.sub(r"✅", "✅  [65]", line)
        counts['total'] += 1
        return line

    # اولویت ۶: شصت گیگ
    if any(gig in line for gig in ["شصت گیگ", "شصد گیگ"]) and \
       not any(phrase in line for phrase in ["صد و شصت گیگ", "صدو شصت گیگ", "صدوشصت گیگ"]):
        if any(day in line for day in ["نود روز"]):
            line = re.sub(r"✅", "✅  [105]", line)
        elif any(day in line for day in ["شصت روز", "شصد روز"]):
            line = re.sub(r"✅", "✅  [90]", line)
        else:
            line = re.sub(r"✅", "✅  [78]", line)
        counts['total'] += 1
        return line

    # اولویت ۷: هفتاد گیگ
    if "هفتاد گیگ" in line:
        line = re.sub(r"✅", "✅  [91]", line)
        counts['total'] += 1
        return line

    # اولویت ۸: هشتاد گیگ
    if "هشتاد گیگ" in line and not any(phrase in line for phrase in ["صد و هشتاد گیگ", "صدو هشتاد گیگ", "صدوهشتاد گیگ"]):
        if any(day in line for day in ["شصت روز", "شصد روز"]):
            line = re.sub(r"✅", "✅  [110]", line)
        else:
            line = re.sub(r"✅", "✅  [104]", line)
        counts['total'] += 1
        return line

    # اولویت ۹: نود گیگ
    if "نود گیگ" in line:
        if "نود روز" in line:
            line = re.sub(r"✅", "✅  [135]", line)
        else:
            line = re.sub(r"✅", "✅  [117]", line)
        counts['total'] += 1
        return line

    # اولویت 10: صد گیگ
    if "صد گیگ" in line:
        if "نود روز" in line:
            line = re.sub(r"✅", "✅  [150]", line)
        else:
            line = re.sub(r"✅", "✅  [130]", line)
        counts['total'] += 1
        return line
    
    # اولویت 11: صد و بیست گیگ
    if any(phrase in line for phrase in ["صد و بیست گیگ", "صدو بیست گیگ", "صدوبیست گیگ"]):
        if any(day in line for day in ["صد و بیست روز", "صدو بیست روز", "صدوبیست روز"]):
            line = re.sub(r"✅", "✅  [180]", line)
        elif "نود روز" in line:
            line = re.sub(r"✅", "✅  [165]", line)
        else:
            line = re.sub(r"✅", "✅  [156]", line)
        counts['total'] += 1
        return line

    # اولویت 12: صد و پنجاه گیگ
    if any(phrase in line for phrase in ["صد و پنجاه گیگ", "صدو پنجاه گیگ", "صدوپنجاه گیگ"]):
        line = re.sub(r"✅", "✅  [195]", line)
        counts['total'] += 1
        return line


    # دیکشنری replacements
    replacements = {}
    
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
