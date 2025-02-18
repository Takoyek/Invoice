import re

def replace_text(input_text):
    # جستجو برای عبارت "تمدید شد ✅" یا مشابه آن
    pattern = r"تمدید شد ✅|تمدید شد✅|تمدید شد  ✅|🟢"
    # اگر عبارت موجود باشد، آن را با "تمدید شد ✅ [45]" جایگزین کن
    output_text = re.sub(pattern, "تمدید شد ✅ [45]", input_text)
    return output_text

def main():
    input_path = "D:\\AVIDA\\CODE\\Invoice\\Input.txt"
    output_path = "D:\\AVIDA\\CODE\\Invoice\\Output.txt"
    
    # خواندن محتوای فایل ورودی
    with open(input_path, 'r', encoding='utf-8') as input_file:
        lines = input_file.readlines()
    
    # آماده کردن لیستی برای ذخیره خطوط تغییر یافته
    filtered_lines = []
    
    # فیلتر کردن خطوطی که شامل یکی از عبارت‌های مشخص شده هستند
    for line in lines:
        if re.search(r"تمدید شد ✅|تمدید شد✅|تمدید شد  ✅|🟢", line):
            # اعمال تغییرات بر روی هر خطی که شرایط را برآورده می‌کند
            filtered_lines.append(replace_text(line))
    
    # نوشتن خطوط فیلتر شده و تغییر یافته به فایل خروجی
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(filtered_lines)

    print("تغییرات با موفقیت انجام شد و فقط خطوط مورد نظر در فایل خروجی ذخیره گردید.")

if __name__ == "__main__":
    main()
