import re

def process_text(line):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
        return None

    if "ده گیگ" in line:
        return re.sub(r"✅", "✅  [25]", line)

    if "بیست گیگ" in line and not any(phrase in line for phrase in ["صد و بیست گیگ", "صدو بیست گیگ", "صدوبیست گیگ"]):
        return re.sub(r"✅", "✅  [35]", line)

    if "سی گیگ" in line:
        return re.sub(r"✅", "✅  [45]", line)

    if "چهل گیگ" in line and not any(phrase in line for phrase in ["صد و چهل گیگ", "صدو چهل گیگ", "صدوچهل گیگ"]):
        if any(day in line for day in ["شصد روز", "شصت روز"]):
            return re.sub(r"✅", "✅  [70]", line)
        return re.sub(r"✅", "✅  [55]", line)

    if "پنجاه گیگ" in line and not any(phrase in line for phrase in ["صد و پنجاه گیگ", "صدو پنجاه گیگ", "صدوپنجاه گیگ"]):
        return re.sub(r"✅", "✅  [65]", line)

    if any(gig in line for gig in ["شصت گیگ", "شصد گیگ"]) and \
       not any(phrase in line for phrase in ["صد و شصت گیگ", "صدو شصت گیگ", "صدوشصت گیگ"]):
        if "نود روز" in line:
            return re.sub(r"✅", "✅  [105]", line)
        elif any(day in line for day in ["شصت روز", "شصد روز"]):
            return re.sub(r"✅", "✅  [90]", line)
        return re.sub(r"✅", "✅  [78]", line)

    if "هفتاد گیگ" in line:
        return re.sub(r"✅", "✅  [91]", line)

    if "هشتاد گیگ" in line and not any(phrase in line for phrase in ["صد و هشتاد گیگ", "صدو هشتاد گیگ", "صدوهشتاد گیگ"]):
        if any(day in line for day in ["شصت روز", "شصد روز"]):
            return re.sub(r"✅", "✅  [110]", line)
        return re.sub(r"✅", "✅  [104]", line)

    if "نود گیگ" in line:
        if "نود روز" in line:
            return re.sub(r"✅", "✅  [135]", line)
        return re.sub(r"✅", "✅  [117]", line)

    if "صد گیگ" in line:
        if "نود روز" in line:
            return re.sub(r"✅", "✅  [150]", line)
        return re.sub(r"✅", "✅  [130]", line)

    if any(phrase in line for phrase in ["صد و بیست گیگ", "صدو بیست گیگ", "صدوبیست گیگ"]):
        if any(day in line for day in ["صد و بیست روز", "صدو بیست روز", "صدوبیست روز"]):
            return re.sub(r"✅", "✅  [180]", line)
        elif "نود روز" in line:
            return re.sub(r"✅", "✅  [165]", line)
        return re.sub(r"✅", "✅  [156]", line)

    if any(phrase in line for phrase in ["صد و پنجاه گیگ", "صدو پنجاه گیگ", "صدوپنجاه گیگ"]):
        return re.sub(r"✅", "✅  [195]", line)

    if "🟢" in line:
        return line.replace("🟢", "🟢  [000000]")

    return line

def main():
    input_path = "D:\\AVIDA\\CODE\\Invoice\\Input.txt"
    output_path = "D:\\AVIDA\\CODE\\Invoice\\Output.txt"
    editme_path = "D:\\AVIDA\\CODE\\Invoice\\EditMe.txt"

    processed_lines = []
    review_lines = []
    
    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    for line in lines:
        processed_line = process_text(line)
        if processed_line:
            processed_lines.append(processed_line)
            if "[000000]" in processed_line:
                review_lines.append(processed_line)

    with open(output_path, "w", encoding="utf-8") as file:
        file.writelines(processed_lines)
    
    with open(editme_path, "w", encoding="utf-8") as file:
        file.writelines(review_lines)

if __name__ == "__main__":
    main()