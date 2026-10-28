import re
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

headers = { 
    "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36 Edg/156.0.0.0"
}

Brand = []
Model = []
RAM = []
storage = []
operating_system = []
display_size = []
processor = []
Price = []
Rating = []

for i in range(1, 31):
    url = f"https://www.flipkart.com/search?q=laptops&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        page = BeautifulSoup(response.text, "html.parser")
    except:
        page = None

    if page:
        Titles = page.find_all("div", class_="RG5Slk")
        product_Tag = page.find_all("div", class_="jIjQ8S")
    else:
        Titles = []
        product_Tag = []

    for Tag in Titles:
        title = Tag.text.strip() if Tag else ""
        spec = title.split(" ")[0] if title else np.nan
        Brand.append(spec if spec else np.nan)

        model_pattern = r'\b(Aspire(?:\s+Lite)?(?:\s+\d+)?|Swift\s+Neo|Chromebook(?:\s+CX\d+)?|One\s+15|Galaxy\s+Book\d+(?:\s+Edge\s+Series|\s+AI|\s+Metal)?|Alienware\s+\d+|Inspiron(?:\s+\d+)?|Vostro(?:\s+\d+)?|DELL\s+\d{1,2}|Victus(?:\s+\d+)?|Omnibook\s+\d+|HP\s+\d{1,2}|IdeaPad\s+Slim\s+\d+|LOQ(?:\s+Essential)?|Legion\s+\d+|100e\s+Chromebook\s+Gen\s+\d+|TUF\s+Gaming\s+[AF]\d+|Vivobook(?:\s+Go)?(?:\s+S?\d{1,2})?(?:\s+\(\d{4}\))?|ExpertBook\s+P\d+|MacBook\s+(?:Air|Pro)(?:\s+\([^)]*\))?|Motobook\s+60(?:\s+Pro)?|Primebook\s+\d+\s+(?:Pro|Max)|Modern\s+\d+|Katana\s+\d+|Summit(?:\s+\w+)?|Aspire\s+\d+|TUF\s+Gaming\s+F\d+|ExpertBook\s+P\d+|ROG\s+\w+|Dell\s+\d{1,2})\b'
        model_match = re.search(model_pattern, title, re.IGNORECASE)
        model_name = model_match.group(0).strip() if model_match else np.nan
        Model.append(model_name)

        os_name = re.findall(
            r"Windows\s+\d+(?:\s+(?:Home|Pro|Single\s+Language))?|"
            r"macOS(?:\s+\w+)*|"
            r"Mac\s+OS(?:\s+\w+)*|"
            r"Chrome\s+OS|Prime\s+OS|"
            r"Android\s+\d+|DOS|Tahoe",
            title,
            re.IGNORECASE
        )
        operating_system.append(os_name[0] if os_name else np.nan)

    for p_ul in product_Tag:
        ul_tag = p_ul.find("ul")
        r_val = np.nan
        s_val = np.nan
        p_val = np.nan
        d_val = np.nan
        if ul_tag:
            lis = ul_tag.find_all("li", class_="DTBslk")
            for each in lis:
                txt = each.text.strip()
                r_match = re.search(r"\b(\d+)\s*GB\b.*\bRAM\b", txt, re.IGNORECASE)
                if r_match:
                    try:
                        r_val = int(r_match.group(1))
                    except:
                        r_val = np.nan

                s_match = re.search(r"(\d+)\s*(GB|TB)\s*SSD", txt, re.IGNORECASE)
                if s_match:
                    try:
                        val = int(s_match.group(1))
                        if s_match.group(2).upper() == "TB":
                            val = val * 1024
                        s_val = val
                    except:
                        s_val = np.nan

                proc_match = re.search(r"(.+?)\s+Processor", txt, re.IGNORECASE)
                if proc_match:
                    p_val = proc_match.group(1).strip()

                disp_match = re.search(r"(\d+(?:\.\d+)?)\s*Inch", txt, re.IGNORECASE)
                if disp_match:
                    d_val = disp_match.group(1)

        RAM.append(r_val)
        storage.append(s_val)
        processor.append(p_val if p_val else np.nan)
        display_size.append(d_val if d_val else np.nan)

    for PT in product_Tag:
        price_tag = PT.find("div", class_="hZ3P6w DeU9vF")
        if price_tag and price_tag.text.strip():
            cost = price_tag.text.strip().replace("₹", "").replace(",", "")
            Price.append(cost if cost.isdigit() else np.nan)
        else:
            Price.append(np.nan)

    for RT in product_Tag:
        rate_tag = RT.find("div", class_="MKiFS6")
        rate = rate_tag.text.strip() if rate_tag and rate_tag.text.strip() else np.nan
        Rating.append(rate)

def fix_length(lst, length=720):
    if len(lst) > length:
        return lst[:length]
    else:
        return lst + [np.nan] * (length - len(lst))

Brand = fix_length(Brand)
Model = fix_length(Model)
RAM = fix_length(RAM)
storage = fix_length(storage)
operating_system = fix_length(operating_system)
processor = fix_length(processor)
display_size = fix_length(display_size)
Price = fix_length(Price)
Rating = fix_length(Rating)

df = pd.DataFrame({
    "Brand": Brand,
    "Model": Model,
    "RAM": RAM,
    "Storage": storage,
    "Operating_System": operating_system,
    "Processor": processor,
    "Display_Size": display_size,
    "Price": Price,
    "Rating": Rating
})

df.to_csv("flipkart_laptops.csv", index=False, na_rep="NaN")