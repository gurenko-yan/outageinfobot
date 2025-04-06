from bs4 import BeautifulSoup
import requests

page = requests.get('http://93.92.65.26/aspx/GorodM.htm')
page.encoding = 'windows-1251'
soup = BeautifulSoup(page.text, 'html.parser')


class api:
    def __init__(self):
        self.root = self.get_tag(['div', 'table'])

    def find_data(self, district, street, number):
        tr = self.root.find('tr') # поиск первого тега <tr>

        while tr['height'] != '0': # поиск <tr> height != 0
            if tr['height'] == '20': # <tr> height = 20
                td = tr.find_all('td')[1]
                text = self.correct(td.get_text())

                if text == district:
                    tr = tr.find_next('tr') # след. <tr> с которого начинается поиск улицы
                    break

            tr = tr.find_next('tr')

        while not(tr['height'] in ['20', '0']): # поиск <tr> height != 20 != 0
            td = tr.find_all('td')[1] # <td> с улицами
            k = self.check_street(td.get_text(), street, number)
            if k:
                return tr

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
    
    def check_street(self, text, street, number):
        text = text.split(';')
        for string in text:
            if string in ['плановое', 'аварийное']:
                return False
            elif street in string:
                return True


test = api()
print(test.find_data('Октябрьскийрайон', 'СНТ Землеустроитель', '432784368'))