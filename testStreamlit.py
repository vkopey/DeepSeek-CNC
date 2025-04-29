# streamlit run testStreamlit.py

from APIkey import key as api_key
from openai import OpenAI
import streamlit as st
import re

def get_gcode(text):
    mo=re.match("```gcode(.*)```", text, re.S)
    if mo==None: return
    return mo.group(1).strip()

def run_gcode(text):
    "Виконує програму для верстата"
    import serial
    import time
    s = serial.Serial('COM14',115200)
    #s = serial.Serial('COM4',9600)
    # Wake up grbl
    s.write("\r\n\r\n".encode("utf-8"))
    time.sleep(2)   # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    # Stream g-code to grbl
    for line in text.splitlines():
        l = line.strip() # Strip all EOL characters for consistency
        print('Sending: ' + l,)
        l+='\n'
        s.write(l.encode("utf-8")) # Send g-code block to grbl
        grbl_out = s.readline().decode("utf-8") # Wait for grbl response with carriage return
        print(' : ' + grbl_out.strip())
    s.close()

st.title("💬DeepSeek Chatbot")
st.caption("CNC-чатбот")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Я можу створити будь-який G-код для лазерного верстата з ЧПК на основі GRBL та пояснити його"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    #if not api_key:
    #    st.info("Please add your API key to continue.")
    #    st.stop()

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    st.session_state.messages.append({"role": "user", "content": prompt})
    #Створи код для рисування лінії. Без коментарів і пояснень.
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="deepseek-chat", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    print(msg)
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)


#checkbox = st.checkbox("Check me!")
if st.button("Виконати G-код!"):
    st.write(msg["content"])
    code=get_gcode(msg["content"])
    print(code)
    #run_gcode(code)
    #if checkbox:
        #st.write("Checkbox is checked!")

