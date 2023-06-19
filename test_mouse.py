import keyboard

while True:
    if keyboard.read_key() == 'a':
        print('space was pressed')
    # if keyboard.is_pressed("esc"):
    #     break