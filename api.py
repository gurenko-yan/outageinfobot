from bs4 import BeautifulSoup
import requests

page = requests.get('http://93.92.65.26/aspx/GorodM.htm')
page.encoding = 'windows-1251'
soup = BeautifulSoup(page.text, 'html.parser')


class api:
    def __init__(self, district, street):
        self.data = []
        root = self.get_tag(['div', 'table'])
        tr = root.find('tr')

        while tr['height'] != '0':
            if tr['height'] == '20':
                td = tr.find_all('td')[1]
                print(td.get_text())
            
            tr = tr.find_next('tr')
    
    def get_tag(self, hierarchy):
        current_tag = soup.body

        for tag in hierarchy:
            current_tag = current_tag.find(tag)

        return current_tag

test = api('Октябрьский район', 'Сады 12')