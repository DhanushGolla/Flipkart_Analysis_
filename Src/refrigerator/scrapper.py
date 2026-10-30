import re
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

Title = []
Brand = []
Capacity = []
Star_Rating = []
Door_Type = []
Compressor_Type = []
Price = []
Rating = []
Product_Warranty = []
Compressor_Warranty = []
len_products = 0

for i in range(1,31):
    url = f"https://www.flipkart.com/search?q=refrigerator&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}"
    response = requests.get(url)
    page = BeautifulSoup(response.text,"html.parser")
    Products = page.find_all("div",class_ = "jIjQ8S")
    len_products = len_products + len(Products)

    for each in Products:
        title_name = each.find("div",class_ = "RG5Slk").text
        brand_name = title_name.split(" ")[0]
        capacity_text = re.findall(r"\d+\s+L",title_name)[0]
        Door_text = re.findall(r"(\w+)\sDoor",title_name)
        star_name = re.findall(r"(\d+)\s+Star",title_name)
        price_tag = each.find("div", class_="hZ3P6w DeU9vF")
        rate_tag = each.find("div", class_="MKiFS6")

        if title_name:
            Title.append(title_name)
        else:
            Title.append(np.nan)

        if brand_name:
            Brand.append(brand_name)
        else:
            Brand.append(np.nan)

        if capacity_text:
            Capacity.append(capacity_text)
        else:
            Capacity.append(capacity_text)

        if Door_text:
            Door_Type.append(Door_text[0])
        else:
            Door_Type.append(np.nan)

        if star_name:
            Star_Rating.append(star_name[0])
        else:
            Star_Rating.append(np.nan)

        Tags = each.find_all("li",class_ = "DTBslk")
        Compressor_Type.append(Tags[0].text if Tags else np.nan)

        warranty_text = " ".join(
            tag.get_text(" ", strip=True) for tag in Tags
            if re.search(r"\bwarrant(?:y|ies)\b", tag.get_text(" ", strip=True), re.I)
        )

        warranty_text = re.sub(r"\[[^\]]*\]", "", warranty_text)

        product_warranty = np.nan
        compressor_warranty = np.nan

        matches = re.findall(r"(\d+)\s*-?\s*Years?\s*([^0-9]*)", warranty_text, re.I)

        for years, description in matches:
            if re.search(r"\bcompressor\b", description, re.I):
                compressor_warranty = int(years)
            else:
                product_warranty = int(years)

        Product_Warranty.append(product_warranty)
        Compressor_Warranty.append(compressor_warranty)

        if price_tag and price_tag.text.strip():
            cost = price_tag.text.strip().replace("₹", "").replace(",", "")
            Price.append(cost if cost.isdigit() else np.nan)
        else:
            Price.append(np.nan)

        rate = rate_tag.text.strip() if rate_tag and rate_tag.text.strip() else np.nan
        Rating.append(rate)

print("Executed")

data = pd.DataFrame({
    "Title": Title,
    "Brand": Brand,
    "Capacity": Capacity,
    "Star_Rating": Star_Rating,
    "Door_Type": Door_Type,
    "Compressor_Type": Compressor_Type,
    "Price": Price,
    "Rating": Rating,
    "Product_Warranty": Product_Warranty,
    "Compressor_Warranty": Compressor_Warranty
})

data.to_csv("refrigerator_data.csv", index=False)

