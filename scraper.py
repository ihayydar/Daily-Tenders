import requests
from bs4 import BeautifulSoup
import datetime

# Aap ke tamam zaroori keywords
KEYWORDS = [
    "printing", "giveaway", "stationery", "book", "textbook", 
    "answer cop", "omr", "paper", "board", "university", 
    "office", "newspaper", "daily dawn", "jang", "express"
]

# Multiple websites (OCR aur manual data cover karne ke liye)
SOURCES = [
    {"name": "PPRA Federal", "url": "https://www.ppra.org.pk/tenders.asp"},
    {"name": "Tenders PK", "url": "https://www.tenders.com.pk/category/printing"}
]

def fetch_tenders():
    print("Tenders search ho rahe hain...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    all_tenders = []
    
    for source in SOURCES:
        try:
            print(f"Searching in {source['name']}...")
            response = requests.get(source['url'], headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            rows = soup.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 3:
                    title = cols[1].text.strip()
                    department = cols[2].text.strip()
                    closing_date = cols[3].text.strip()
                    
                    link_tag = cols[1].find('a')
                    pdf_link = link_tag['href'] if link_tag else "#"
                    
                    if pdf_link.startswith('/'):
                        if "ppra" in source['url']:
                            pdf_link = "https://www.ppra.org.pk" + pdf_link
                        else:
                            pdf_link = "https://www.tenders.com.pk" + pdf_link

                    # Keyword check (bina error ke)
                    if any(kw.lower() in title.lower() for kw in KEYWORDS):
                        all_tenders.append({
                            "title": title,
                            "department": department,
                            "date": closing_date,
                            "link": pdf_link,
                            "source": source['name']
                        })
        except Exception as e:
            print(f"Error in {source['name']}: {e}. Skipping to next...")
            
    return all_tenders

def generate_html(tenders):
    today_date = datetime.datetime.now().strftime("%d %B %Y - %I:%M %p")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Tenders Report - Pakistan</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #2c3e50; font-size: 28px; }}
            .date-header {{ text-align: center; color: #7f8c8d; margin-bottom: 30px; font-weight: bold; }}
            .table-container {{ overflow-x: auto; }}
            table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #e9ecef; }}
            th {{ background-color: #34495e; color: white; font-weight: 600; text-transform: uppercase; font-size: 14px; }}
            tr:hover {{ background-color: #f1f4f6; }}
            .source-badge {{ background-color: #e74c3c; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
            .source-ppra {{ background-color: #2980b9; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
            .btn {{ display: inline-block; padding: 8px 16px; background: #27ae60; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; transition: 0.3s; }}
            .btn:hover {{ background: #2ecc71; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
        </style>
    </head>
    <body>
        <h1>Pakistan Tenders (Office, Stationery, Printing)</h1>
        <div class="date-header">Last Updated: {today_date}</div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Tender Title</th>
                        <th>Department</th>
                        <th>Source</th>
                        <th>Closing Date</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    if not tenders:
        html_content += "<tr><td colspan='5' style='text-align:center; padding: 30px; color: #7f8c8d;'>Aaj in keywords ke mutabiq koi tender nahi mila.</td></tr>"
    else:
        for t in tenders:
            badge_class = "source-ppra" if "PPRA" in t['source'] else "source-badge"
            html_content += f"""
                <tr>
                    <td style="font-weight: 500; color: #2c3e50;">{t['title']}</td>
                    <td style="color: #34495e;">{t['department']}</td>
                    <td><span class="{badge_class}">{t['source']}</span></td>
                    <td style="color: #e67e22; font-weight: bold;">{t['date']}</td>
                    <td><a href="{t['link']}" class="btn" target="_blank">Download PDF</a></td>
                </tr>
            """
            
    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    print("index.html successfully updated!")

if __name__ == "__main__":
    found_tenders = fetch_tenders()
    generate_html(found_tenders)
