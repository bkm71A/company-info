from lxml import html
import requests
import sqlite3
from sqlite3 import Error

symbol_list = ["CAT", "MRK", "DIS", "JPM", "WMT", "UTX", "CSCO", "IBM", "MCD", "HD", "MMM", "KO", "XOM", "MSFT", "PFE", "GS", "V", "TRV", "INTC", "NKE", "AAPL", "PG", "CVX", "BA", "JNJ", "VZ", "GE", "UNH", "AXP", "DD-PA", "DD-PB", "DWDP.BA"]
yahoo_base_url = 'https://finance.yahoo.com/quote/'
yahoo_financials = '/financials?p='
yahoo_profile = '/profile?p='
create_table_sql = """CREATE TABLE IF NOT EXISTS company (
                      symbol text PRIMARY KEY,
                      name text,
                      url text,
                      industry text,
                      employees text,
                      phone text,
                      address text,
                      address_country text,
                      address_city text,
                      address_zip text,
                      address_state text,
                      revenue text
                    );"""
update_table_sql = """INSERT OR REPLACE INTO company(symbol,name,url,industry,employees,phone,address,address_country,address_city,address_zip,address_state,revenue)
                      values (?,?,?,?,?,?,?,?,?,?,?,?);"""

def parse_address( city_zip_state ):
  city = ''
  state = ''
  zip = ''
  if city_zip_state:
    parts = city_zip_state.split(',')
    if(len(parts)==2):
      city = parts[0].strip()
      state_zip = parts[1].strip().split()
      if(len(state_zip)==2):
       state = state_zip[0].strip()
       zip = state_zip[1].strip()
  return [city,zip,state]

def create_connection(db_file):
  try:
    return sqlite3.connect(db_file)
  except Error as e:
    print(e)
  return None

conn = create_connection("company-info.db")
with conn:
  try:
    cursor = conn.cursor()
    cursor.execute(create_table_sql)

    for symbol in symbol_list:
        tree = html.fromstring(requests.get(yahoo_base_url + symbol + yahoo_profile + symbol).content)
        
        company_name = tree.xpath('//h3[@class="Mb(10px)"]/text()')
        company_name = company_name[0] if len(company_name)>0 else ""
        
        address_lines = tree.xpath('//p[@class="D(ib) W(47.727%) Pend(40px)"]/text()')
        address_part_1 = (address_lines[0]+','+address_lines[1] if len(address_lines)>3 else address_lines[0]) if len(address_lines)>0 else ""
        address_city_zip_state = parse_address(address_lines[len(address_lines)-2] if len(address_lines)>1 else "")
        address_country = address_lines[len(address_lines)-1] if len(address_lines)>2 else ""
    
        company_phone = tree.xpath('//a[@data-reactid="15"]/text()')
        company_phone = company_phone[0] if len(company_phone)>0 else ""
        
        company_industry = tree.xpath('//strong[@data-reactid="25"]/text()')
        company_industry = company_industry[0] if len(company_industry)>0 else ""
        
        number_of_employees = tree.xpath('//span[@data-reactid="30"]/text()')
        number_of_employees = number_of_employees[0] if len(number_of_employees)>0 else ""
        
        company_url = tree.xpath('//a[@data-reactid="17"]/text()')
        company_url = company_url[0] if len(company_url)>1 else ""
        
        estimated_annual_revenue_thousands = html.fromstring(requests.get(yahoo_base_url + symbol + yahoo_financials + symbol).content).xpath('//section[@data-test="qsp-financial"]/div/table/tbody/tr[2]/td[2]/span/text()')
        estimated_annual_revenue_thousands = estimated_annual_revenue_thousands[0].replace(',','') if len(estimated_annual_revenue_thousands)>0 else ""
        
        print('{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(symbol,company_name,company_url,company_industry,number_of_employees,company_phone,address_part_1,address_country,address_city_zip_state[0],' ' + address_city_zip_state[1],address_city_zip_state[2],estimated_annual_revenue_thousands))

        cursor.execute(update_table_sql,(symbol,company_name,company_url,company_industry,number_of_employees,company_phone,address_part_1,address_country,address_city_zip_state[0],address_city_zip_state[1],address_city_zip_state[2],estimated_annual_revenue_thousands))

    conn.commit()
  except Error as e:
    print(e)
 
conn.close()

    