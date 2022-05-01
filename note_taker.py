from random import randint, random
from secrets import randbits
import vk
import json
import datetime
import pytz
from bot_handmade import *
from db import connect, User, Note

CHAT_START_ID = int(2E9)
NOTE_CASES = ['заметок', 'заметка', 'заметки']

def case_number(n, cases):
    n = n % 10
    if n == 0 or n >= 5:
        return cases[0]
    if n == 1:
        return cases[1]
    return cases[2]

def vkrandom():
    # 31 random bits + sign
    return randbits(31) * (1 if random() < 0.5 else -1)

# open options.json
with open('options.json', 'r') as f:
    options = json.load(f)

TOKEN = options['TOKEN']
GROUP_ID = options['GROUP_ID']
DB_NAME = options['DB_NAME']
DB_HOST = options['DB_HOST']
DB_PORT = options['DB_PORT']
PREFIX = options['PREFIX']
MAX_NOTES = options['MAX_NOTES']

connect(DB_NAME, DB_HOST, DB_PORT)

session = vk.Session(access_token=options['TOKEN'])
api = vk.API(session, v='5.131')

lp = Longpoll(session, api, group_id=options['GROUP_ID'])

def get_user(user_id):
    user = User.objects(user_id=user_id).first()
    if not user:
        name = api.users.get(user_id=user_id)[0]['first_name']
        user = User(
            user_id=user_id,
            name=name,
        )
        user.save()
    return user

def list_notes(message):
    user = get_user(message['from_id'])
    notes = user.notes
    if not notes:
        reply_to_chat(message, '📝 У вас нет заметок')
        return
    
    notes_text = ''
    number = 1
    for note in notes:
        notes_text += f'{number}. {note.text}\n'
        number += 1
    reply_to_chat(message, f'📝 У вас {len(notes)} {case_number(len(notes), NOTE_CASES)}\n' + notes_text)

def new_note(message, text):
    user = get_user(message['from_id'])
    if len(user.notes) >= MAX_NOTES:
        reply_to_chat(message, '⚠ У вас максимальное количество заметок')
        return
    note = Note(text=text)
    note.save()
    user.notes.append(note)
    user.save()
    reply_to_chat(message, '📝 Заметка сохранена: ' + text)

def delete_note(message, num):
    user = get_user(message['from_id'])
    notes = user.notes
    if not notes:
        reply_to_chat(message, 'ℹ У вас нет заметок')
        return
    if num > len(notes) or num < 1:
        reply_to_chat(message, '⚠ Нет такой заметки')
        return
    note = notes[num - 1]
    user.notes.remove(note)
    user.save()
    note.delete()
    reply_to_chat(message, 'ℹ Заметка удалена')

def delete_all_notes(message):
    user = get_user(message['from_id'])
    notes = user.notes
    if not notes:
        reply_to_chat(message, 'ℹ У вас нет заметок')
        return
    for note in notes:
        note.delete()
    user.notes = []
    user.save()
    reply_to_chat(message, 'ℹ Все заметки удалены')

def edit_note(message, num, new_text):
    user = get_user(message['from_id'])
    notes = user.notes
    if not notes:
        reply_to_chat(message, 'ℹ У вас нет заметок')
        return
    if num > len(notes) or num < 1:
        reply_to_chat(message, '⚠ Нет такой заметки')
        return
    note = notes[num - 1]
    note.text = new_text
    note.save()
    reply_to_chat(message, 'ℹ Заметка изменена')

commands = [
    ('заметки', 'показать все заметки'),
    ('заметка <текст>...', 'создать новую заметку'),
    ('удалить <целое>', 'удалить заметку'),
    ('удалить все', 'удалить все заметки'),
    ('изменить <целое> <текст>...', 'изменить заметку'),
    ('помощь', 'показать это сообщение'),
]
def gen_help():
    return ('ℹ Помощь по боту:\n' +
        '\n'.join(f'{PREFIX}{command[0]} - {command[1]}' for command in commands) +
        f'\n\nМаксимальное количество заметок - {MAX_NOTES}'
    )

def reply_to_chat(message, text):
    api.messages.send(peer_id=message['peer_id'],
        message=text,
        random_id=vkrandom())

def process_new(message):
    if len(message['text']) == 0: return
    words: list[str] = message['text'].lower().split()
    if not words[0].startswith(PREFIX): return
    words[0] = words[0][1:]

    match words:
        case ['заметки' | 'список' | 'list']:
            list_notes(message)
        case ['заметка' | 'note', *rest] if len(rest) > 0:
            text = ' '.join(rest)
            new_note(message, text)
        case ['удали' | 'удалить' | 'del' | 'delete', 'все' | 'всё' | 'all']:
            delete_all_notes(message)
        case ['удали' | 'удалить' | 'del' | 'delete', num]:
            try:
                delete_note(message, int(num))
            except ValueError:
                reply_to_chat(message, '⚠ Вы ввели не целое число')
        case ['исправь' | 'измени' | 'edit', num, *rest]:
            if len(rest) == 0:
                reply_to_chat(message, '⚠ Укажите текст, на который надо изменить заметку')
            else:
                try:
                    edit_note(message, int(num), ' '.join(rest))
                except ValueError:
                    reply_to_chat(message, f'⚠ Вы ввели не целое число')
        case ['помощь' | 'help']:
            reply_to_chat(message, gen_help())

def main():
    print(f'Начал работать в группе {options["GROUP_ID"]}, ts = {lp.ts}')
    while True:
        for update in lp.get():
            # print(f'Тип {update.type}:', update.object)
            if update.type == MESSAGE_NEW:
                process_new(update.object['message']) # update.object['client_info']

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Пока, мир!')