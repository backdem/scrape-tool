from striprtf.striprtf import rtf_to_text

with open("./data/BTI2003-2022_CountryReports_Europe/Moldova_BTI2022.rtf") as infile:
    content = infile.read()
    text = rtf_to_text(content, encoding="utf-8", errors="ignore")
    text_as_list = text.split('\n')
    for s in text_as_list:
        print(s)
        print("-----@@@----")
        #if(s and s[0].isdigit()):
        #    print(s)

