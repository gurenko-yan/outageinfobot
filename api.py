from bs4 import BeautifulSoup
import requests
import streets_base

class api:
    def __init__(self):
        self.page = requests.get('http://93.92.65.26/aspx/GorodM.htm')
        self.page.encoding = 'windows-1251'
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        self.root = self.get_tag(['div', 'table'])
        self.streets = streets_base.streets
    
    def find_data(self, district, street):
        tr = self.root.find('tr') # поиск первого тега <tr>

        try:
            tr['height']
        except:
            with open('cache.txt', 'r', encoding='utf-8') as cache: # кэширование html для обработки ошибок
                text = cache.read()
            
            if not(text):
                return -1

            self.soup = BeautifulSoup(text, 'html.parser')
            self.root = self.get_tag(['div', 'table'])
            
            tr = self.root.find('tr')
        else:
            with open('cache.txt', 'w', encoding='utf-8') as cache:
                cache.write(self.page.text)
        
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
    
    def simplify(self, data, flag):
        s = ''
        is_excessive_space = False
        divide_trigger = ['\n', ',']

        for let in data:
            if not let in ['\r', '\n', ',']:
                if let == ' ' and not is_excessive_space:
                    s += let
                    is_excessive_space = True
                elif not let in [' ', '\xa0']:
                    if let == ';':
                        s += '|'
                    s += let
                    is_excessive_space = False
            elif let == divide_trigger[flag]:
                s += '; '
                is_excessive_space = True

        return s

    def structuring(self, data):
        structured_data = {}
        col1 = self.simplify(data[0], 0).split('; ')
        col2 = self.simplify(data[1], 1).split(';')
        col3 = self.simplify(data[2], 0).split('; ')

        if 'отмена' in col3:
            return None
        
        s = ''
        for i in col1:
            if 'ООО' in i or 'ПАО' in i or 'АО' in i:
                structured_data.update({'resource': s})
                s = ''
            elif 'т.' in i:
                structured_data.update({'company': s})
                structured_data.update({'phone': i[3:]})
            elif len(s):
                s += ' '
            s += i
        
        s = ''
        flag = False
        street = []
        streets = []
        new_street = True
        for i in col2:
            if 'аварийное' in i or 'плановое' in i:
                flag = True
            
            if flag:
                s += i
            elif new_street:
                new_street = False
                char_counter = 0
                divide_point = len(i) + 1

                for j in range(len(i)):
                    if not(i[j].isdigit() or i[j] in ['-', '/', '|']):
                        if char_counter > 1:
                            divide_point = len(i) + 1
                        char_counter += 1
                    else:
                        char_counter = 0
                        if divide_point == len(i) + 1:
                            divide_point = j

                begin = 0
                if i[divide_point - 1] == ' ':
                    if i[0] == ' ': begin += 1
                    street.append(i[begin:(divide_point - 1)])
                else:
                    if i[0] == ' ': begin += 1
                    street.append(i[begin:divide_point])

                if i[divide_point:] != '':
                    if i[-1] == '|':
                        street.append(i[divide_point:-1])
                        streets.append(street)
                        street = []
                        new_street = True
                    else:
                        street.append(i[divide_point:])
            elif i[-1] == '|':
                begin = 0
                if i[0] == ' ': begin += 1
                street.append(i[begin:-1])
                streets.append(street)
                street = []
                new_street = True
            else:
                street.append(i)

        structured_data.update({'streets': streets})
        structured_data.update({'info': s})

        s = ''
        flag = False
        for i in col3:
            s += i
            if not flag:
                end = i.rfind('-')
                if end != -1:
                    flag = True
                    structured_data.update({'start': s})
                    s = ''
            if len(s):
                s += ' '

        structured_data.update({'finish': s})

        return structured_data

# демонстрация
test = api()
data = test.find_data('Железнодорожный район', 'Красной Армии')
print(data['resource'])
print(data['company'])
print(data['phone'])
for i in data['streets']:
    print(i)
print(data['info'])
print(data['start'])
print(data['finish'])