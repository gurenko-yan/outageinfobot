from bs4 import BeautifulSoup
import requests

class api:
    def __init__(self):
        self.page = requests.get('http://93.92.65.26/aspx/GorodM.htm')
        self.page.encoding = 'windows-1251'
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        self.root = self.get_tag(['div', 'table'])
    
    def find_data(self, district, street):
        tr = self.root.find('tr') # поиск первого тега <tr>

        try:
            tr['height']
        except:
            cache = open('cache.txt', 'r', encoding='utf-8')
            text = cache.read()
            cache.close()
            
            if not(text):
                return -1

            self.soup = BeautifulSoup(text, 'html.parser')
            self.root = self.get_tag(['div', 'table'])
            
            tr = self.root.find('tr')
        else:
            cache = open('cache.txt', 'w', encoding='utf-8')
            cache.write(self.page.text)
            cache.close()

        
        while tr['height'] != '0': # поиск строки с названием района
            if tr['height'] == '20':
                td = tr.find_all('td')[1]
                text = self.only_alpha(td.get_text())

                if text == self.only_alpha(district):
                    tr = tr.find_next('tr') # след. <tr> с которого начинается поиск улицы
                    break

            tr = tr.find_next('tr')

        while not(tr['height'] in ['20', '0']): # поиск <tr> height != 20 != 0
            td = tr.find_all('td')
            is_correct = self.check_street(td[1].get_text(), street)
            if is_correct:
                data = []

                for i in td:
                    data.append(i.get_text())

                return self.structuring(data)

            tr = tr.find_next('tr')
    
    def get_tag(self, hierarchy): # получение тега в иерархии
        current_tag = self.soup.body

        for tag in hierarchy:
            current_tag = current_tag.find(tag)

        return current_tag
    
    def only_alpha(self, text): # преобразование текста в строку без не буквенных символов
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
    
    def correct_data(self, data, flag):
        structured_data = []
        s = ''
        is_excessive_space = False

        for let in data:
            if not let in ['\n', '\r', '\xa0']:
                if let == ' ':
                    if not is_excessive_space:
                        s += let
                        is_excessive_space = True
                else:
                    s += let
                    is_excessive_space = False
            elif not s in ['', ' '] and flag:
                structured_data.append(s)
                s = ''
        
        if not s in ['', ' ']:
            structured_data.append(s)

        return structured_data

    def structuring(self, data):
        structured_data = []
        structured_data += self.correct_data(data[0], 1)
        structured_data += self.correct_data(data[1], 0)
        structured_data += self.correct_data(data[2], 1)

        return structured_data


test = api()
data = test.find_data('Советский район', 'Авангардная')
print(data)