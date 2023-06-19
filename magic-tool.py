import json
import os
import pandas as pd
from pynput import keyboard
import colorama
from termcolor import colored

colorama.init(autoreset=True)

DATA_BOARD = ""
LIST_LEVEL = ""
LIST_WORDS = ""

SIZE_W = 0
SIZE_H = 0
BOARD = ""
LEVEL_N_WORDS = ""

INDEX_STORE = ""
LEVEL_EDIT = ""

LEVEL_EDIT_SIZE = 25

SELECTED_LEVEL = ""
INDEX_SELECTED = ""
HOTSWAP_KEY = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

CURRENT_MODE = "SELECT MODE"

# '\x1b[B\x1b[C\x1b[A\x1b[D\x1b[B\x1b[D\x1b[C\x1b[A\x1b[B\x1b[C\x1b[A\x1b[C\x1b[C\x1b[C\x1b[B\x1b[D\x1b[C\x1b[A\x1b[D\x1b[C\x1b[B\x1b[Cqeeqeqe\x1b2'
BLACK_LIST = ["\x1b", "[B", "[A", "[C", "[D", "\t", "\n", "\s", "a", "d", "w", "s", "q", "e", "r"]


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[38;5;196m'


def _load_database():
    global DATA_BOARD, LIST_LEVEL, LIST_WORDS

    path = "/Users/locnq/Desktop/Git/word_timber/Assets/Resources/LevelsData/Final/chapter0.json"

    DATA_BOARD = json.load(open(path, "r"))
    LIST_LEVEL = DATA_BOARD["ListLevelsInChapter"]

    data_words = pd.read_csv("words1.0.26.csv")
    LIST_WORDS = data_words["normal words"].to_list()


def _load_level(selected_level):
    global SIZE_W, SIZE_H, BOARD, LEVEL_N_WORDS

    level_n = LIST_LEVEL[selected_level]
    SIZE_W = level_n["h"]
    SIZE_H = level_n["w"]
    BOARD = level_n["b"]
    LEVEL_N_WORDS = [i.upper()
                     for i in LIST_WORDS[selected_level].split(" - ")]


def _prepare_index_store():
    global INDEX_STORE
    # draw the board and convert to array, also create board of index
    row_ele_count = 0

    board_array = [[" " for x in range(SIZE_W)] for y in range(SIZE_H)]
    c_col = 0
    c_row = 0

    # index_store = {
    #   1: [{"r": 0, "c": 0}, {"r": 0, "c": 1}, {"r": 0, "c": 2}]
    # }
    # which index 1 is WHO in horizontal and start at {"r": 0, "c": 0} in board_array
    INDEX_STORE = {}

    for cell in BOARD:
        # print(f"{cell['v']}", end=" ")
        # print(f"{c_row}, {c_col}")
        try:
            board_array[c_row][c_col] = cell['v']
        except:
            pass

        if not cell['v'] == ' ':
            if cell["i"] not in INDEX_STORE:
                INDEX_STORE[cell["i"]] = [{"r": c_row, "c": c_col}]
            else:
                INDEX_STORE[cell["i"]].append({"r": c_row, "c": c_col})

            if cell["ic"]:
                if cell["iw"] not in INDEX_STORE:
                    INDEX_STORE[cell["iw"]] = [{"r": c_row, "c": c_col}]
                else:
                    INDEX_STORE[cell["iw"]].append({"r": c_row, "c": c_col})

        row_ele_count += 1
        c_col += 1
        if row_ele_count == SIZE_W:
            # print()
            row_ele_count = 0
            c_row += 1
            c_col = 0


def _scale_up():

    global LEVEL_EDIT
    # insert board into bigger board 25x25

    LEVEL_EDIT = [[" " for x in range(LEVEL_EDIT_SIZE)]
                  for y in range(LEVEL_EDIT_SIZE)]
    start_point_row = 5
    start_point_col = 5

    # first col and first row will be toạ độ coordinates symbol
    for i in range(LEVEL_EDIT_SIZE):
        LEVEL_EDIT[0][i] = i % 10
        LEVEL_EDIT[i][0] = i % 10

    # import index_store to LEVEL_EDIT: scale coordinates to larger coordinates in LEVEL_EDIT
    for index in INDEX_STORE:
        for coor in INDEX_STORE[index]:
            coor["r"] += start_point_row
            coor["c"] += start_point_col


def _update_level_index():
    global LEVEL_EDIT
    # convert word with index to LEVEL_EDIT from index_store
    for r in range(LEVEL_EDIT_SIZE):
        for c in range(LEVEL_EDIT_SIZE):

            is_set = False  # check if set Letter for cell

            for index in INDEX_STORE:
                i = 0  # index of a letter in word
                for coor in INDEX_STORE[index]:
                    if r == coor["r"] and c == coor["c"]:
                        if not index == INDEX_SELECTED:
                            LEVEL_EDIT[r][c] = f"{colored(LEVEL_N_WORDS[index][i], 'cyan', attrs=['bold'])}"
                        else:
                            LEVEL_EDIT[r][c] = f"{colored(LEVEL_N_WORDS[index][i], 'red', attrs=['bold'])}"

                        is_set = True
                        break
                    i += 1  # move to a next letter

            if not is_set:
                LEVEL_EDIT[r][c] = " "


# print level_edit
def _print_level_edit():
    print("\n\t\t", end="")
    print(" ".join(["~"] + [str(i % 10) for i in range(LEVEL_EDIT_SIZE)]))
    row_count = 0
    for r in LEVEL_EDIT:
        print(f"\t\t{row_count % 10}", end=" ")
        row_count += 1
        for c in r:
            if c == " ":
                print("-", end=" ")
            else:
                print(c, end=" ")
        print()

    # table = PrettyTable()
    # table.field_names = [f"{i:02d}" for i in range(LEVEL_EDIT_SIZE)]
    # table.add_rows(LEVEL_EDIT)
    # table.hrules = ALL
    # print(table)

    # get word's index
    print(f"\t\t\t\tWord\tIndex\t{','.join(LEVEL_N_WORDS[-1])}")
    print("\t\t\t\t------------")
    for i in range(len(LEVEL_N_WORDS)):
        if i == INDEX_SELECTED:
            # print(f"\t\t\t\t{bcolors.RED}{bcolors.UNDERLINE}{LEVEL_N_WORDS[i]}\t{i + 1}{bcolors.ENDC}")
            print(f"\t\t\t\t{colored(LEVEL_N_WORDS[i], 'red')}\t{i + 1}")
        else:
            print(f"\t\t\t\t{LEVEL_N_WORDS[i]}\t{i + 1}")
        print("\t\t\t\t------------")


def _print_current_mode():
    if CURRENT_MODE == "SELECT MODE":
        print(f"You are in {colored('SELECT MODE', 'yellow')}")
    if CURRENT_MODE == "EDIT MODE":
        print(f"You are in {colored('EDIT MODE', 'red')}\n")


def _print_how_to_use():
    print(f"""
    Tip:
    In {colored('Edit', 'red')} mode:
        ↑→↓←\tMove
        WASD\tMove
        R\tRotate horizontal, vertical
        Q, E\tSelect previous, next word
        ESC\tDeselected word
        TAB\tHold Tab to show index of words

    In {colored('Select', 'yellow')} mode:
        save\tSave and back to Level select
        quit\tDiscard changes and back to Level select
    """)


def _move_left(word_index):
    global INDEX_STORE
    for coor in INDEX_STORE[word_index]:
        coor["c"] -= 1


def _move_right(word_index):
    global INDEX_STORE
    for coor in INDEX_STORE[word_index]:
        coor["c"] += 1


def _move_down(word_index):
    global INDEX_STORE
    for coor in INDEX_STORE[word_index]:
        coor["r"] += 1


def _move_up(word_index):
    global INDEX_STORE
    for coor in INDEX_STORE[word_index]:
        coor["r"] -= 1


def _rotate(word_index):

    first_coor = INDEX_STORE[word_index][0]
    second_coor = INDEX_STORE[word_index][1]

    if second_coor["r"] == first_coor["r"] + 1:
        print("Word in vertical")
        _rotate_horizontal(word_index)
        return

    if second_coor["c"] == first_coor["c"] + 1:
        print("Word in horizontal")
        _rotate_vertical(word_index)
        return


def _rotate_vertical(word_index):
    global INDEX_STORE

    # [13,14], [13,15], [13,16] should turn into [13,14], [14,14], [15,14] when rotate vertcal

    step = 0
    for coor in INDEX_STORE[word_index]:
        coor["r"] += step
        coor["c"] -= step
        step += 1


def _rotate_horizontal(word_index):
    global INDEX_STORE

    # [13,14], [14,14], [15,14] should turn into [13,14], [13,15], [13,16] when rotate horizontal

    step = 0
    for coor in INDEX_STORE[word_index]:
        coor["r"] -= step
        coor["c"] += step
        step += 1


def _next_word():
    global INDEX_SELECTED
    if INDEX_SELECTED + 1 < len(LEVEL_N_WORDS):
        INDEX_SELECTED += 1


def _prev_word():
    global INDEX_SELECTED
    if INDEX_SELECTED - 1 >= 0:
        INDEX_SELECTED -= 1

# save to file


def _save_to_file():
    # find top-most and left-most coors in index_store
    top_most_coor = LEVEL_EDIT_SIZE
    left_most_coor = LEVEL_EDIT_SIZE
    bottom_most_coor = 0
    right_most_coor = 0

    for index in INDEX_STORE:
        for coor in INDEX_STORE[index]:
            if coor["r"] <= top_most_coor:
                top_most_coor = coor["r"]

            if coor["c"] <= left_most_coor:
                left_most_coor = coor["c"]

    # print(top_most_coor)
    # print(left_most_coor)
    # print(bottom_most_coor)
    # print(right_most_coor)

    # move all index in INDEX_STORE to fit coor
    for index in INDEX_STORE:
        for coor in INDEX_STORE[index]:
            coor["r"] -= top_most_coor
            coor["c"] -= left_most_coor

    for index in INDEX_STORE:
        for coor in INDEX_STORE[index]:
            if coor["r"] >= bottom_most_coor:
                bottom_most_coor = coor["r"]

            if coor["c"] >= right_most_coor:
                right_most_coor = coor["c"]

    right_most_coor += 1
    bottom_most_coor += 1

    # get board_array_after_edit
    after_edit = [[" " for x in range(right_most_coor)]
                  for y in range(bottom_most_coor)]

    for r in range(bottom_most_coor):
        for c in range(right_most_coor):

            is_set = False  # check if set Letter for cell

            for index in INDEX_STORE:
                i = 0  # index of letter in word
                for coor in INDEX_STORE[index]:
                    if r == coor["r"] and c == coor["c"]:
                        after_edit[r][c] = LEVEL_N_WORDS[index][i]
                        is_set = True
                        break
                    i += 1  # move to next letter

            if not is_set:
                after_edit[r][c] = " "

    # save to file
    # list_level[selected_level] = output
    # output = [
    #     {'v': ' ', 'i': 0, 'ic': False, 'iw': 0},
    #     {'v': ' ', 'i': 0, 'ic': False, 'iw': 0},
    #     ...
    # ]

    output_lv = []

    for r in range(bottom_most_coor):
        for c in range(right_most_coor):
            if after_edit[r][c] == " ":
                output_lv.append(
                    {'v': ' ', 'i': 0, 'ic': False, 'iw': 0}
                )
            else:
                _temp = {'v': ' ', 'i': 0, 'ic': False, 'iw': 0}
                is_check_cross = False  # True to continues search for crossword
                for index in INDEX_STORE:

                    if not is_check_cross:
                        for coor in INDEX_STORE[index]:
                            if r == coor["r"] and c == coor["c"]:
                                _temp['v'] = after_edit[r][c]
                                _temp['i'] = index
                                is_check_cross = True
                                break
                    else:
                        for coor in INDEX_STORE[index]:
                            if r == coor["r"] and c == coor["c"]:
                                _temp['iw'] = index
                                _temp['ic'] = True
                                break

                output_lv.append(_temp.copy())
                _temp.clear()

    # print(output_lv)
    _temp_save = {
        'w': bottom_most_coor,
        'h': right_most_coor,
        'b': output_lv
    }
    DATA_BOARD["ListLevelsInChapter"][SELECTED_LEVEL] = _temp_save.copy()

    path_1 = "/Users/locnq/Desktop/Git/word_timber/Assets/Resources/LevelsData/Final/chapter0.json"
    path_2 = "/Users/locnq/Desktop/Git/word_timber/Assets/Resources/LevelsData/Test/chapter0.json"

    # save to file
    with open(path_1, "w") as save:
        json.dump(DATA_BOARD, save)
        save.close()

    with open(path_2, "w") as save:
        json.dump(DATA_BOARD, save)
        save.close()

# os.funct


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def _give_me_that_shit(level_id):
    # load everything funct
    _load_database()
    _load_level(level_id)
    _prepare_index_store()
    _scale_up()


def _print_me_that_shit():
    # print funct
    cls()
    _update_level_index()
    _print_level_edit()
    _print_how_to_use()
    _print_current_mode()


# control funct
def on_press(key):
    global INDEX_SELECTED
    try:
        # print('alphanumeric key {0} pressed'.format(
        #     key.char))

        if key.char in HOTSWAP_KEY:
            INDEX_SELECTED = int(key.char) - 1
            _print_me_that_shit()

        # if key == keyboard.Key.right:
        #     # print("move right")
        #     _move_right(INDEX_SELECTED)
        #     _print_me_that_shit()
        # if key == keyboard.Key.left:
        #     # print("move left")
        #     _move_left(INDEX_SELECTED)
        #     _print_me_that_shit()
        # if key == keyboard.Key.up:
        #     # print("move up")
        #     _move_up(INDEX_SELECTED)
        #     _print_me_that_shit()
        # if key == keyboard.Key.down:
        #     # print("move down")
        #     _move_down(INDEX_SELECTED)
        #     _print_me_that_shit()

        if key.char == 'w':
            # print("move up")
            _move_up(INDEX_SELECTED)
            _print_me_that_shit()
        if key.char == 'a':
            # print("move up")
            _move_left(INDEX_SELECTED)
            _print_me_that_shit()
        if key.char == 's':
            # print("move up")
            _move_down(INDEX_SELECTED)
            _print_me_that_shit()
        if key.char == 'd':
            # print("move up")
            _move_right(INDEX_SELECTED)
            _print_me_that_shit()
        if key.char == 'q':
            # print("prev word")
            _prev_word()
            _print_me_that_shit()
        if key.char == 'e':
            # print("next word")
            _next_word()
            _print_me_that_shit()
        if key.char == 'r':
            _rotate(INDEX_SELECTED)
            _print_me_that_shit()
            

    except AttributeError:
        # print('special key {0} pressed'.format(
        #     key))
        pass


def on_release(key):
    # print('{0} released'.format(
    #     key))
    if key == keyboard.Key.esc:
        # stop listening event
        _print_me_that_shit()
        return False


def _refine_input(str):
    for bl in BLACK_LIST:
        str = str.replace(bl, "")
        if str in ["save", "quit", "backup", "restore"]:
            return str
    return str


# save funct
# _save_to_file()


if __name__ == "__main__":
    cls()
    # global CURRENT_MODE
    while True:
        is_quit = False
        while True:
            try:
                _temp_input = input("\n Input level you want to change: ")
                if _temp_input == "quit":
                    is_quit = True
                    break
                SELECTED_LEVEL = int(_temp_input)
                # convert level 1 in input to level 0 in data, bc level start at index 0
                SELECTED_LEVEL -= 1
                break
            except:
                print(repr(_temp_input))
                continue

        if is_quit:
            break

        _give_me_that_shit(SELECTED_LEVEL)
        is_save = False
        while True:
            _print_me_that_shit()
            try:

                is_move_on = False

                while True:
                    _temp_input = input("(Select mode) Select word's index: ")
                    _temp_input = _refine_input(_temp_input)
                    if _temp_input.isdigit():
                        INDEX_SELECTED = int(_temp_input) - 1
                        is_move_on = True
                        break
                    else:
                        if _temp_input == "save":
                            is_save = True
                            break
                        if _temp_input == "quit":
                            break
                        print(repr(_temp_input))

                if not is_move_on:
                    break

                CURRENT_MODE = "EDIT MODE"
                _print_me_that_shit()

                with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                    listener.join()
                    listener.stop()
                # while True:
                #     if not on_press():
                #         break

                INDEX_SELECTED = -2

                CURRENT_MODE = "SELECT MODE"

                # a = input("Saved, press Enter to continous")

            except:
                continue

        cls()
        if is_save:
            _save_to_file()
