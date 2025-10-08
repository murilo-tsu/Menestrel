# Importando bibliotecas relevantes
import time
import keyboard
import pyautogui
import pygetwindow
import pywinauto

def automatic_gui_validation(window_title='SAP Logon'):
    pyautogui.moveTo(807,557,duration=3.0)
    time.sleep(30)
    window = pygetwindow.getWindowsWithTitle(window_title)[0]
    if not window.isActive:
        pywinauto.application.Application().connect(handle=window._hWnd).top_window().set_focus()
       
    keyboard.send('enter')
    time.sleep(1)
    keyboard.send('enter')
    time.sleep(60)
    keyboard.send('alt+f4')
    time.sleep(1)
    keyboard.send('tab')
    time.sleep(1)
    keyboard.send('enter')

automatic_gui_validation()