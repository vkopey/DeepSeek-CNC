# Для запуску программи введіть в консолі:
# streamlit run testStreamlit.py

example="""
G21       ; Встановлення метричних одиниць (міліметри)
G90       ; Абсолютна система координат
G0 X0 Y0 Z0  ; Швидке переміщення до початку координат (без малювання)
G1 X100 Y0 Z0 F1000 ; Переміщення на швидкості подачі
G1 X100 Y20 Z0
G1 X20 Y10 Z0
"""

from APIkey import key as api_key
from openai import OpenAI
import streamlit as st
import re

def is_gcode(text):
    """Повертає True, якщо усі рядки тексту є G-кодом. Тобто починаються з G або M, за якими іде цифра"""
    return all([bool(re.match(r"^G\d+|M\d+", ln.strip())) for ln in text.strip().splitlines()])

def get_gcode(text):
    """Повертає G-код без Markdown тексту```gcode...```"""
    mo=re.match("```gcode(.*)```", text, re.S)
    if mo==None: return
    return mo.group(1).strip()

def parse_gcode(text):
    """Виконує найпростіший парсинг G-коду. Код повинен бути в такому форматі: G1 X5 Y5 Z5. Повертає списки координат X,Y,Z"""
    X, Y, Z = [], [], [] # координати
    for line in text.splitlines():
        mo=re.match("G[0|1] X(?P<X>[0-9]*) Y(?P<Y>[0-9]*) Z(?P<Z>[0-9]*)", line, re.S) # пошук в рядку за регулярним виразом
        if mo==None: continue # якщо немає, то пропускаємо рядок
        XYZ=mo.groupdict() # словник зі знайденими групами
        #print(line, XYZ) # тільки для відлагодження
        x=int(XYZ['X']) # перетворити в число
        y=int(XYZ['Y'])
        z=int(XYZ['Z'])
        X.append(x) # додати до списку
        Y.append(y)
        Z.append(z)
    return X,Y,Z

def draw_path(X,Y,Z):
    """Рисує шлях інструмента за списками X,Y,Z з використанням plotly"""
    import plotly.graph_objects as go

    fig=go.Figure(data=[go.Scatter3d(x=X,y=Y,z=Z,mode='lines+markers',marker=dict(size=5),line=dict(width=2))]) # тривимірний графік з точками

    fig.update_layout(scene=dict(xaxis_title='X Axis', yaxis_title='Y Axis', zaxis_title='Z Axis'), title="3D Tool Path Visualization") # заголовок і назви осей

    return fig


def run_gcode(text):
    "Виконує програму для верстата, що підтримує GRBL"
    import serial
    import time
    s = serial.Serial('COM14', 115200) # назва і швидкість послідовного порта
    #s = serial.Serial('COM4', 9600)

    s.write("\r\n\r\n".encode("utf-8")) # пробудити GRBL
    time.sleep(2)   # чекати, поки GRBL ініціалізується
    s.flushInput()  # очистити текст в послідовному порті

    for line in text.splitlines(): # для кожного рядка G-коду
        l = line.strip() # видалиити усі символи EOL
        print('Sending: ' + l,)
        l+='\n' # додати символ кінця рядка
        s.write(l.encode("utf-8")) # відіслати G-код на GRBL
        grbl_out = s.readline().decode("utf-8") # чкати відповіді з поверенням каретки
        print(' : ' + grbl_out.strip())
    s.close() # закрити порт

st.title("💬DeepSeek CNC-Chatbot") # заголовок Streamlit програми
sys_output="Я можу створити будь-який G-код для верстата з ЧПК, що рисує маркером, на основі GRBL та пояснити його"
st.caption(sys_output) # вивести текст

user_input = st.text_area("Запитання:", value="Створи код для рисування лінії. Без коментарів і пояснень") # багаторядкове поле введення запитання користувача

if st.button("Надіслати"):
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    messages=[
        {"role": "system", "content": sys_output},
        {"role": "user", "content": user_input},
    ] # повідомлення системи і користувача
    response = client.chat.completions.create(model="deepseek-chat", messages=messages) # відповідь
    msg = response.choices[0].message.content # текст відповіді
    st.caption("Відповідь:")
    st.write(msg) # вивести відповідь

checkbox = st.checkbox("Виконання на GRBL") # якщо True, то код надсилається на верстат з GRBL

# натиснуто кнопку "Візуалізація"
if st.button("Візуалізація"):
    if is_gcode(user_input): # якщо користувач ввів G-код
        st.markdown("```gcode\n"+user_input+"\n```") # вивести його з підсвічуванням синтаксису
        X,Y,Z=parse_gcode(user_input) # виконати парсинг коду
        st.plotly_chart(draw_path(X,Y,Z)) # створити і показати графік в Streamlit
        #print(user_input)
        if checkbox: # якщо обрано "Виконання на GRBL"
            #print(user_input)
            run_gcode(user_input) # виконати на GRBL