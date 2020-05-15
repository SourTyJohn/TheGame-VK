import vk_api
import vk_api.keyboard
from core import server as sv

B_COLORS = [
    vk_api.keyboard.VkKeyboardColor.DEFAULT,
    vk_api.keyboard.VkKeyboardColor.PRIMARY,
    vk_api.keyboard.VkKeyboardColor.POSITIVE,
    vk_api.keyboard.VkKeyboardColor.NEGATIVE
]

BUTTON_MENU = ['Меню', 2, 1]
BUTTON_HELP = ['Справка', 0, 1]
BUTTON_BACK = ['Назад', 2, 1]


def create_keyboard(buttons: list, one_time=False, inline=False):
    # Buttons = [[text, color, new_line], [...], ]
    keyboard = vk_api.keyboard.VkKeyboard(one_time=one_time, inline=inline)

    for i, button in enumerate(buttons):
        if button[2]:
            keyboard.add_line()
        keyboard.add_button(button[0], color=B_COLORS[button[1]])

    return keyboard.get_keyboard()


class Keyboard:
    board = create_keyboard([])
    commands = {}
    text = '?KeyboardText?'
    back_command = None

    @classmethod
    def get_board(cls, *args):
        return cls.board


class k_MainMenu(Keyboard):
    """Главное меню"""
    board = create_keyboard([['Подземелье', 1, False],
                             ['Инвентарь', 0, True], ['Персонажи', 0, False],
                             ['Торговая_площадка', 1, True],
                             ['Арена', 3, True]])
    commands = {'подземелье': sv.f_prepare, 'инвентарь': sv.f_inventory_main,
                'торговая_площадка': sv.f_marketplace, 'персонажи': sv.f_characters_main}


class k_YesNoClose(Keyboard):
    board = create_keyboard([['Да', 2, False], ['Нет', 3, False],
                             ['Закрыть', 0, True]])
    commands = {}

    @classmethod
    def is_command_exists(cls, command):
        return command in cls.commands.keys()


class k_PreDungeon(Keyboard):
    """Меню выбора героев для похода"""
    board = create_keyboard([['. 1', 1, 0], ['. 2', 1, 0], ['. 3', 1, 0],
                             ['Отправиться', 2, 1], ['Отменить', 3, 0]])
    commands = {'отменить': sv.f_goto_menu, '.': sv.f_chose_pos, 'отправиться': sv.f_goto_dungeon}


class k_Inventory(Keyboard):
    board = create_keyboard([['Обновить', 1, 0],
                             BUTTON_HELP,
                             BUTTON_MENU])
    commands = {'обновить': sv.f_inventory_main, 'меню': sv.f_goto_menu,
                'о': sv.f_show_item_good, 'и': sv.f_use_from_inv,
                'п': sv.f_sell, 'к': sv.f_buy,
                'справка': sv.f_inventory_help}


class k_Marketplace(Keyboard):
    board = create_keyboard([['<--', 1, 0], ['Обновить', 1, 0], ['-->', 1, 0],
                             ['Мои_лоты', 1, 1],
                             BUTTON_HELP,
                             BUTTON_MENU])

    commands = {'обновить': sv.f_marketplace, 'меню': sv.f_goto_menu,
                '<--': sv.f_prev_page, '-->': sv.f_next_page,
                'п': sv.f_sell, 'к': sv.f_buy,
                'справка': sv.f_market_help,
                'н': sv.f_find_in_market, 'мои_лоты': sv.f_show_my_lots}


class k_MarketplaceSearch(k_Marketplace):
    board = create_keyboard([['<--', 1, 0], ['Обновить', 1, 0], ['-->', 1, 0],
                             ['Отменить_поиск', 1, 1],
                             BUTTON_HELP,
                             BUTTON_MENU])

    commands = k_Marketplace.commands.copy()
    del commands['мои_лоты']
    commands['отменить_поиск'] = sv


class k_MyLots(Keyboard):
    board = create_keyboard([['Обновить', 1, 0],
                             BUTTON_HELP,
                             BUTTON_BACK])
    commands = {'назад': sv.f_marketplace, 'справка': sv.f_my_lots_help, 'у': sv.f_delete_lot,
                'обновить': sv.f_show_my_lots}


class k_CharacterMenu(Keyboard):
    board = create_keyboard([['. 1', 1, 0], ['. 2', 1, 0], ['. 3', 1, 0],
                             ['. 4', 1, 1], ['. 5', 1, 0], ['. 6', 1, 0],
                             BUTTON_MENU])
    commands = {'.': sv.f_character, 'меню': sv.f_goto_menu}


class k_WeaponSelect(Keyboard):
    board = create_keyboard([['Готово', 2, 0], ])
    commands = {'готово': sv.f_prepare, 'в': sv.f_dungeon_chose}


class k_PreDungeonCharactersSelect(k_CharacterMenu):
    commands = {'.': sv.f_dungeon_character, 'меню': sv.f_goto_menu}


class k_Character(Keyboard):
    board = create_keyboard([['Улучшить', 1, 0],
                             ['Справка', 1, 0],
                             BUTTON_BACK])
    commands = {'улучшить': sv.f_character_upgrade_main, 'назад': sv.f_characters_main,
                'справка': sv.f_character_help, 'выгнать': sv.f_character_delete}


class k_UpgradeCharacter(Keyboard):
    board = create_keyboard([['+ str', 1, 0], ['+ dex', 1, 0], ['+ rea', 1, 1], ['+ stm', 1, 0],
                             ['+ agl', 1, 1], ['+ int', 1, 0], ['+ lck', 1, 1], ['+ att', 1, 0],
                             BUTTON_BACK])
    commands = {'назад': sv.f_characters_main, '+': sv.f_character_upgrade}


class k_BattleMain(Keyboard):
    board = create_keyboard([['Атаковать', 3, 0], ['Предмет', 2, 1], ['Пропустить ход', 0, 1]])
    commands = {'атаковать': sv.f_chose_attacks_menu, 'пропустить': sv.f_skip_turn}


class k_Skill_Select(Keyboard):
    board = create_keyboard([['. 1', 1, 0], ['. 2', 1, 0], ['. 3', 1, 0],
                             ['. 4', 1, 1], ['. 5', 1, 0], ['. 6', 1, 0],
                             BUTTON_BACK])
    commands = {'назад': sv.f_battle_main, '.': sv.f_chose_attack}


class k_EnemyToAttack(Keyboard):
    board = create_keyboard([['. 1', 1, 0], ['. 2', 1, 0], ['. 3', 1, 0], BUTTON_BACK])
    commands = {'назад': sv.f_battle_main, '.': sv.f_attack}


class k_NextTurn(Keyboard):
    board = create_keyboard([['-->', 3, 0], ])
    commands = {'-->': sv.f_battle}


KEYBOARDS = {
    2: k_MainMenu,

    4: k_Inventory,

    3: k_PreDungeon,
    11: k_PreDungeonCharactersSelect,
    12: k_WeaponSelect,

    8: k_CharacterMenu,
    9: k_Character,
    10: k_UpgradeCharacter,

    5: k_Marketplace,
    6: k_MyLots,
    7: k_MarketplaceSearch,

    21: k_BattleMain,
    22: k_Skill_Select,
    23: k_EnemyToAttack,
    24: k_NextTurn,
}
