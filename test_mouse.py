from pynput import keyboard

is_selected_word = False
is_on_controlling = True



def on_press(key):
    try:
        # print('alphanumeric key {0} pressed'.format(
        #     key.char))
        
        if key == keyboard.Key.right:
            print("move right")
        if key == keyboard.Key.left:
            print("move left")
        if key == keyboard.Key.up:
            print("move up")
        if key == keyboard.Key.down:
            print("move down")

        if key.char == 'q':
            print("rotate vertical")
        if key.char == 'e':
            print("rotate horizontal")

    except AttributeError:
        # print('special key {0} pressed'.format(
        #     key))
        pass

def on_release(key):
    # print('{0} released'.format(
    #     key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()