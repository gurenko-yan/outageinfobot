from bs4 import BeautifulSoup
import requests

page = requests.get('http://93.92.65.26/aspx/GorodM.htm')
page.encoding = 'windows-1251'
soup = BeautifulSoup(page.text, 'html.parser')


class api:
    def __init__(self):
        self.root = self.get_tag(['div', 'table'])

    def find_data(self, district, street):
        tr = self.root.find('tr') # поиск первого тега <tr>

        while tr['height'] != '0': # поиск <tr> height != 0
            if tr['height'] == '20': # <tr> height = 20
                td = tr.find_all('td')[1]
                text = self.correct(td.get_text())

                if text == self.correct(district):
                    tr = tr.find_next('tr') # след. <tr> с которого начинается поиск улицы
                    break

            tr = tr.find_next('tr')

        while not(tr['height'] in ['20', '0']): # поиск <tr> height != 20 != 0
            td = tr.find_all('td')[1] # <td> с улицами
            is_correct = self.check_street(td.get_text(), street)
            if is_correct:
                data = tr.find_all('td')
                data_text = []
                for i in data:
                    data_text.append(i.get_text())
                return data_text

            tr = tr.find_next('tr')
    
    def get_tag(self, hierarchy): # получение тега в иерархии
        current_tag = soup.body

        for tag in hierarchy:
            current_tag = current_tag.find(tag)

        return current_tag
    
    def correct(self, text): # преобразование текста в строку без не буквенных символов
        result_text = ''

        for let in text:
            if let.isalpha():
                result_text += let

        return result_text
    
    def check_street(self, text, street):
        text = text.split(';')
        for string in text:
            if string in ['плановое', 'аварийное']:
                return False
            elif street in string:
                return True
        
    def structuring(self, data):
        structured_data = []
        for d in data:
            string = ''
            for let in d:
                if let == '\\':
                    if len(string):
                        structured_data += [string]
                        string = ''
                        
                string += let


test = api()
print(test.find_data('Октябрьский район', '2-я Мелькомбинатская'))