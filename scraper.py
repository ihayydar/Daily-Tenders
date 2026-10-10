import requests
from bs4 import BeautifulSoup
import datetime

KEYWORDS = [
    "printing", "giveaway", "stationery", "book", "textbook", 
    "answer cop", "omr", "paper", "board", "university", 
    "office", "supply", "publication", "cards", "publishing"
]

def fetch_ppra_tenders():
    print("Fetching PPRA tenders...")
    url = "https://www.ppra.org.pk/tenders.asp"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    tenders = []
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    text_content = row.text.strip()
                    
                    # Keyword matching
                    if any(kw.lower() in text_content.lower() for kw in KEYWORDS):
                        links = row.find_all('a')
                        pdf_link = "#"
                        for l in links:
                            href = l.get('href', '')
                            if href and ('upload' in href.lower() or 'pdf' in href.lower() or 'doc' in href.lower() or 'tender' in href.lower()):
                                pdf_link = href if href.startswith('http') else "https://www.ppra.org.pk/" + href.lstrip('/')
                                break
                        
                        title = cols[0].text.strip().replace('\n', ' ') if len(cols) > 0 else "Tender Notice"
                        dept = cols[1].text.strip().replace('\n', ' ') if len(cols) > 1 else "Federal Dept"
                        date = cols[2].text.strip().replace('\n', ' ') if len(cols) > 2 else "As per ad"
                        
                        # Clean up title length
                        if len(title) > 120:
                            title = title[:120] + "..."
                            
                        tenders.append({
                            "title": title,
                            "department": dept,
                            "date": date,
                            "link": pdf_link,
                            "source": "PPRA (Official)"
                        })
    except Exception as e:
        print(f"Error fetching PPRA: {e}")
        
    return tenders

def generate_html(tenders):
    today_date = datetime.datetime.now().strftime("%d %B %Y - %I:%M %p")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Tenders Report - Pakistan</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; }}
        h1 {{ text-align: center; color: #2c3e50; font-size: 26px; margin-bottom: 5px; }}
        .date-header {{ text-align: center; color: #7f8c8d; margin-bottom: 25px; font-weight: bold; font-size: 14px; }}
        .table-container {{ overflow-x: auto; max-width: 1100px; margin: 0 auto; }}
        table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e9ecef; font-size: 14px; }}
        th {{ background-color: #34495e; color: white; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }}
        tr:hover {{ background-color: #f1f4f6; }}
        .source-ppra {{ background-color: #2980b9; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; display: inline-block; }}
        .btn {{ display: inline-block; padding: 6px 12px; background: #27ae60; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 12px; transition: 0.2s; }}
        .btn:hover {{ background: #2ecc71; }}
        .no-data {{ text-align: center; padding: 40px; color: #7f8c8d; font-size: 15px; }}
    </style>
</head>
<body>
    <h1>Pakistan Tenders (Office, Stationery, Printing)</h1>
    <div class="date-header">Last Updated: {today_date} PKT</div>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th style="width: 40%;">Tender Title</th>
                    <th style="width: 25%;">Department</th>
                    <th style="width: 15%;">Source</th>
                    <th style="width: 10%;">Closing Date</th>
                    <th style="width: 10%;">Action</th>
                </tr>
            </thead>
            <tbody>
"""
    
    if not tenders:
        html_content += """
                <tr>
                    <td colspan="5" class="no-data">
                        Aaj PPRA par printing, stationery, aur office supplies ke mutaliq koi naya tender upload nahi hua. System kal subah 8:00 AM dobara scan karega.
                    </td>
                </tr>
"""
    else:
        for t in tenders:
            html_content += f"""
                <tr>
                    <td style="font-weight: 500; color: #2c3e50;">{t['title']}</td>
                    <td style="color: #34495e;">{t['department']}</td>
                    <td><span class="source-ppra">{t['source']}</span></td>
                    <td style="color: #e67e22; font-weight: bold;">{t['date']}</td>
                    <td><a href="{t['link']}" class="btn" target="_blank">View PDF</a></td>
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
    print("index.html generated successfully!")

if __name__ == "__main__":
    ppra_data = fetch_ppra_tenders()
    generate_html(ppra_data)
