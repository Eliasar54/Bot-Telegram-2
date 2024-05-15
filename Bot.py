import logging
from datetime import datetime
import telepot
import os
import requests
import subprocess
import time
from pytube import YouTube
from PIL import Image
from io import BytesIO
import random
import string

# Configuración del bot
TOKEN = input("Por favor, introduce el token de acceso del bot: ")  
bot = telepot.Bot(TOKEN)

# Diccionario para almacenar los datos de registro de cada usuario
usuarios = {}

# Función para generar un código único de 23 dígitos
def generar_codigo():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=23))

# Función para enviar mensajes con animación de carga
def enviar_mensaje_con_animacion(chat_id, text):
    message = bot.sendMessage(chat_id, text)
    # Animación de carga
    animation = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    for frame in animation:
        time.sleep(0.5)
        bot.editMessageText((chat_id, message['message_id']), f'{text} {frame}')

# Función para manejar el registro de usuarios
def registrar(chat_id, user_id, username):
    codigo = generar_codigo()
    if user_id not in usuarios:
        usuarios[user_id] = {'username': username, 'codigo': codigo, 'edad': None, 'usos_w': 0}
        bot.sendMessage(chat_id, f'¡Hola {username}! Bienvenido al bot. Tu código de registro es: {codigo}.')
    else:
        bot.sendMessage(chat_id, '¡Ya estás registrado!')

# Función para eliminar el registro de un usuario
def desregistrar(chat_id, user_id):
    if user_id in usuarios:
        del usuarios[user_id]
        bot.sendMessage(chat_id, 'Se ha eliminado tu registro correctamente.')
    else:
        bot.sendMessage(chat_id, '¡No estás registrado!')

# Función para saludar al usuario
def saludar(chat_id, username):
    bot.sendMessage(chat_id, f'Hola {username}! Qué gusto verte.')

# Función para obtener la edad del usuario
def obtener_edad(chat_id, user_id):
    if user_id in usuarios and usuarios[user_id]['edad'] is not None:
        bot.sendMessage(chat_id, f'Tu edad registrada es: {usuarios[user_id]["edad"]}')
    else:
        bot.sendMessage(chat_id, 'Aún no has registrado tu edad.')

# Función para actualizar la edad del usuario
def actualizar_edad(chat_id, user_id, edad):
    if user_id in usuarios:
        usuarios[user_id]['edad'] = edad
        bot.sendMessage(chat_id, 'Tu edad ha sido actualizada correctamente.')
    else:
        bot.sendMessage(chat_id, '¡No estás registrado!')

# Función para ganar diamantes
def ganar_diamantes(chat_id, user_id):
    enviar_mensaje_con_animacion(chat_id, 'Ganando diamantes...')
    if user_id in usuarios:
        if usuarios[user_id]['usos_w'] < 6:
            usuarios[user_id]['usos_w'] += 1
            bot.sendMessage(chat_id, '¡Has ganado 5 diamantes! Ahora tienes {} diamantes.'.format(usuarios[user_id]['usos_w'] * 5))
        else:
            bot.sendMessage(chat_id, '¡Has alcanzado el límite de usos para este comando!')
    else:
        bot.sendMessage(chat_id, 'Debes registrarte primero para ganar diamantes.')

# Función para buscar imágenes en Google Images
def buscar_imagen(chat_id, user_id, text):
    enviar_mensaje_con_animacion(chat_id, 'Buscando imágenes...')
    if user_id in usuarios and usuarios[user_id]['usos_w'] < 6:
        usuarios[user_id]['usos_w'] += 1
        search_query = '+'.join(text.split()[1:])
        response = requests.get(f'https://www.google.com/search?q={search_query}&tbm=isch')
        try:
            images = response.json().get('items', [])
            if images:
                image_url = images[0]['link']
                bot.sendPhoto(chat_id, image_url)
            else:
                bot.sendMessage(chat_id, 'No se encontraron imágenes para tu búsqueda.')
        except ValueError:
            bot.sendMessage(chat_id, 'No se pudo obtener la respuesta de Google Images.')
    else:
        bot.sendMessage(chat_id, '¡No tienes suficientes diamantes para este comando o has alcanzado el límite de usos!')

# Función para descargar videos de YouTube
def descargar_video(chat_id, user_id, text):
    enviar_mensaje_con_animacion(chat_id, 'Descargando video...')
    if user_id in usuarios and usuarios[user_id]['usos_w'] < 6:
        usuarios[user_id]['usos_w'] += 1
        video_name = '+'.join(text.split()[1:])
        try:
            yt = YouTube(f"ytsearch:{video_name}")
            stream = yt.streams.get_highest_resolution()
            stream.download()
            bot.sendVideo(chat_id, open(f"{yt.title}.mp4", 'rb'))
            bot.sendMessage(chat_id, f'Se ha descargado el video "{video_name}".')
            bot.sendMessage(chat_id, f'Ahora tienes {usuarios[user_id]["usos_w"] * 5} diamantes.')
        except Exception as e:
            bot.sendMessage(chat_id, f'Hubo un error al descargar el video: {str(e)}')
    else:
        bot.sendMessage(chat_id, '¡No tienes suficientes diamantes para este comando o has alcanzado el límite de usos!')

# Función para mostrar el menú de comandos
def mostrar_menu(chat_id):
    menu_text = '''---------------------
MENU-BOT🤖
--------------------
|° /play2 descargar videos 
|° /imagen buscar imágenes 
|° /w ganar diamantes 
|° /reg registrar en el bot
|° /unreg eliminar registro
|° /edad obtener o actualizar edad
----------------------------'''
    bot.sendMessage(chat_id, menu_text)

# Manejador de mensajes
def handle_messages(msg):
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    username = msg['from']['username'] if 'username' in msg['from'] else 'usuario'
    text = msg['text']
    
    # Mostrar mensaje en la terminal
    print(f'Mensaje recibido de {username}: {text}')
    
    if text.startswith('/reg'):
        registrar(chat_id, user_id, username)
    elif text.startswith('/unreg'):
        desregistrar(chat_id, user_id)
    elif user_id not in usuarios:
        bot.sendMessage(chat_id, 'Debes registrarte primero para usar otros comandos. Usa /reg para registrarte.')
    elif text.startswith('/edad'):
        if len(text.split()) == 1:
            obtener_edad(chat_id, user_id)
        elif len(text.split()) == 2:
            edad = text.split()[1]
            if edad.isdigit():
                actualizar_edad(chat_id, user_id, edad)
            else:
                bot.sendMessage(chat_id, 'La edad debe ser un número.')
        else:
            bot.sendMessage(chat_id, 'Comando /edad no válido. Utiliza /edad para obtener tu edad o /edad <numero> para actualizarla.')
    elif text.startswith('/w'):
        ganar_diamantes(chat_id, user_id)
    elif text.startswith('/imagen'):
        buscar_imagen(chat_id, user_id, text)
    elif text.startswith('/play2'):
        descargar_video(chat_id, user_id, text)
    elif text.startswith('/menu'):
        mostrar_menu(chat_id)
    else:
        bot.sendMessage(chat_id, 'Comando no válido. Utiliza /menu para ver la lista de comandos disponibles.')

# Manejador de mensajes
bot.message_loop(handle_messages)

print('Escuchando ...')

# Mantener el programa en ejecución
while True:
    pass
