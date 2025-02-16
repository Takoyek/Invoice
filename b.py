b




def process_text(line):
    if not any(keyword in line for keyword in ["تمدید شد ✅", "تمدید شد✅", "🟢"]):
        return None




    if "بیست گیگ" in line and not any(phrase in line for phrase in ["صد و بیست گیگ", "صدو بیست گیگ", "صدوبیست گیگ"]):
        return re.sub(r"✅", "✅  [35]", line)



    if "بیست گیگ" in line and not any(phrase in line for phrase in ["صد و بیست گیگ", "صدو بیست گیگ", "صدوبیست گیگ"]):
        return re.sub(r"✅", "✅  [35]", line)




    if any(gig in line for gig in ["شصت گیگ", "شصد گیگ"]) and \
       not any(phrase in line for phrase in ["صد و شصت گیگ", "صدو شصت گیگ", "صدوشصت گیگ"]):
        if any(day in line for day in ["شصت روز", "شصد روز"]):
            return re.sub(r"✅", "✅  [90]", line)
        elif "نود روز" in line:
            return re.sub(r"✅", "✅  [105]", line)
        return re.sub(r"✅", "✅  [78]", line)

    
        
    if any(gig in line for gig in ["شصت گیگ", "شصد گیگ"]) and \
       not any(phrase in line for phrase in ["صد و شصت گیگ", "صدو شصت گیگ", "صدوشصت گیگ"]):
        if any(day in line for day in ["شصت روز", "شصد روز"]):
            return re.sub(r"✅", "✅  [90]", line)
        elif "نود روز" in line:
            return re.sub(r"✅", "✅  [105]", line)
        return re.sub(r"✅", "✅  [78]", line)