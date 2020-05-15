import random as rd
from vk_api.bot_longpoll import VkBotEventType

from core.keyboards import KEYBOARDS
from core import server

from data.db_session import create_session


def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


def main():
    #  Заполнение таблиц-констант
    session = create_session()
    server.init_items(session)
    server.init_enemies(session)
    session.close()

    print('running...')

    for event in server.longpoll.listen():
        event_do(event, server.vk)


def event_do(event, vk):
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message['from_id']
        text = event.message['text'].lower().split()

        session = create_session()
        user = server.getOwnUser(user_id, session)

        if user:
            keyboard = server.checkKeyboard(user)

            if text[0] in KEYBOARDS[keyboard].commands.keys():
                if text[0] in KEYBOARDS[keyboard].commands.keys():
                    msg = KEYBOARDS[keyboard].commands[text[0]](user, session, text)
                    btn = server.checkKeyboard(user)
                    # print('MSG:', msg)
                    send_message(user_id, vk, msg, btn)

        else:
            send_message(user_id, vk, server.f_start(user_id, session, None), 2)

        session.commit()
        session.close()


def send_message(user, vk, message, keyboard_type=0):
    keyboard = KEYBOARDS[keyboard_type].get_board()
    if not message:
        message = '...'
    vk.messages.send(user_id=user, message=message, random_id=rd.randint(0, 2 ** 32), keyboard=keyboard)


if __name__ == '__main__':
    main()
