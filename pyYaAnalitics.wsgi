import sys, os
import urllib.parse 

imp1 = os.path.dirname(os.path.abspath(__file__)) + '/site-packages'
imp2 = os.path.dirname(os.path.abspath(__file__)) + '/scripts/YaAnaliticsBudget'

if imp1 not in sys.path:
    sys.path.append(imp1)
    
if imp2 not in sys.path:
    sys.path.append(imp2)

import MAIN_program
from jinja2 import Environment, FileSystemLoader

def application(environ, start_response):
    #полуачаем список POST переменных
    post_input = urllib.parse.parse_qs(environ['wsgi.input'].readline().decode(),True)
    #подключаем директорию с шаблонами
    templ_dir = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)) + '/scripts/YaAnaliticsBudget'))
    #выбираем нужный нам шаблон
    template = templ_dir.get_template('index.html')
    status = '200 OK' 

    if 't_id' in post_input:
        t_id = str(post_input['t_id'][0]).encode('utf-8')
        response_program = MAIN_program.main(t_id)  
        response_body = template.render(content=response_program).encode()  
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]
    else:
        response_program = u'<p><b>ERROR: </b>Скрипт не получил POST параметер t_id (идентификатор таблицы)</p>' 
        response_body = template.render(content=response_program).encode() 
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]

