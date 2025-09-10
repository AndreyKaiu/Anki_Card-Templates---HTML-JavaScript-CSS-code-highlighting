# -*- coding: utf-8 -*-
# An add-on to the Anki program. For the window with card templates, 
# it adds the ability to color the code, insert and auto-complete some words and lines.
# It can save the cursor position when switching templates.
# It is possible to open the code in an external editor.
# The original idea "HTML Buttons in Template" is from the author: https://ankiweb.net/shared/info/2063726776
# This code has been corrected, improved and supplemented with other ideas:
# - the most important thing and could be in Anki is saving the cursor position (selection)
#     when switching between the front and back templates, css.
# - the ability to save the code and open it with a third-party application 
#     (preferably Visual Studio Code). The Anki editor is not blocked 
#     and if you save in both applications, then even parallel work is possible. 
#     A copy of the template is also saved (by Ctrl + S) to the temporary folder anki_backup.
#     If necessary, such copies can be loaded later.
# - code autocompletion, autoinsert, user code templates.
# - highlighting by code of all words as in the current selection, 
#     the ability to find the desired word by code (Ctrl+F, and continue F3)
# https://github.com/AndreyKaiu/Anki_Card-Templates---HTML-JavaScript-CSS-code-highlighting
# Version 1.1, date: 2025-09-10
import os
import json
import time
import re
import shlex
import copy
import unicodedata
import logging
import tempfile
import subprocess
import anki.lang

from logging import Logger, FileHandler, Formatter
from pathlib import Path
from datetime import datetime, timedelta
from aqt.utils import showText, askUser, tr 
from anki.lang import without_unicode_isolation
from aqt.clayout import CardLayout
from types import MethodType

from aqt import mw
from aqt.qt import *
from aqt.gui_hooks import card_layout_will_show
from aqt.clayout import CardLayout
from aqt.addons import AddonManager
from aqt.utils import tooltip, shortcut, getOnlyText
from aqt.clayout import CardLayout
from aqt.theme import theme_manager
from bs4 import BeautifulSoup, Comment

# ========================= PYQT_VERSION ======================================
try:
    from PyQt6.QtWidgets import (
        QApplication,
        QPushButton, 
        QHBoxLayout, 
        QGroupBox, 
        QColorDialog, 
        QTextEdit,
        QDialog,
        QVBoxLayout,
        QCompleter,
        QFileDialog,
        QLabel,
        QComboBox,
        QLineEdit,
        QStyledItemDelegate        
    )    
    from PyQt6.QtGui import QTextDocument, QTextOption, QGuiApplication, QTextCharFormat, QColor, QFont, QSyntaxHighlighter, QTextCursor, QPainter, QTextFormat
    from PyQt6.QtCore import QRegularExpression, Qt, QSize, QEvent, QTimer   
    pyqt_version = "PyQt6"
except ImportError:
    from PyQt5.QtWidgets import (
        QApplication,
        QPushButton, 
        QHBoxLayout, 
        QGroupBox, 
        QColorDialog, 
        QTextEdit,
        QDialog,
        QVBoxLayout,
        QCompleter,
        QFileDialog,
        QLabel,
        QComboBox,
        QLineEdit,
        QStyledItemDelegate        
    )
    from PyQt5.QtGui import QTextDocument, QTextOption, QGuiApplication, QTextCharFormat, QColor, QFont, QSyntaxHighlighter, QTextCursor, QPainter, QTextFormat
    from PyQt5.QtCore import QRegExp, Qt, QSize, QEvent, QTimer
    pyqt_version = "PyQt5"

if pyqt_version == "PyQt6":    
    KeepAnchor = QTextCursor.MoveMode.KeepAnchor
    MoveAnchor = QTextCursor.MoveMode.MoveAnchor
    NextCharacter = QTextCursor.MoveOperation.NextCharacter
    PreviousCharacter = QTextCursor.MoveOperation.PreviousCharacter
    SingleUnderline = QTextCharFormat.UnderlineStyle.SingleUnderline 
    WA_TransparentForMouseEvents = Qt.WidgetAttribute.WA_TransparentForMouseEvents
    WA_NoSystemBackground = Qt.WidgetAttribute.WA_NoSystemBackground
    WA_TranslucentBackground = Qt.WidgetAttribute.WA_TranslucentBackground
    MetaModifier = Qt.KeyboardModifier.MetaModifier
    ControlModifier = Qt.KeyboardModifier.ControlModifier 
    ShiftModifier = Qt.KeyboardModifier.ShiftModifier
    AltModifier = Qt.KeyboardModifier.AltModifier
    FindBackward = QTextDocument.FindFlag.FindBackward
    FindWholeWords = QTextDocument.FindFlag.FindWholeWords 
    FindCaseSensitively = QTextDocument.FindFlag.FindCaseSensitively
    Start = QTextCursor.MoveOperation.Start
    WaitCursor = Qt.CursorShape.WaitCursor
    GC_white = Qt.GlobalColor.white
    GC_black = Qt.GlobalColor.black
    CustomContextMenu = Qt.ContextMenuPolicy.CustomContextMenu
    Key_Return = Qt.Key.Key_Return
    Key_Space = Qt.Key.Key_Space
    Key_Percent = Qt.Key.Key_Percent
    Key_Tab = Qt.Key.Key_Tab
    Key_Backtab = Qt.Key.Key_Backtab
    Key_Enter = Qt.Key.Key_Enter
    Key_Escape = Qt.Key.Key_Escape
    Key_Up = Qt.Key.Key_Up
    Key_Down = Qt.Key.Key_Down
    Key_V = Qt.Key.Key_V
    Key_Home = Qt.Key.Key_Home
    Key_End = Qt.Key.Key_End
    Key_F1 = Qt.Key.Key_F1
    Key_0 = Qt.Key.Key_0
    Key_Slash = Qt.Key.Key_Slash
    Key_B = Qt.Key.Key_B
    Key_I = Qt.Key.Key_I
    Key_U = Qt.Key.Key_U
    Key_K = Qt.Key.Key_K
    Key_M = Qt.Key.Key_M
    Key_Q = Qt.Key.Key_Q
    Key_Equal = Qt.Key.Key_Equal
    Key_Plus = Qt.Key.Key_Plus
    Key_Exclam = Qt.Key.Key_Exclam
    Key_At = Qt.Key.Key_At
    Key_NumberSign = Qt.Key.Key_NumberSign
    Key_Dollar = Qt.Key.Key_Dollar
    Key_AsciiCircum = Qt.Key.Key_AsciiCircum
    Key_Ampersand = Qt.Key.Key_Ampersand
    Key_Asterisk = Qt.Key.Key_Asterisk
    Key_D = Qt.Key.Key_D
    Key_T = Qt.Key.Key_T
    Key_B = Qt.Key.Key_B
    Key_BraceLeft = Qt.Key.Key_BraceLeft
    Key_BracketLeft = Qt.Key.Key_BracketLeft
    Key_ParenLeft = Qt.Key.Key_ParenLeft
    Key_QuoteDbl = Qt.Key.Key_QuoteDbl
    Key_Apostrophe = Qt.Key.Key_Apostrophe
    Key_Minus = Qt.Key.Key_Minus
    Key_Greater = Qt.Key.Key_Greater


else:
    KeepAnchor = QTextCursor.KeepAnchor
    MoveAnchor = QTextCursor.MoveAnchor
    NextCharacter = QTextCursor.NextCharacter
    PreviousCharacter = QTextCursor.PreviousCharacter
    SingleUnderline = QTextCharFormat.SingleUnderline 
    WA_TransparentForMouseEvents = Qt.WA_TransparentForMouseEvents
    WA_NoSystemBackground = Qt.WA_NoSystemBackground
    WA_TranslucentBackground = Qt.WA_TranslucentBackground 
    MetaModifier = Qt.MetaModifier
    ControlModifier = Qt.ControlModifier 
    ShiftModifier = Qt.ShiftModifier
    AltModifier = Qt.AltModifier
    FindBackward = QTextDocument.FindBackward
    FindWholeWords = QTextDocument.FindWholeWords 
    FindCaseSensitively = QTextDocument.FindCaseSensitively
    Start = QTextCursor.Start
    WaitCursor = Qt.WaitCursor
    GC_white = Qt.white
    GC_black = Qt.black
    CustomContextMenu = Qt.CustomContextMenu
    Key_Return = Qt.Key_Return
    Key_Space = Qt.Key_Space
    Key_Percent = Qt.Key_Percent
    Key_Tab = Qt.Key_Tab
    Key_Backtab = Qt.Key_Backtab
    Key_Enter = Qt.Key_Enter
    Key_Escape = Qt.Key_Escape
    Key_Up = Qt.Key_Up
    Key_Down = Qt.Key_Down
    Key_V = Qt.Key_V
    Key_Home = Qt.Key_Home
    Key_End = Qt.Key_End
    Key_F1 = Qt.Key_F1
    Key_0 = Qt.Key_0
    Key_Slash = Qt.Key_Slash
    Key_B = Qt.Key_B
    Key_I = Qt.Key_I
    Key_U = Qt.Key_U
    Key_K = Qt.Key_K
    Key_M = Qt.Key_M
    Key_Q = Qt.Key_Q
    Key_Equal = Qt.Key_Equal
    Key_Plus = Qt.Key_Plus
    Key_Exclam = Qt.Key_Exclam
    Key_At = Qt.Key_At
    Key_NumberSign = Qt.Key_NumberSign
    Key_Dollar = Qt.Key_Dollar
    Key_AsciiCircum = Qt.Key_AsciiCircum
    Key_Ampersand = Qt.Key_Ampersand
    Key_Asterisk = Qt.Key_Asterisk
    Key_D = Qt.Key_D
    Key_T = Qt.Key_T
    Key_B = Qt.Key_B
    Key_BraceLeft = Qt.Key_BraceLeft
    Key_BracketLeft = Qt.Key_BracketLeft
    Key_ParenLeft = Qt.Key_ParenLeft
    Key_QuoteDbl = Qt.Key_QuoteDbl
    Key_Apostrophe = Qt.Key_Apostrophe
    Key_Minus = Qt.Key_Minus
    Key_Greater = Qt.Key_Greater

# ========================= LOGGING ===========================================
log: Logger = logging.getLogger(__name__)

class Logs:
    def __init__(self, log_dir: Path, version):
        log_dir.mkdir(exist_ok=True, parents=True)
        self.__log_file: Path = log_dir.joinpath("Card Templates - HTML JavaScript CSS code highlighting.log")
        
        self.__root_logger: Logger = self.__configure_logging()
        self.error_count = 0  # Счетчик ошибок

    def root_logger(self) -> Logger:
        return self.__root_logger

    def set_level(self, log_level: str) -> None:
        self.__root_logger.setLevel(log_level)

    def get_log_file(self) -> Path:
        return self.__log_file

    def __configure_logging(self) -> Logger:
        logger: Logger = logging.getLogger(__name__.split(".")[0])
        handler: FileHandler = FileHandler(self.__log_file, encoding="utf-8", errors="replace")
        level: int = logging.DEBUG # (DEBUG, INFO, WARNING, ERROR, CRITICAL) 
        handler.setLevel(level)
        formatter: Formatter = Formatter('%(asctime)s %(levelname)s %(name)s %(funcName)s %(threadName)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)        
        logger.info(f"\n\n{'#' * 34} {logger.name} {'#' * 34}\nLogger was configured: "
                    f"logger_name={logger.name}, version={version} level={logging.getLevelName(level)}, "
                    f"PyQt_version={pyqt_version}\n   file={self.__log_file}"
                    )        
        return logger
    

module_dir: Path = Path(__file__).parent
module_name: str = module_dir.stem
addon_manager: AddonManager = mw.addonManager
version: str = addon_manager.addonMeta(module_name).get("human_version", "0.0")
log_dir: Path = addon_manager.logs_folder(module_name)
logs: Logs = Logs(log_dir, version)
logs.set_level("DEBUG")



# ========================= CONFIG ============================================
# Loading the add-on configuration
config = mw.addonManager.getConfig(__name__)
meta  = mw.addonManager.addon_meta(__name__)
this_addon_provided_name = meta.provided_name

def configF(par1, par2, default=""):
    """получить данные из конфига"""
    try:
        ret = config[par1][par2]
        return ret
    except Exception as e:        
        logError(e)
        return default     
    
# определям темная или светлая тема
theme_night = True if theme_manager.night_mode else False        

themeName = configF("GLOBAL_SETTINGS", "theme", "MODERN")
auto_insert = config["GLOBAL_SETTINGS"]["auto_insert"]
auto_completion = config["GLOBAL_SETTINGS"]["auto_completion"]
languageName = configF("GLOBAL_SETTINGS", "language", "en")
current_language = anki.lang.current_lang #en, pr-BR, en-GB, ru и подобное 
if not languageName: # если надо автоопределение       
    languageName = current_language    
    if languageName not in config["LOCALIZATION"]:        
        languageName = "en" # Если не поддерживается, откатываемся на английский                
    


try:
    localization = config["LOCALIZATION"][languageName]    
except Exception as e:
    text = f"ERROR in add-on '{this_addon_provided_name}'\n"
    text += f"Config[\"GLOBAL_SETTINGS\"][\"language\"] does not contain '{languageName}'"
    text += "\nChange the add-on configuration, \"language\": \"en\""
    languageName = "en"
    config["GLOBAL_SETTINGS"]["language"] = languageName # меняем язык
    mw.addonManager.writeConfig(__name__, config) # записываем конфиг с изменениями  
    showText(text, type="error")

if theme_night:        
    colors = config["THEMES"][themeName]["DARK_MODE"]    
else:
    colors = config["THEMES"][themeName]["LIGHT_MODE"] 

def localizationF(par1, default=""):
    """получить данные из localization = config["LOCALIZATION"][languageName] """
    try:
        ret = localization[par1]
        return ret
    except Exception as e:        
        logError(e)
        return default      
# =============================================================================

html_js_highlighting_addon = None
thisCardLayout = None
template_name = None
gl_model_name = None
from aqt.gui_hooks import card_layout_will_show

original_update_current_ordinal_and_redraw = None

def custom_update_current_ordinal_and_redraw(self, idx: int) -> None:    
    global template_name, gl_model_name, html_js_highlighting_addon, original_update_current_ordinal_and_redraw    
    if self.ignore_change_signals:
        return
    # если изменения пройдут и станет self.ord = idx то надо сохранить позицию
    html_js_highlighting_addon.save_cursor_position(html_js_highlighting_addon.cur_edit_area)

    original_update_current_ordinal_and_redraw(idx) # вызов оригинального

    template_name = self.model["name"] + "_card" + str(self.ord+1)    
    # изменения прошли и вызвать смену позиции        
    html_js_highlighting_addon.restore_cursor_position(html_js_highlighting_addon.cur_edit_area, html_js_highlighting_addon.current_button)
    html_js_highlighting_addon.needs_update_from_external_editor(html_js_highlighting_addon.cur_edit_area)



paste_without_tab_replace = False
def on_card_layout_will_show(card_layout: CardLayout):   
    global thisCardLayout, gl_model_name, template_name, theme_night, colors, html_js_highlighting_addon, original_update_current_ordinal_and_redraw   
    if theme_manager.night_mode: # определям темная или светлая тема
        theme_night = True
    else:
        theme_night = False
    if theme_night:        
        colors = config["THEMES"][themeName]["DARK_MODE"]    
    else:
        colors = config["THEMES"][themeName]["LIGHT_MODE"] 
 
    thisCardLayout = card_layout   
    
    # табуляция 4 символа
    thisCardLayout.tform.edit_area.setTabStopDistance(thisCardLayout.tform.edit_area.fontMetrics().horizontalAdvance('0000')) 
    # Переопределяем метод вставки из буфера обмена
    original_insert_from_mime_data = thisCardLayout.tform.edit_area.insertFromMimeData
    def custom_insert_from_mime_data(source: QMimeData):
        global thisCardLayout, paste_without_tab_replace         
        text = source.text() # Получаем текст из буфера обмена               
        if not paste_without_tab_replace:
            text = text.replace("\t", "    ") # Заменяем табуляции на 4 пробела 
        cursor = thisCardLayout.tform.edit_area.textCursor() # Вставляем измененный текст
        cursor.insertText(text)
    # Заменяем оригинальный метод на наш
    thisCardLayout.tform.edit_area.insertFromMimeData = custom_insert_from_mime_data

    # Изменяем структуру self.cursor_positions для хранения позиции курсора и вертикального скроллинга
    html_js_highlighting_addon.cursor_positions = {
        i: { # стиль общий и всегда хранится в i==0
            "front_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]},
            "back_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]},
            "style_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]}
        }
        for i in range(len(thisCardLayout.templates))
    }

    gl_model_name = card_layout.model["name"] 
    # print("html_js_highlighting_addon.load_cursor_positions_from_prefs21")
    # QTimer.singleShot(100, lambda: html_js_highlighting_addon.load_cursor_positions_from_prefs21(gl_model_name) )
    html_js_highlighting_addon.load_cursor_positions_from_prefs21(gl_model_name)

    # замена на свой update_current_ordinal_and_redraw
    original_update_current_ordinal_and_redraw = card_layout.update_current_ordinal_and_redraw
    # Привязываем кастомный метод к экземпляру card_layout
    card_layout.update_current_ordinal_and_redraw = MethodType(custom_update_current_ordinal_and_redraw, card_layout)
    # Переподключаем сигнал
    card_layout.topAreaForm.templatesBox.currentIndexChanged.disconnect()
    qconnect(
        card_layout.topAreaForm.templatesBox.currentIndexChanged,
        card_layout.update_current_ordinal_and_redraw,
    )   

    
    


    # подмена on_search_changed чтобы можно было сделать поиск назад по Shift+Enter
    def custom_on_search_changed(self, text: str) -> None:
        editor = self.tform.edit_area
        modifiers = QApplication.keyboardModifiers()        
        if modifiers == ShiftModifier:            
            cursor = editor.textCursor()
            start_pos = cursor.position() - 1
            cursor.movePosition(QTextCursor.MoveOperation.Left)  # Перемещаем курсор на одну позицию назад
            editor.setTextCursor(cursor)  # Устанавливаем курсор
            found = editor.find(text, FindBackward)
            if not found:                
                cursor.movePosition(QTextCursor.MoveOperation.End)
                editor.setTextCursor(cursor)
                found = editor.find(text, FindBackward)
                if not found:
                    tooltip("No matches found.")
        else:
            if not editor.find(text):
                # try again from top
                cursor = editor.textCursor()
                cursor.movePosition(Start)
                editor.setTextCursor(cursor)
                if not editor.find(text):
                    tooltip("No matches found.")

    card_layout.tform.search_edit.textChanged.disconnect()
    card_layout.tform.search_edit.setPlaceholderText(localizationF("SearchPlaceholder", "Search ('Enter' - next, 'Shift+Enter' - previous)"))
    card_layout.topAreaForm.templatesBox.setToolTip("↑ " + shortcut("Ctrl+F3") + ", " + shortcut("Ctrl+F4") + "  ↓" )
    card_layout.on_search_changed = MethodType(custom_on_search_changed, card_layout)
    qconnect(card_layout.tform.search_edit.textChanged, card_layout.on_search_changed)       


    # подмена удаления, чтобы можно было удалить и в cursor_positions
    original_onRemoveInner = card_layout.onRemoveInner
    def custom_onRemoveInner(self, template: dict) -> None:
        cord = self.ord
        # удаляем тут и cursor_positions по индексу cord
        if cord in html_js_highlighting_addon.cursor_positions:
            if cord==0 and len(self.templates) > 1: # перепишем стиль из 0
                html_js_highlighting_addon.cursor_positions[cord+1]["style_button"] = html_js_highlighting_addon.cursor_positions[cord]["style_button"]
            del html_js_highlighting_addon.cursor_positions[cord] 
            # Сдвигаем ключи для оставшихся элементов
            keys_to_shift = sorted(k for k in html_js_highlighting_addon.cursor_positions.keys() if k > cord)
            for key in keys_to_shift:
                html_js_highlighting_addon.cursor_positions[key - 1] = html_js_highlighting_addon.cursor_positions.pop(key)
        original_onRemoveInner(template)

    card_layout.onRemoveInner = MethodType(custom_onRemoveInner, card_layout)
    

    # подмена добавления, чтобы можно было cursor_positions правильно отработать
    originl_onAddCard = card_layout.onAddCard
    def custom_onAddCard(self) -> None:
        cnt = self.mw.col.models.use_count(self.model)
        txt = tr.card_templates_this_will_create_card_proceed(count=cnt)
        if cnt and not askUser(txt):
            return
        if not self.change_tracker.mark_schema():
            return

        new_index = len(html_js_highlighting_addon.cursor_positions)
        html_js_highlighting_addon.cursor_positions[new_index] = {
            "front_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]},
            "back_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]},
            "style_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]}
            }

        name = self._newCardName()
        t = self.mm.new_template(name)
        old = self.current_template()
        t["qfmt"] = old["qfmt"]
        t["afmt"] = old["afmt"]
        self.mm.add_template(self.model, t)
        self.ord = len(self.templates) - 1
        self.redraw_everything()

    card_layout.onAddCard = MethodType(custom_onAddCard, card_layout)


    # подмена изменения позиции
    original_onReorder = card_layout.onReorder 
    def custom_onReorder(self) -> None:
        n = len(self.templates)
        template = self.current_template()
        current_pos = self.templates.index(template) + 1
        pos_txt = getOnlyText(
            tr.card_templates_enter_new_card_position_1(val=n),
            default=str(current_pos),
        )
        if not pos_txt:
            return
        try:
            pos = int(pos_txt)
        except ValueError:
            return
        if pos < 1 or pos > n:
            return
        if pos == current_pos:
            return
        new_idx = pos - 1
        if not self.change_tracker.mark_schema():
            return
              
         # Выполняем обмен
        tmp_cursor_positions = copy.deepcopy(html_js_highlighting_addon.cursor_positions[self.ord])       
        html_js_highlighting_addon.cursor_positions[self.ord] = copy.deepcopy(html_js_highlighting_addon.cursor_positions[new_idx])
        html_js_highlighting_addon.cursor_positions[new_idx] = tmp_cursor_positions        
        if self.ord == 0: # если из них был 0, то стили оставляем в нулевом
            html_js_highlighting_addon.cursor_positions[0]["style_button"] = html_js_highlighting_addon.cursor_positions[new_idx]["style_button"]
        if new_idx == 0:
            html_js_highlighting_addon.cursor_positions[0]["style_button"] = html_js_highlighting_addon.cursor_positions[self.ord]["style_button"]
        

        self.mm.reposition_template(self.model, template, new_idx)
        self.ord = new_idx
        self.redraw_everything()

    card_layout.onReorder = MethodType(custom_onReorder, card_layout)

    html_js_highlighting_addon.setup_close_event_handler(card_layout)
    html_js_highlighting_addon.setup_show_event_handler(card_layout)
    html_js_highlighting_addon.setup_hide_event_handler(card_layout)
    
# Подключаем хук
card_layout_will_show.append(on_card_layout_will_show)

def CtrlF4():
    global thisCardLayout    
    thisCardLayout.topAreaForm.templatesBox.setFocus()
    thisCardLayout.update_current_ordinal_and_redraw(thisCardLayout.ord + 1) if thisCardLayout.ord + 1 < len(thisCardLayout.templates) else None

def CtrlF3():
    global thisCardLayout    
    thisCardLayout.topAreaForm.templatesBox.setFocus()
    thisCardLayout.update_current_ordinal_and_redraw(thisCardLayout.ord - 1) if thisCardLayout.ord - 1 > -1 else None

# подмена CardLayout.setupShortcuts чтобы заменить F3, F4 на Ctrl+F3, Ctrl+F4
def custom_CardLayout_setupShortcuts(self) -> None:
    self.tform.front_button.setToolTip(shortcut("Ctrl+1"))
    self.tform.back_button.setToolTip(shortcut("Ctrl+2"))
    self.tform.style_button.setToolTip(shortcut("Ctrl+3"))
    QShortcut(  # type: ignore
        QKeySequence("Ctrl+1"),
        self,
        activated=self.tform.front_button.click,
    )
    QShortcut(  # type: ignore
        QKeySequence("Ctrl+2"),
        self,
        activated=self.tform.back_button.click,
    )
    QShortcut(  # type: ignore
        QKeySequence("Ctrl+3"),
        self,
        activated=self.tform.style_button.click,
    )    
    for i in range(min(len(self.cloze_numbers), 9)):
        QShortcut(  # type: ignore
            QKeySequence(f"Alt+{i+1}"),
            self,
            activated=lambda n=i: self.pform.cloze_number_combo.setCurrentIndex(n),
        )        
# Подменяем метод setupShortcuts
CardLayout.setupShortcuts = custom_CardLayout_setupShortcuts


# =============================================================================


def convert_color_to_hex(color: str) -> str:
    """
    Конвертирует цвет из форматов rgb(), rgba(), hsl(), hsla() в #RRGGBB или #AARRGGBB.
    Если формат не распознан, возвращает исходное значение.
    """
    # Регулярные выражения для rgb/rgba
    rgb_regex = re.compile(r'rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)')
    rgba_regex = re.compile(r'rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(0|1|0?\.\d+)\s*\)')

    # Регулярные выражения для hsl/hsla
    hsl_regex = re.compile(r'hsl\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*\)')
    hsla_regex = re.compile(r'hsla\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*,\s*(0|1|0?\.\d+)\s*\)')

    # Проверяем rgb
    match = rgb_regex.match(color)
    if match:
        r, g, b = map(int, match.groups())
        return f"#{r:02X}{g:02X}{b:02X}"

    # Проверяем rgba
    match = rgba_regex.match(color)
    if match:
        r, g, b = map(int, match.groups()[:3])
        a = float(match.group(4))
        alpha = int(a * 255)        
        return f"#{alpha:02X}{r:02X}{g:02X}{b:02X}"

    # Проверяем hsl
    match = hsl_regex.match(color)
    if match:
        h, s, l = map(int, match.groups())
        r, g, b = hsl_to_rgb(h, s / 100, l / 100)
        return f"#{r:02X}{g:02X}{b:02X}"

    # Проверяем hsla
    match = hsla_regex.match(color)
    if match:
        h, s, l = map(int, match.groups()[:3])
        a = float(match.group(4))
        r, g, b = hsl_to_rgb(h, s / 100, l / 100)
        alpha = int(a * 255)
        return f"#{alpha:02X}{r:02X}{g:02X}{b:02X}"

    # Если формат не распознан, возвращаем исходное значение
    return color

def hsl_to_rgb(h, s, l):
    """
    Преобразует HSL в RGB.
    h: Hue (0-360)
    s: Saturation (0-1)
    l: Lightness (0-1)
    Возвращает кортеж (r, g, b) с компонентами в диапазоне 0-255.
    """
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x
    else:
        r, g, b = 0, 0, 0

    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)

    return r, g, b



class AppFocusWatcher(QObject):  # Наследуемся от QObject
    def __init__(self, app):
        super().__init__()  # Инициализируем базовый класс QObject
        self.app = app
        self.app.installEventFilter(self)
        self.is_active = False  # Флаг активности приложения
        self.activate_trigger = False # Менялось ли активность и надо обработать её

    def eventFilter(self, obj, event):
        # Проверяем тип события в зависимости от версии PyQt
        event_type = event.type()
        if pyqt_version == "PyQt6":
            activate_event = QEvent.Type.ApplicationActivate
            deactivate_event = QEvent.Type.ApplicationDeactivate
        else:  # PyQt5
            activate_event = QEvent.ApplicationActivate
            deactivate_event = QEvent.ApplicationDeactivate

        if event_type == activate_event:
            self.is_active = True                       
        elif event_type == deactivate_event:
            self.is_active = False     
            self.activate_trigger = True                 
        return super().eventFilter(obj, event)

focus_watcher = AppFocusWatcher(QApplication.instance())



class InputDialogWithHistory:
    def __init__(self, nameH="input_dialog_with_history", max_history=20):
        self.max_history = max_history
        self.nameH = nameH
        self.history = {}  # Будет хранить историю для разных заголовков/меток
        self.load_history() # Загружает историю из настроек
        
    def getText(self, parent, title, label, default_text=""):
        """Показывает диалог ввода с историей"""
        # Создаем комбобокс вместо обычного поля ввода
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)
        
        # Метка
        layout.addWidget(QLabel(label))
        
        # Комбобокс с историей
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        combo.setMaxCount(self.max_history)
        combo.setDuplicatesEnabled(False)
        
        # Загружаем историю 
        history_key = self.nameH
        if history_key in self.history:
            for item in self.history[history_key]:
                combo.addItem(item)
        
        if default_text:
            combo.setCurrentText(default_text)
        
        layout.addWidget(combo)
        combo.lineEdit().selectAll()
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                     QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Показываем диалог
        result = dialog.exec()
        text = combo.currentText().strip()
        
        if result == QDialog.DialogCode.Accepted and text:
            # Сохраняем в историю
            self._add_to_history(history_key, text)
            self.save_history()
            return text, True
        else:
            return "", False
    
    def _add_to_history(self, key, text):
        """Добавляет текст в историю"""
        if key not in self.history:
            self.history[key] = []
        
        # Удаляем если уже есть
        if text in self.history[key]:
            self.history[key].remove(text)
        
        # Добавляем в начало
        self.history[key].insert(0, text)
        
        # Ограничиваем размер истории
        if len(self.history[key]) > self.max_history:
            self.history[key] = self.history[key][:self.max_history]
    
    def save_history(self):
        """Сохраняет историю в настройки"""
        try:
            mw.pm.profile[self.nameH] = self.history
        except:
            pass
    
    def load_history(self):
        """Загружает историю из настроек"""
        try:
            self.history = mw.pm.profile.get(self.nameH, {})            
        except:
            self.history = {}
    
    def closeEvent(self, event):
        """Сохраняем историю при закрытии"""
        self.save_history()
        super().closeEvent(event)




class FindReplaceDialog(QDialog):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setWindowTitle(localizationF("Find_and_Replace", "Find and Replace"))
        layout = QVBoxLayout(self)

        cursor = self.editor.textCursor()
        self.cursor_hasSelection = cursor.hasSelection()

        # Заменяем QLineEdit на QComboBox для истории поиска
        self.find_edit = QComboBox()
        self.find_edit.setEditable(True)  # Разрешаем редактирование
        self.find_edit.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)  # Новые элементы в начало
        self.find_edit.setMaxCount(20)  # Максимум 20 элементов в истории
        self.find_edit.setDuplicatesEnabled(False)  # Не допускать дубликаты

        self.replace_edit = QComboBox()
        self.replace_edit.setEditable(True)
        self.replace_edit.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
        self.replace_edit.setMaxCount(20)
        self.replace_edit.setDuplicatesEnabled(False)

        # Загружаем историю из настроек
        self.load_history()

        # Флаги поиска
        self.case_checkbox = QCheckBox(localizationF("Case_sensitive", "Case sensitive"))
        self.case_checkbox.setChecked(True)
        self.word_checkbox = QCheckBox(localizationF("Whole_words", "Whole words"))
        self.word_checkbox.setChecked(False)
        self.selection_checkbox = QCheckBox(localizationF("In_selection_only", "In selection only"))
        self.selection_checkbox.setChecked(False)

        # Кнопки поиска
        btn_layout = QHBoxLayout()
        self.find_btn_prev = QPushButton(localizationF("Find_previous", "Find previous"))
        self.find_btn = QPushButton(localizationF("Find_next", "Find next"))              
        btn_layout.addWidget(self.find_btn_prev)
        btn_layout.addWidget(self.find_btn)

        layout.addWidget(QLabel(localizationF("Find_string", "Find string:")))
        layout.addWidget(self.find_edit)
        layout.addLayout(btn_layout)
        
        if self.cursor_hasSelection: # выбор только в выделении если это выделение было
            layout.addWidget(self.selection_checkbox)
            txt = cursor.selectedText()
            if not any(c in txt for c in {'\n', '\r', '\u2028', '\u2029'}):
                self.find_edit.setCurrentText(cursor.selectedText())
        
        layout.addWidget(self.case_checkbox)
        layout.addWidget(self.word_checkbox)
        

        layout.addWidget(QLabel(localizationF("Replace_with_string","Replace with string:")))
        layout.addWidget(self.replace_edit)
        self.replace_btn = QPushButton(localizationF("Replace","Replace"))
        self.replace_all_btn = QPushButton(localizationF("Replace_All", "Replace All"))
        layout.addWidget(self.replace_btn)
        layout.addWidget(self.replace_all_btn)

        self.find_btn_prev.clicked.connect(self.find_prev)
        self.find_btn.clicked.connect(self.find_next)
        self.replace_btn.clicked.connect(self.replace_one)
        self.replace_all_btn.clicked.connect(self.replace_all)
        
        self.find_edit.lineEdit().selectAll()
        self.replace_edit.lineEdit().selectAll()

        self.selection_start = cursor.selectionStart()
        self.selection_end = cursor.selectionEnd()
        self.find1 = True
        self.find_btn.setDefault(True)  # Сделать find_btn активной по умолчанию


    def load_history(self):
        """Загружает историю поиска и замены из настроек"""
        try:
            # Загрузка истории поиска
            find_history = mw.pm.profile.get('find_replace_find_history', [])
            for item in find_history:
                self.find_edit.addItem(item)
            
            # Загрузка истории замены
            replace_history = mw.pm.profile.get('find_replace_replace_history', [])
            for item in replace_history:
                self.replace_edit.addItem(item)
        except:
            pass


    def save_history(self):
        """Сохраняет историю поиска и замены в настройки"""
        try:
            # Сохраняем историю поиска
            find_history = []
            for i in range(min(self.find_edit.count(), 20)):  # Сохраняем до 20 элементов
                find_history.append(self.find_edit.itemText(i))
            mw.pm.profile['find_replace_find_history'] = find_history
            
            # Сохраняем историю замены
            replace_history = []
            for i in range(min(self.replace_edit.count(), 20)):
                replace_history.append(self.replace_edit.itemText(i))
            mw.pm.profile['find_replace_replace_history'] = replace_history
        except:
            pass


    def add_to_history(self, combo_box, text):
        """Добавляет текст в историю комбобокса"""
        if text.strip():  # Не добавляем пустые строки
            # Удаляем если уже существует
            index = combo_box.findText(text)
            if index >= 0:
                combo_box.removeItem(index)
            # Добавляем в начало
            combo_box.insertItem(0, text)
            combo_box.setCurrentIndex(0)


    def get_flags(self):
        if pyqt_version == "PyQt6":
            flags = QTextDocument.FindFlag(0)
            if self.case_checkbox.isChecked():
                flags |= QTextDocument.FindFlag.FindCaseSensitively
            if self.word_checkbox.isChecked():
                flags |= QTextDocument.FindFlag.FindWholeWords
        else:
            flags = 0
            if self.case_checkbox.isChecked():
                flags |= QTextDocument.FindCaseSensitively
            if self.word_checkbox.isChecked():
                flags |= QTextDocument.FindWholeWords
        return flags


    def find_prev(self) -> bool:
        text = self.find_edit.currentText().strip()
        if not text:
            return False
        
        # Добавляем в историю
        self.add_to_history(self.find_edit, text)
        
        flags = self.get_flags() | FindBackward
        cursor = self.editor.textCursor()              
        if self.selection_checkbox.isChecked() and self.cursor_hasSelection: # Поиск только в выделенном
            if self.find1 == True:
                self.find1 = False
                cursor.setPosition(self.selection_end)
                self.editor.setTextCursor(cursor)           
            found = False
            while True:
                found = self.editor.find(text, flags)
                if not found:
                    break
                c = self.editor.textCursor()
                if c.selectionStart() < self.selection_start or c.selectionEnd() > self.selection_end:
                    cursor = self.editor.textCursor() 
                    cursor.setPosition(self.selection_start)
                    self.editor.setTextCursor(cursor)                    
                    break
                # Нашли в выделении
                return True
            msg = localizationF("Not_found_in_selection", "Not found in selection")
            tooltip(f"<p style='color: yellow; background-color: black'>{msg}</p>")
            return False
        else:
            found = self.editor.find(text, flags)
            if not found:
                msg = localizationF("notfound", "Not found")
                tooltip(f"<p style='color: yellow; background-color: black'>{msg}</p>")
                return False
            return True


    def find_next(self) -> bool:
        text = self.find_edit.currentText().strip()
        if not text:
            return False
        
        # Добавляем в историю
        self.add_to_history(self.find_edit, text)
        
        flags = self.get_flags()
        cursor = self.editor.textCursor()                
        if self.selection_checkbox.isChecked() and self.cursor_hasSelection: # Поиск только в выделенном
            if self.find1 == True:
                self.find1 = False
                cursor.setPosition(self.selection_start)
                self.editor.setTextCursor(cursor)
            found = False
            while True:
                found = self.editor.find(text, flags)
                if not found:
                    break
                c = self.editor.textCursor()
                if c.selectionStart() < self.selection_start or c.selectionEnd() > self.selection_end:
                    cursor = self.editor.textCursor() 
                    cursor.setPosition(self.selection_end)
                    self.editor.setTextCursor(cursor)                    
                    break
                # Нашли в выделении
                return True            
            msg = localizationF("Not_found_in_selection", "Not found in selection")
            tooltip(f"<p style='color: yellow; background-color: black'>{msg}</p>")
            return False
        else:            
            found = self.editor.find(text, flags)
            if not found:
                msg = localizationF("notfound", "Not found")
                tooltip(f"<p style='color: yellow; background-color: black'>{msg}</p>")
                return False
            return True


    def replace_one(self) -> bool:
        self.find1 = False
        text = self.find_edit.currentText().strip()
        replace = self.replace_edit.currentText()
        
        if text:  # Добавляем в историю только если есть что искать
            self.add_to_history(self.find_edit, text)
            self.add_to_history(self.replace_edit, replace)
        
        cursor = self.editor.textCursor()
        if cursor.hasSelection(): 
            cursor.insertText(replace)
            self.find_next()
   

    def replace_all(self):
        self.find1 = False
        text = self.find_edit.currentText().strip()
        replace = self.replace_edit.currentText()
        
        if text:  # Добавляем в историю только если есть что искать
            self.add_to_history(self.find_edit, text)
            self.add_to_history(self.replace_edit, replace)
        
        flags = self.get_flags()
        cursor = self.editor.textCursor()                
        if self.selection_checkbox.isChecked() and self.cursor_hasSelection:
            cursor.setPosition(self.selection_start)            
            self.editor.setTextCursor(cursor)
            n = 0
            r = False            
            while True:
                if not self.find_next():
                    break
                cursor = self.editor.textCursor()
                if cursor.hasSelection(): 
                    cursor.insertText(replace)
                    n += 1                    
                else:
                    break
            msg = localizationF("Replacement", "Replacement")
            tooltip(f"<p style='color: yellow; background-color: black'>{msg}: {n}</p>")
        else:
            self.editor.moveCursor(Start)                        
            n = 0
            while True:
                if not self.find_next():                    
                    break
                cursor = self.editor.textCursor()
                if cursor.hasSelection():                     
                    cursor.insertText(replace)
                    n += 1                    
                else:
                    break
            msg = localizationF("Replacement", "Replacement")
            tooltip(f"<p style='color: yellow; background-color: black'>{msg}: {n}</p>")


    def closeEvent(self, event):
        """Сохраняем историю при закрытии диалога"""
        self.save_history()
        super().closeEvent(event)



def show_find_replace_dialog(edit_area):
    global findStrT
    dialog = FindReplaceDialog(edit_area)
    if pyqt_version == "PyQt6":
        dialog.exec()
    else:
        dialog.exec_()
    if dialog.find_edit.currentText() != "":
        findStrT = dialog.find_edit.currentText()
        




class LineNumberArea(QWidget):    
    def __init__(self, editor):
        global colors
        super().__init__(editor)
        self.editor = editor           

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        global colors
        self.setStyleSheet("background-color: "+ colors["line_number_background_color"] + "; color: " 
                        + colors["line_number_text_color"] + ";")  
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(colors["line_number_background_color"]))

        

        document = self.editor.document()
        font_metrics = self.editor.fontMetrics()
        line_height = font_metrics.height()

        scroll_value = self.editor.verticalScrollBar().value()
        page_bottom = scroll_value + self.editor.viewport().height()

        cursor = self.editor.cursorForPosition(QPoint(0, 0))
        first_visible_block = cursor.block()
        first_visible_block_number = first_visible_block.blockNumber()
        rect = self.editor.cursorRect(cursor)
        top = rect.top()

        block = first_visible_block
        block_number = first_visible_block_number

        # Получаем номер текущей строки
        current_block_number = self.editor.textCursor().blockNumber()


        try:            
            while block.isValid() and top <= page_bottom:
                if block.isVisible():
                    number = str(block_number + 1)

                    # Цвет для текущей строки
                    if block_number == current_block_number:
                        painter.setPen( QColor(colors["current_line_color"]) )  # цвет текущей строки 
                        font = painter.font()
                        font.setBold(True)
                        painter.setFont(font)
                    else:                    
                        painter.setPen(QColor( colors["line_number_text_color"] )) 
                        font = painter.font()
                        font.setBold(False)
                        painter.setFont(font)
                    painter.drawText(
                        0, int(top), self.width() - 5, line_height,
                        Qt.AlignmentFlag.AlignRight if pyqt_version == "PyQt6" else Qt.AlignRight, number
                    )

                    if block_number == current_block_number:
                        # Горизонтальная линия сверху
                        pen = QPen(QColor(colors["current_line_color"]))
                        pen.setWidthF(0.5)
                        painter.setPen(pen)
                        painter.drawLine(0, int(top), self.width(), int(top))
                        # # Линия слева
                        # painter.setPen(QColor("#ff0000"))
                        # painter.drawLine(2, int(top), 2, int(top + line_height))
                        # # Горизонтальная линия снизу
                        # painter.setPen(QColor("#0000ff"))
                        # painter.drawLine(0, int(top + line_height - 1), self.width(), int(top + line_height - 1))

                block = block.next()
                cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
                rect = self.editor.cursorRect(cursor)
                top = rect.top()
                block_number += 1
                
        except Exception as e:        
            logError(e)

        

class TextCharFormatS:
    def __init__(self, formats):
        """=ru= Класс для хранения формата текста"""        
        self._formats = formats  # =ru= Список QTextCharFormat
        self._idx = 0  # =ru= Индекс текущего формата
        self._maxidx = len(self.formats)-1 # =ru= Максимальный индекс формата             

    def get_format_open(self):        
        """=ru= Возвращает текущий формат для открывающего тега"""     
        if self.maxidx==0:
            return self.formats[0]
        else:
            format = self.formats[self.idx]
            self.idx = (self.idx + 1) % (self.maxidx+1) # =ru= +1 индекс 
            return format
        
    def get_format_close(self):        
        """=ru= Возвращает текущий формат для закрывающего тега"""     
        if self.maxidx==0:
            return self.formats[0]
        else:
            self.idx = (self.idx - 1) % (self.maxidx+1) # =ru= -1 индекс 
            format = self.formats[self.idx]             
            return format
        

def logError(e):
    """=ru= показ и запись ошибок в лог"""
    error_text = f"Exception: {e}\n\n{traceback.format_exc()}"  # Полная трассировка ошибки                      
    log.error(error_text)  # Запись в лог
    logs.error_count += 1
    tooltip(f"<p style='color: yellow; background-color: black'>{logs.error_count} ERRORS, last one: {e}<br>See in file: {logs.get_log_file()}</p>")



def ask_user_for_text_find(dialog, title="Brief information that you can understand", 
                     label="Enter a hint:", default_text=""):
    """Запрашивает текстовое значение у пользователя с историей."""
    input_dialog_with_history = InputDialogWithHistory(nameH="ask_user_for_text_find")    
    text, ok = input_dialog_with_history.getText(dialog, title, label, default_text)    
    if ok:
        return text
    return None

def ask_user_for_text_goto(dialog, title="Brief information that you can understand", 
                     label="Enter a hint:", default_text=""):
    """Запрашивает текстовое значение у пользователя с историей."""
    global template_name, gl_model_name
    GotonameH = ""    
    if html_js_highlighting_addon.current_button == "front_button":
        suffix = "_front"
        GotonameH = template_name + suffix        
    elif html_js_highlighting_addon.current_button == "back_button":
        suffix = "_back"
        GotonameH = template_name + suffix
    else:
        suffix = "_style"
        GotonameH = gl_model_name + suffix     
        
    input_dialog_with_history = InputDialogWithHistory(nameH=GotonameH)    
    text, ok = input_dialog_with_history.getText(dialog, title, label, default_text)    
    if ok:
        return text
    return None









findStrT = "" # подстрока которую будем искать
def findF3T(editor, dialog):        
    """поиск подстроки ранее запомненной"""    
    global findStrT
    if not findStrT:
        return
    
    cursor = editor.textCursor()
    document = editor.document()
    
    # Начинаем поиск с позиции конца
    found_cursor = document.find(findStrT,  cursor.selectionEnd() )

    if found_cursor.isNull():
        # Повторный поиск с начала
        notfound = localizationF("notfound", "Not found")
        tooltip(f"<p style='color: yellow; background-color: black'>{notfound}. ⏮️</p>")
        found_cursor = document.find(findStrT, 0)

    if not found_cursor.isNull():
        editor.setTextCursor(found_cursor)        
    else:
        notfound = localizationF("notfound", "Not found")
        tooltip(f"<p style='color: yellow; background-color: black'>{notfound}</p>")


def findShiftF3T(editor, dialog):        
    """поиск назад подстроки ранее запомненной""" 
    global findStrT
    if not findStrT:
        return
    
    cursor = editor.textCursor()
    document = editor.document()
    start_pos = cursor.selectionStart()

    # Если есть выделение — снимаем его и ставим курсор в начало выделения
    if cursor.hasSelection():        
        cursor.setPosition(start_pos)
        editor.setTextCursor(cursor)        

    found_cursor = document.find(findStrT, start_pos, FindBackward)
    
    if not found_cursor.isNull():        
        editor.setTextCursor(found_cursor)
    else:       
        # Если не найдено, можно начать поиск с конца документа
        notfound = localizationF("notfound", "Not found")
        tooltip(f"<p style='color: yellow; background-color: black'>{notfound}. ⏭️</p>")
        found_cursor = document.find(findStrT, document.characterCount() - 1, FindBackward)

        if not found_cursor.isNull():
            editor.setTextCursor(found_cursor)
        else:
            tooltip(f"<p style='color: yellow; background-color: black'>{notfound}</p>")


def findT(editor, dialog):  
    """поиск подстроки и запомним подстроку в findStrT"""     
    global findStrT
    find = localizationF("Find", "Find a substring")
    find_t = localizationF("Find_tooltip", "Enter a substring")
    seltxt = editor.textCursor().selectedText()
    if len(seltxt) == 0: 
        user_find = ask_user_for_text_find(dialog, find, find_t, findStrT) # ввод от пользователя строки 
    else:
        user_find = ask_user_for_text_find(dialog, find, find_t, seltxt) # ввод от пользователя строки 
    if user_find is None or not user_find.strip():
        return
    findStrT = user_find
    findF3T(editor, dialog)


def goto_line(editor, line_num):
    """переход на строку (ПОКА НЕ ИСПОЛЬЗУЕТСЯ)"""
    doc = editor.document()
    block = doc.findBlockByNumber(line_num - 1)
    if not block.isValid():
        return
    cursor = editor.textCursor()
    cursor.setPosition(block.position())
    editor.setTextCursor(cursor)

    # Прокрутить так, чтобы строка была вверху
    block_rect = editor.cursorRect(cursor)
    scroll_bar = editor.verticalScrollBar()
    # block_rect.top() — позиция строки относительно viewport
    # scroll_bar.value() — текущая прокрутка
    # scroll_bar.setValue(scroll_bar.value() + block_rect.top() - 2) — сдвигаем так, чтобы строка была вверху
    scroll_bar.setValue(scroll_bar.value() + block_rect.top() - 2)


def goto_line_preserve_offset(editor, line_num):
    """
    Переходит на строку line_num, сохраняя вертикальный отступ курсора от верхнего края viewport.
    """
    doc = editor.document()
    block = doc.findBlockByNumber(line_num - 1)
    if not block.isValid():
        return
    # 1. Получаем текущий вертикальный отступ курсора от верха viewport
    old_cursor = editor.textCursor()
    old_rect = editor.cursorRect(old_cursor)
    offset_from_top = old_rect.top()
    # 2. Переходим на новую строку
    cursor = editor.textCursor()
    cursor.setPosition(block.position())
    editor.setTextCursor(cursor)
    # 3. Получаем новый rect для курсора
    new_rect = editor.cursorRect(cursor)
    scroll_bar = editor.verticalScrollBar()
    # 4. Корректируем прокрутку так, чтобы новый курсор был на том же расстоянии от верха
    delta = new_rect.top() - offset_from_top
    scroll_bar.setValue(scroll_bar.value() + delta)    


gotoNStr = "1" # номер строки на которую переходим
def gotoN(editor, dialog):
    """переход на строку с номером N если этот номер введет пользователь"""
    global gotoNStr
    goto = localizationF("goto", "Go to line with number")
    gotoEnt = localizationF("gotoEnt", "Enter line number:")
    seltxt = editor.textCursor().selectedText()

    # Проверяем, выделено ли число, иначе предлагаем ввести
    def is_int(s):
        try:
            int(s)
            return True
        except Exception:
            return False

    if len(seltxt) == 0 or not is_int(seltxt.strip()):
        user_find = ask_user_for_text_goto(dialog, goto, gotoEnt, gotoNStr)
    else:
        user_find = ask_user_for_text_goto(dialog, goto, gotoEnt, seltxt.strip())

    if user_find is None or not user_find.strip():
        return

    gotoNStr = user_find.strip()

    # Преобразуем введённое значение в номер строки
    try:
        line_num = int(gotoNStr)
        if line_num < 1:
            raise ValueError
    except Exception:
        tooltip(localizationF("gotoErr", "Please enter a valid positive integer line number"), parent=dialog)
        return

    # Получаем QTextDocument и переходим на нужную строку
    doc = editor.document()
    block = doc.findBlockByNumber(line_num - 1)
    if not block.isValid():
        tooltip(localizationF("gotoErr2", "Line number out of range"), parent=dialog)
        return

    goto_line_preserve_offset(editor, line_num)



class HtmlSyntaxHighlighter(QSyntaxHighlighter):   
    """=ru= Класс для подсветки синтаксиса HTML и CSS в редакторе Anki""" 
    def __init__(self, parent=None):
        super(HtmlSyntaxHighlighter, self).__init__(parent)        

        self.cur_edit_area = None  
        self.edit_area_selected_text = ""       
        self.edit_area_highlighterF4_text = ""

        self.current_line = -1  # Хранит номер текущей строки
        self.current_line_format = QTextCharFormat()
        self.current_line_format.setBackground(QColor(colors["current_line_color"]))

        self.mult_block_start = ["<!--", "/*", "= `", "=`"]
        self.mult_block_end = ["-->", "*/", "`", "`"]
        self.mult_block_idx = -1 # =ru= индекс блока

        self.highlighting_rules = [] # =ru= правила раскрашивания строки     
        self.highlighting_rulesComm = [] # =ru= правила раскрашивания строки даже в комментариях           

        # для поиска в строке перебирая self.mult_block_start
        self.mult_block_start_regex = re.compile("|".join(map(re.escape, self.mult_block_start)))
      
        text_color = QTextCharFormat()        
        try:
            text_color.setForeground(QColor(colors["text_color"]))
        except Exception as e: logError(e)

        error_color = QTextCharFormat()        
        try:
            error_color.setForeground(QColor(colors["error_color"]))
        except Exception as e: logError(e)

        # Defining the orange format for Anki fields =br= Definição do formato laranja para campos do Anki        
        anki_field_color = QTextCharFormat()
        try:
            anki_field_color.setForeground(QColor(colors["x_anki_field_color"]))
        except Exception as e: logError(e)

        brackets_curly_color = QTextCharFormat()
        try:
            brackets_curly_color.setForeground(QColor(colors["x_brackets_curly_color"]))
        except Exception as e: logError(e)
        brackets_round_color = QTextCharFormat()        
        try:
            brackets_round_color.setForeground(QColor(colors["x_brackets_round_color"]))
        except Exception as e: logError(e)
        brackets_square_color = QTextCharFormat()
        try:
            brackets_square_color.setForeground(QColor(colors["x_brackets_square_color"]))
        except Exception as e: logError(e)

        self.comment_color = QTextCharFormat()
        try:
            self.comment_color.setForeground(QColor(colors["x_comment_color"]))
        except Exception as e: logError(e)

        css_id_color = QTextCharFormat()
        try:
            css_id_color.setForeground(QColor(colors["x_css_id_color"]))
        except Exception as e: logError(e)

        css_class_color = QTextCharFormat()
        try:
            css_class_color.setForeground(QColor(colors["x_css_class_color"]))
        except Exception as e: logError(e)


        css_property_color = QTextCharFormat()
        try:
            css_property_color.setForeground(QColor(colors["x_css_property_color"]))
        except Exception as e: logError(e)

        html_tag_attr_color = QTextCharFormat()
        try:
            html_tag_attr_color.setForeground(QColor(colors["x_html_tag_attr_color"]))
        except Exception as e: logError(e)

        html_tag_color = QTextCharFormat()
        try:
            html_tag_color.setForeground(QColor(colors["x_html_tag_color"]))
            html_tag_color.setFontWeight(QFont.Weight.Bold.value if pyqt_version == "PyQt6" else QFont.Bold)
        except Exception as e: logError(e)


        self.keyword_attention_color = QTextCharFormat()        
        try:
            self.keyword_attention_color.setForeground(QColor(colors["x_keyword_attention_color"]))
            self.keyword_attention_color.setFontWeight(QFont.Weight.Bold.value if pyqt_version == "PyQt6" else QFont.Bold)
        except Exception as e: logError(e)
        self.keyword_attention_colorRed = QTextCharFormat()        
        try:
            if pyqt_version == "PyQt6":
                self.keyword_attention_colorRed.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
            else:
                self.keyword_attention_colorRed.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            self.keyword_attention_colorRed.setUnderlineColor(QColor("red"))  # Цвет подчеркивания
        except Exception as e: logError(e)
        self.keyword_attention_colorBlue = QTextCharFormat()        
        try:
            if pyqt_version == "PyQt6":
                self.keyword_attention_colorBlue.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
            else:
                self.keyword_attention_colorBlue.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            self.keyword_attention_colorBlue.setUnderlineColor(QColor("blue"))  # Цвет подчеркивания
        except Exception as e: logError(e)

        keyword_block_color = QTextCharFormat()
        try:
            keyword_block_color.setForeground(QColor(colors["x_keyword_block_color"]))
        except Exception as e: logError(e)

        keyword_color = QTextCharFormat()
        try:
            keyword_color.setForeground(QColor(colors["x_keyword_color"]))        
        except Exception as e: logError(e)

        name_color = QTextCharFormat()
        try:
            name_color.setForeground(QColor(colors["x_name_color"]))
        except Exception as e: logError(e)

        name_function_color = QTextCharFormat()
        try:
            name_function_color.setForeground(QColor(colors["x_name_function_color"]))
        except Exception as e: logError(e)

        number_color = QTextCharFormat()
        try:
            number_color.setForeground(QColor(colors["x_number_color"]))
        except Exception as e: logError(e)

        self.string_color = QTextCharFormat()        
        try:
            self.string_color.setForeground(QColor(colors["x_string_color"]))            
        except Exception as e: logError(e)

        string_multiline_color = QTextCharFormat()
        try:
            string_multiline_color.setForeground(QColor(colors["x_string_multiline_color"]))
        except Exception as e: logError(e)

        self.add_highlighting_rule(R"([\^&\|~!])(?!=)", self.keyword_attention_color) 
        self.add_highlighting_rule(R"(?:&&)|(?:\|\|)", text_color)
        

        # если возможные ошибки = в условиях в for и if
        self.add_highlighting_rule(R"\b(?:(if)|(while))\b\s*\([^\)]*[^=\<\>!](=)[^=][^\)]*\)", self.keyword_attention_color)           
        self.add_highlighting_rule(R"\bfor\b[^;\)]*;[^;\)=\<\>!]*(=)[^;\)=\<\>!]*;[^\)]*\)", self.keyword_attention_color)  
        # внимание если пытаются присвоить числу, функции (скобкам)
        self.add_highlighting_rule(R"(?:(\))|(\b\d+))\s*(=)(?![=\>])", self.keyword_attention_color)
        
        self.add_highlighting_rule(R"\b[a-zA-Z\$\-_][a-zA-Z0-9\$\-_]*\b", name_color)

        self.add_highlighting_rule(R"&(?:[A-Za-z0-9]+|#[0-9]+|#x[0-9A-Fa-f]+)(?=;)", html_tag_color) # &nbsp; и подобное
        self.add_highlighting_rule(R"<(\/?[^> ]+)(?:[^>]*)(?=>)", html_tag_color)
        self.add_highlighting_rule(R"\b([a-zA-Z_]+[a-zA-Z0-9_:\-]*)\s*=(?=[^>]*\>)", html_tag_attr_color)         
        
        self.add_highlighting_rule(R"\.[a-zA-Z\$_][a-zA-Z0-9\$\-_]*\b", css_class_color) 
        self.add_highlighting_rule(R"#\b[a-zA-Z\$_][a-zA-Z0-9\$\-_]*\b", css_id_color)      
        # self.add_highlighting_rule(R"[^\.#:]\b([a-zA-Z\$\-_][a-zA-Z0-9\$\-_]*\b):", css_property_color)              
        self.add_highlighting_rule(R"^\s*\b([a-zA-Z\$\-_][a-zA-Z0-9\$\-_]*\b):", css_property_color)              
        # self.add_highlighting_rule(R"[^\.#:]\b[a-zA-Z\$\-_][a-zA-Z0-9\$\-_]*\b:\s+([^;\>]*)[;\>]", self.string_color)
        self.add_highlighting_rule(R"^\s*\b[a-zA-Z\$\-_][a-zA-Z0-9\$\-_]*\b:\s+([^;\>]*)[;\>]", self.string_color)

        self.add_highlighting_rule(R"(\b[a-zA-Z\$\-_][a-zA-Z0-9\$\-_]*\b\s*)\(", name_function_color)               
        # self.add_highlighting_rule(R"-?\b(?:\d+(?:\.\d+)?(?:e[+-]?\d+)?|0x[0-9a-fA-F]+|0b[01]+|0o[0-7]+)\b", number_color) всё 1asdf считать надо за число а это не пойдет
        self.add_highlighting_rule(R"(\b.?\b\d+\w*(%?|\b))", number_color)        
        self.add_highlighting_rule(R"#[0-9A-Fa-f]{3,8}\b", number_color)       

        # подсветка для скобок разных
        self.add_highlighting_rule(R"[\{\}]", brackets_curly_color)
        self.add_highlighting_rule(R"[\(\)]", brackets_round_color)
        self.add_highlighting_rule(R"[\[\]]", brackets_square_color)

        # подсветка для строк  (смотри в def highlightBlock(self, text): для некоторых там может быть )    
        # self.add_highlighting_rule(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"", self.string_color)      
        # self.add_highlighting_rule(r"'[^'\\]*(?:\\.[^'\\]*)*'", self.string_color) 
        # self.add_highlighting_rule(r"`[^`\\]*(?:\\.[^`\\]*)*`", self.string_color) 
        
        #подсветка ограничивающих символов строк
        self.add_highlighting_rule(R"[\"'`]", self.string_color)

        # строки которые важны для отображения id, class
        self.add_highlighting_rule(R"\bid\s*=\s*[\"']([a-zA-Z\$_][a-zA-Z0-9\$\-_]*\b)[\"']", css_id_color) 
        self.add_highlighting_rule(R"\bclass\s*=\s*[\"']([a-zA-Z\$_][a-zA-Z0-9\$\-_]*\b)[\"']", css_class_color) 

        # особо для style=
        self.add_highlighting_rule(R"\b(style)\s*=\s*", self.keyword_attention_color) 
        
        #self.add_highlighting_rule(R"\b(abstract|await|boolean|byte|case|char|class|const|debugger|default|delete|do|double|else|enum|export|extends|false|final|float|for|function|goto|if|implements|import|in|instanceof|int|interface|let|long|native|new|null|package|private|protected|public|short|static|super|switch|synchronized|this|transient|true|typeof|var|void|volatile|while|with|yield)(?!\s*=)\b", keyword_color)
        self.add_highlighting_rule(R"\b(abstract|await|boolean|byte|case|char|class|const|debugger|default|delete|double|else|enum|export|extends|false|final|float|function|if|implements|import|in|instanceof|int|interface|let|long|native|new|null|package|private|protected|public|short|static|super|switch|synchronized|this|transient|true|typeof|var|void|volatile|with|yield)(?!\s*=)\b", keyword_color)
        
        self.add_highlighting_rule(R"\b(do|for|while|try|catch|finally)(?!\s*=)\b", keyword_block_color)
        self.add_highlighting_rule(R"\b(return|break|continue|goto|throw|close()|exit())(?!\s*=)\b", self.keyword_attention_color)
        self.add_highlighting_rule(R"[ ]", self.keyword_attention_color) 

        # =ru= комментарии (только для строки!) обрабатывать в последнюю очередь
        self.add_highlighting_rule(R"(?:[^:]|^)(//.*$)", self.comment_color)
        self.add_highlighting_rule(R"(//\*.*\*//)", self.comment_color)
        self.add_highlighting_rule(R"<!--.*-->", self.comment_color)
        
        self.add_highlighting_rule(R"\{\{[^{}]+\}\}", anki_field_color)
        self.add_highlighting_rule(R"%%", anki_field_color)

        # правила подсветки даже в комментариях
        self.add_highlighting_ruleComm(R"\{\{[^{}]+\}\}", anki_field_color)
        
     
                
    def enhance_text_edit(self, edit_area):
        self.cur_edit_area = edit_area      

        

    
    def setup_selection_change_handler(self, edit_area: QTextEdit):
        """Подключает обработчик изменения выделения."""
        edit_area.selectionChanged.connect(lambda: self.on_selection_changed(edit_area))

    def on_selection_changed(self, edit_area: QTextEdit):
        """Обрабатывает изменение выделения."""      
        cursor = edit_area.textCursor()
        self.edit_area_selected_text = cursor.selectedText()                      
        
    def rehighlight_code(self):
        """Повторно подсвечивает весь код."""
        if self.cur_edit_area and self.cur_edit_area.highlighter:   
            # Устанавливаем курсор в режим "песочные часы"
            QGuiApplication.setOverrideCursor(WaitCursor)
            try:
                self.edit_area_highlighterF4_text = self.edit_area_selected_text
                # Выполняем подсветку
                self.cur_edit_area.highlighter.rehighlight()
            finally:
                # Возвращаем курсор в нормальное состояние
                QGuiApplication.restoreOverrideCursor()

         
    


    def add_highlighting_rule(self, pattern, color_format):
        """Добавляет правило подсветки в зависимости от версии PyQt."""
        if pyqt_version == "PyQt6":
            regex = QRegularExpression(pattern)
        else:  # PyQt5
            regex = QRegExp(pattern)
        self.highlighting_rules.append((regex, color_format))

    def add_highlighting_ruleComm(self, pattern, color_format):
        """Добавляет правило подсветки в зависимости от версии PyQt."""
        if pyqt_version == "PyQt6":
            regex = QRegularExpression(pattern)
        else:  # PyQt5
            regex = QRegExp(pattern)
        self.highlighting_rulesComm.append((regex, color_format))


    def highlightBlockIdxComm(self, text, idx):
        """=ru= Метод для раскрашивания даже в комментариях"""
        if text is None or len(text) == 0:
            return
        # надо обработать все правила для self.highlighting_rulesComm - даже в комментариях
        if pyqt_version == "PyQt6":
            for pattern, format in self.highlighting_rulesComm:            
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    lci = match.lastCapturedIndex()                    
                    if lci == 0: # =ru= если не указаны группы ()
                        self.setFormat(idx + match.capturedStart(), match.capturedLength(), format)
                    else: # =ru= иначе все группы, остальные пассивные могут быть (?: )
                        for i in range(1, lci+1):      
                            self.setFormat(idx + match.capturedStart(i), match.capturedLength(i), format)
        else: # if pyqt_version == "PyQt5":
            for pattern, format in self.highlighting_rulesComm:
                pos = 0  # Начальная позиция для поиска
                while (pos := pattern.indexIn(text, pos)) != -1:  # Ищем совпадение начиная с позиции pos
                    captured_texts = pattern.capturedTexts()
                    lci = len(captured_texts) - 1  # Количество групп (capturedTexts включает группу 0)                    
                    if lci == 0:  # =ru= если не указаны группы ()
                        self.setFormat(idx + pos, pattern.matchedLength(), format)
                    else:  # =ru= иначе все группы, остальные пассивные могут быть (?: )
                        for i in range(1, lci + 1):
                            group_start = pattern.pos(i)
                            group_length = len(captured_texts[i])
                            if group_start != -1:  # Проверяем, что группа найдена
                                self.setFormat(idx + group_start, group_length, format)                    
                    # Сдвигаем позицию для следующего поиска
                    pos += pattern.matchedLength()      
    
                          

    def isInsideQuotes(self, text, position):
        """
        =ru= Проверяет, находится ли позиция внутри кавычек
        Учитывает экранированные кавычки \", \'
        """
        single_quote = False
        double_quote = False
        backtick = False
        escape = False
        
        for i in range(position):
            char = text[i]
            
            if escape:
                escape = False
                continue
                
            if char == '\\':
                escape = True
                continue
                
            if char == "'":
                single_quote = not single_quote
            elif char == "\"":
                double_quote = not double_quote
            elif char == "`":
                backtick = not backtick
        
        return single_quote or double_quote or backtick
    

    def highlightBlockIdx(self, text, idx, findComm = True):
        """=ru= Метод для раскрашивания блока с частичным смещением """
        if text is None or len(text) == 0:
            return
        
        # проверка на начало комментария
        if findComm:        
            bidx = self.mult_block_idx                  
            if bidx > -1: # если комментарий уже начат
                end = self.mult_block_end[bidx]
                fendidx = text.find(end)                
                # комментарий найден закончившимся
                if fendidx > -1:
                    self.mult_block_idx = -1
                    newidx = fendidx + len(end)
                    text1 = text[:newidx]
                    text2 = text[newidx:] 
                    self.setFormat(idx, len(text1)+ len(end), self.comment_color if bidx < 2 else self.string_color )                    
                    self.highlightBlockIdxComm(text1, idx) # раскраска даже в комментариях
                    self.highlightBlockIdx(text2, idx + newidx)                    
                    return
                else: # вся строка комментарий
                    self.setFormat(idx, len(text), self.comment_color if bidx < 2 else self.string_color)
                    self.highlightBlockIdxComm(text, idx) # раскраска даже в комментариях
                    return
            else: # комментарий еще не найден, надо искать
                start_index = -1
                # Ищем первое совпадение
                match = self.mult_block_start_regex.search(text)
                if match:
                    found = match.group()
                    match_pos = match.start()                      
                    
                    # ПРОВЕРКА: находится ли найденный блок внутри кавычек?
                    if self.isInsideQuotes(text, match_pos):
                        # Пропускаем этот match и ищем следующий
                        remaining_text = text[match_pos + len(found):]
                        next_match = self.mult_block_start_regex.search(remaining_text)
                        if next_match:
                            # Рекурсивно обрабатываем оставшийся текст
                            text_before = text[:match_pos + len(found)]
                            text_after = text[match_pos + len(found):]
                            self.highlightBlockIdx(text_before, idx, False)
                            self.highlightBlockIdx(text_after, idx + len(text_before), True)
                        return
                    
                    # ПРОВЕРКА: если это // и перед ним не стоит :                    
                    if (found == "//") and (match_pos == 0 or (match_pos > 0 and text[match_pos-1] != ":")):
                        # Однострочный комментарий
                        pass
                    else:
                        bidx = self.mult_block_start.index(found) 
                        start_index = match.start() 
                        # нашли, то обработка разделяется на до и после                           
                        lenStBl = len( self.mult_block_start[bidx] )
                        text1 = text[:start_index]
                        text2 = text[start_index+lenStBl:] 

                        self.highlightBlockIdx(text1, idx, False) # тут нет комментария, можно повторно не проверять начало
                        # не включаем равно для поиска = `
                        if found[0]=="=":
                            self.setFormat(idx + start_index+1, lenStBl-1, self.comment_color if bidx < 2 else self.string_color)
                        else:
                            self.setFormat(idx + start_index, lenStBl, self.comment_color if bidx < 2 else self.string_color)
                        self.mult_block_idx = bidx # показываем, что комментарий уже найден и надо искать его конец
                        self.highlightBlockIdx(text2, idx + start_index + lenStBl)                    
                        return


        # надо обработать все правила, так как это не комментарий
        if pyqt_version == "PyQt6":
            for pattern, format in self.highlighting_rules:            
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    lci = match.lastCapturedIndex()                    
                    if lci == 0: # =ru= если не указаны группы ()
                        self.setFormat(idx + match.capturedStart(), match.capturedLength(), format)
                    else: # =ru= иначе все группы, остальные пассивные могут быть (?: )
                        for i in range(1, lci+1):      
                            self.setFormat(idx + match.capturedStart(i), match.capturedLength(i), format)
        else: # if pyqt_version == "PyQt5":
            for pattern, format in self.highlighting_rules:
                pos = 0  # Начальная позиция для поиска
                while (pos := pattern.indexIn(text, pos)) != -1:  # Ищем совпадение начиная с позиции pos
                    captured_texts = pattern.capturedTexts()
                    lci = len(captured_texts) - 1  # Количество групп (capturedTexts включает группу 0)                    
                    if lci == 0:  # =ru= если не указаны группы ()
                        self.setFormat(idx + pos, pattern.matchedLength(), format)
                    else:  # =ru= иначе все группы, остальные пассивные могут быть (?: )
                        for i in range(1, lci + 1):
                            group_start = pattern.pos(i)
                            group_length = len(captured_texts[i])
                            if group_start != -1:  # Проверяем, что группа найдена
                                self.setFormat(idx + group_start, group_length, format)                    
                    # Сдвигаем позицию для следующего поиска
                    pos += pattern.matchedLength()  



    def highlight_simple_strings(self, text, offset):
        """Подсветка строковых значений без исключений."""                        
        regex1 = QRegularExpression(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"")        
        regex2 = QRegularExpression(r"'[^'\\]*(?:\\.[^'\\]*)*'")  
        regex3 = QRegularExpression(r"`[^`\\]*(?:\\.[^`\\]*)*`")  

        regex1.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        regex2.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        regex3.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        iterator = regex1.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(offset + start, length, self.string_color)
            self.highlightBlockIdxComm(text, offset) # раскраска даже в комментариях
        iterator = regex2.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(offset + start, length, self.string_color)
            self.highlightBlockIdxComm(text, offset) # раскраска даже в комментариях
        iterator = regex3.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(offset + start, length, self.string_color)
            self.highlightBlockIdxComm(text, offset) # раскраска даже в комментариях


    def highlightBlock(self, text):   
        """=ru= Метод для раскрашивания блока (строки) текста"""     
                    
        # если это первая строка
        if self.currentBlock().blockNumber() == 0:
            self.mult_block_idx = -1 # =ru= индекс блока            

        self.highlightBlockIdx(text, 0)              

        

        # Регулярные выражения для поиска
        on_regex = re.compile(r"\bon[a-zA-Z]{3,16}\s*=\s*")
        style_regex = re.compile(r"(\bstyle\s*=\s*)|(\bid\s*=\s*)|(\bclass\s*=\s*)")
        quotes_regex1 = re.compile(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"")        
        quotes_regex2 = re.compile(r"'[^'\\]*(?:\\.[^'\\]*)*'")  
        quotes_regex3 = re.compile(r"`[^`\\]*(?:\\.[^`\\]*)*`")  
        position = 0
        lenText = len(text)
        cntErr = 10000
        while position < lenText:       
            # Ищем ближайшие совпадения
            on_match = on_regex.search(text, position)
            style_match = style_regex.search(text, position)
            # Определяем позиции совпадений
            on_pos = on_match.start() if on_match else -1
            style_pos = style_match.start() if style_match else -1     
            # Выбираем минимальную позицию
            next_pos = min(pos for pos in [on_pos, style_pos] if pos != -1) if on_pos != -1 or style_pos != -1 else lenText
            # Обрабатываем текст до найденной позиции
            sub_text = text[position:next_pos]            
            self.highlight_simple_strings(sub_text, position)
            position = next_pos            
            # Пропускаем найденное слово и его значение в кавычках
            if position < lenText:                
                match1 = quotes_regex1.search(text, position)                
                match2 = quotes_regex2.search(text, position)                  
                match3 = quotes_regex3.search(text, position)  
                posN = -1
                pos1 = match1.start() if match1 else -1
                if pos1 != -1:
                    position = match1.end()                 
                    posN = pos1 
                pos2 = match2.start() if match2 else -1
                if pos2 != -1 and (pos2 < posN or posN == -1):
                    position = match2.end()
                    posN = pos2
                pos3 = match3.start() if match3 else -1
                if pos3 != -1 and (pos3 < posN or posN == -1):
                    position = match3.end()
                    posN = pos3
                if posN == -1:
                    position += 1                                         

            cntErr -= 1
            if(cntErr <= 0):
                position = lenText
                log.error("cntErr def highlightBlock(self, text): while position < lenText: ")  # Запись в лог
                break 
                
        # Обрабатываем оставшийся текст
        if position < lenText:
            self.highlight_simple_strings(text[position:], position)

               

        # Подсветка слов с цветами #
        color_regex = QRegularExpression( r'#[a-fA-F0-9]{3,8}\b' )
        color_regex.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        color_iter = color_regex.globalMatch(text)
        while color_iter.hasNext():
            match = color_iter.next()   
            color_code = match.captured(0)
            qcolor = QColor(color_code)
            if not qcolor.isValid():
                continue
            fmt = QTextCharFormat()
            fmt.setBackground(qcolor)
            # Автоматически выбираем белый/чёрный текст по яркости
            if qcolor.lightness() < 128:
                fmt.setForeground(GC_white)
            else:
                fmt.setForeground(GC_black)
            self.setFormat(match.capturedStart(0), match.capturedLength(0), fmt)

        # Подсветка слов заданные словом цвета               
        #color_regex = QRegularExpression( r'\b([a-zA-Z]{3,20})(?:[;"\'])' ) убрал, сделаем проще
        color_regex = QRegularExpression( r'\b([a-zA-Z]{3,20})\b' )
        color_regex.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        color_iter = color_regex.globalMatch(text)
        while color_iter.hasNext():
            match = color_iter.next()   
            color_code = match.captured(1)
            qcolor = QColor(color_code)
            if not qcolor.isValid():
                continue
            fmt = QTextCharFormat()
            fmt.setBackground(qcolor)
            # Автоматически выбираем белый/чёрный текст по яркости
            if qcolor.lightness() < 128:
                fmt.setForeground(GC_white)
            else:
                fmt.setForeground(GC_black)
            self.setFormat(match.capturedStart(1), match.capturedLength(1), fmt)    

        # Подсветка слов с rgb shl
        color_regex = QRegularExpression( r'rgba?\([^\)]+\)|hsla?\([^\)]+\)' )
        color_regex.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        color_iter = color_regex.globalMatch(text)
        while color_iter.hasNext():
            match = color_iter.next()   
            color_code = match.captured(0)
            qcolor = QColor( convert_color_to_hex(color_code) )
            if not qcolor.isValid():
                continue
            fmt = QTextCharFormat()
            fmt.setBackground(qcolor)
            # Автоматически выбираем белый/чёрный текст по яркости
            if qcolor.lightness() < 128:
                fmt.setForeground(GC_white)
            else:
                fmt.setForeground(GC_black)
            #self.setFormat(match.capturedStart(0), match.capturedLength(0), fmt)
            self.setFormat(match.capturedStart(0), 4, fmt)

        
        # Подсветка выделенного текста edit_area_highlighterF4_text
        if self.edit_area_highlighterF4_text and len(self.edit_area_highlighterF4_text) >= 1:
            fmt = QTextCharFormat()
            if theme_night:
                fmt.setBackground(QColor("#5e5e30"))
                fmt.setForeground(QColor("yellow"))
            else:
                fmt.setBackground(QColor("#cfcf6d"))
                fmt.setForeground(QColor("blue"))
           

            pattern = QRegularExpression(re.escape(self.edit_area_highlighterF4_text))    
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)

            # особо для парных
            if len(self.edit_area_highlighterF4_text) == 1:
                strp1 = "{[(<}])>"
                strp2 = "}])>{[(<"
                findp = strp1.find(self.edit_area_highlighterF4_text)
                if findp >= 0:              
                    fmt = QTextCharFormat()
                    if theme_night:
                        fmt.setBackground(QColor("#cfcf6d"))
                        fmt.setForeground(QColor("#e80af7"))
                    else:
                        fmt.setBackground(QColor("#cfcf6d"))
                        fmt.setForeground(QColor("#e80af7"))

                    pattern = QRegularExpression(re.escape( strp2[findp] ))
                    match_iter = pattern.globalMatch(text)
                    while match_iter.hasNext():
                        match = match_iter.next()
                        start = match.capturedStart()
                        length = match.capturedLength()
                        self.setFormat(start, length, fmt)

        
        # подсветка особых пробельных символов (не включать \u200D так как это для emoji Zero Width Joiner (ZWJ, U+200D)  )        
        attBg_regex = QRegularExpression("[\u00A0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u200C\u200E\u200F\u202F\u205F\u3000]+")
        attBg_regex.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        attBg_iter = attBg_regex.globalMatch(text)
        while attBg_iter.hasNext():
            match = attBg_iter.next()
            self.setFormat(match.capturedStart(0), match.capturedLength(0), self.keyword_attention_colorRed)
        # табуляция допустима в некоторых тэгах, так что синим
        attBg_regex = QRegularExpression(R"[\t]+")
        attBg_regex.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        attBg_iter = attBg_regex.globalMatch(text)
        while attBg_iter.hasNext():
            match = attBg_iter.next()
            self.setFormat(match.capturedStart(0), match.capturedLength(0), self.keyword_attention_colorBlue)
      




def show_text_dialog(title: str, content: str, html: bool = False):
        """показать окно с текстом"""
        dialog = QDialog(mw.app.activeWindow())
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        if html:
            text_edit.setHtml(content)
        else:
            text_edit.setPlainText(content)

        close_button = QPushButton("OK")
        close_button.clicked.connect(dialog.close)

        layout.addWidget(text_edit)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.resize(600, 400)
        dialog.exec()




class HtmlJavaScriptHighlightingAddon:
    """=ru= Класс для добавления функционала форматирования текста в редактор Anki"""
    def __init__(self):        
        # super().__init__()        
        global focus_watcher, thisCardLayout
        self.RShift = False
        self.cur_edit_area = None              
        self.historyN = 0 # позиция в истории курсора
        self.current_completion = ""        
        self.update_timer = QTimer()
        self.update_timer.setInterval(5000)  # Интервал 5s
        self.update_timer.timeout.connect(self.timer_needs_update)  # Подключаем обработчик
        focus_watcher.activate_trigger = True
        self.update_timer.start()

        self.sel_par_timer = QTimer()
        self.sel_par_timer.setInterval(100)  # Интервал 100ms
        self.sel_par_timer.setSingleShot(True) # для однократного запуска
        self.sel_par_timer.timeout.connect( lambda: self.highlight_pair(thisCardLayout.tform.edit_area) )  # Подключаем обработчик
        
        card_layout_will_show.append(self.setup_formatting_buttons)
        self.selTextBeforeShift = "" # выделенный текст до нажатия Shift+5 или просто %
        # Изменяем структуру self.cursor_positions для хранения позиции курсора и вертикального скроллинга
        self.cursor_positions = {            
            i: { # стиль общий и всегда хранится в i==0
                "front_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]},
                "back_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]},
                "style_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0, "position_history": [{"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0} for _ in range(7)]}
            }
            for i in range(1)
        }
        self.current_button = "front_button"  # По умолчанию активна front_button
        
        self.auto_close_tags = {            
            "<html>": "</html>", "<head>": "</head>", "<body>": "</body>", "<title>": "</title>",    
            "<script>": "</script>", "<style>": "</style>", "<div>": "</div>", "<span>": "</span>",
            "<p>": "</p>", "<a>": "</a>", "<ul>": "</ul>", "<ol>": "</ol>",
            "<li>": "</li>", "<table>": "</table>", "<thead>": "</thead>", "<tbody>": "</tbody>",
            "<tfoot>": "</tfoot>", "<tr>": "</tr>", "<td>": "</td>", "<th>": "</th>",
            "<b>": "</b>", "<strong>": "</strong>", "<i>": "</i>", "<em>": "</em>",
            "<u>": "</u>", "<mark>": "</mark>", "<small>": "</small>", "<del>": "</del>",
            "<ins>": "</ins>", "<sup>": "</sup>", "<sub>": "</sub>", "<h1>": "</h1>",
            "<h2>": "</h2>", "<h3>": "</h3>", "<h4>": "</h4>", "<h5>": "</h5>",
            "<h6>": "</h6>", "<form>": "</form>", "<label>": "</label>", "<fieldset>": "</fieldset>",
            "<legend>": "</legend>", "<select>": "</select>", "<option>": "</option>", "<textarea>": "</textarea>",
            "<button>": "</button>", "<figure>": "</figure>", "<figcaption>": "</figcaption>", "<article>": "</article>",
            "<section>": "</section>", "<nav>": "</nav>", "<aside>": "</aside>", "<main>": "</main>",
            "<header>": "</header>", "<footer>": "</footer>", "<details>": "</details>", "<summary>": "</summary>",
            "<time>": "</time>","<code>": "</code>", "<pre>": "</pre>", "<blockquote>": "</blockquote>",
            "<q>": "</q>", "<canvas>": "</canvas>", "<svg>": "</svg>", "<noscript>": "</noscript>",
            "<iframe>": "</iframe>", "<object>": "</object>", "<audio>": "</audio>", "<video>": "</video>",
            "<map>": "</map>", "<address>": "</address>"
            }
        
        self.no_close_tags = [
            "<area>", "<base>", "<br>", "<col>", "<embed>", "<hr>",
            "<img>", "<input>", "<link>", "<meta>", "<source>", 
            "<track>", "<wbr>"
        ]
        self.recently_used_tags = []  # Список для хранения недавно введенных элементов
        self.wordsFromEdit_Area = [] # слова из текста 

        # Список HTML-тегов, атрибутов
        self.html_tags = [
            "<a", "<abbr", "<address", "<area", "<article", "<aside", "<audio", "<b", "<base", "<bdi", "<bdo", "<blockquote", "<body",
            "<br", "<button", "<canvas", "<caption", "<cite", "<code", "<col", "<colgroup", "<data", "<datalist", "<dd", "<del", "<details",
            "<dfn", "<dialog", "<div", "<dl", "<dt", "<em", "<embed", "<fieldset", "<figcaption", "<figure", "<footer", "<form", "<h1", "<h2",
            "<h3", "<h4", "<h5", "<h6", "<head", "<header", "<hr", "<html", "<i", "<iframe", "<img", "<input", "<ins", "<kbd", "<label", "<legend",
            "<li", "<link", "<main", "<map", "<mark", "<meta", "<meter", "<nav", "<noscript", "<object", "<ol", "<optgroup", "<option", "<output",
            "<p", "<param", "<picture", "<pre", "<progress", "<q", "<rp", "<rt", "<ruby", "<s", "<samp", "<script", "<section", "<select", "<small",
            "<source", "<span", "<strong", "<style", "<sub", "<summary", "<sup", "<table", "<tbody", "<td", "<template", "<textarea", "<tfoot",
            "<th", "<thead", "<time", "<title", "<tr", "<track", "<u", "<ul", "<var", "<video", "<wbr",
            # атрибуты
            "accept", "accept-charset", "accesskey", "action", "align", "allow", "alt", "async", "autocapitalize",
            "autocomplete", "autofocus", "autoplay", "background", "bgcolor", "border", "buffered", "capture", "challenge",
            "charset", "checked", "cite", "class", "code", "codebase", "color", "cols", "colspan", "content",
            "contenteditable", "contextmenu", "controls", "coords", "crossorigin", "csp", "data", "data-*", "datetime",
            "decoding", "default", "defer", "dir", "dirname", "disabled", "download", "draggable", "enctype", "enterkeyhint",
            "for", "form", "formaction", "formenctype", "formmethod", "formnovalidate", "formtarget", "headers", "height",
            "hidden", "high", "href", "hreflang", "http-equiv", "icon", "id", "importance", "integrity", "intrinsicsize",
            "inputmode", "ismap", "itemprop", "keytype", "kind", "label", "lang", "list", "loading", "loop", "low", "max",
            "maxlength", "minlength", "media", "method", "min", "multiple", "muted", "name", "novalidate", "open", "optimum",
            "pattern", "ping", "placeholder", "poster", "preload", "radiogroup", "readonly", "referrerpolicy", "rel",
            "required", "reversed", "role", "rows", "rowspan", "sandbox", "scope", "scoped", "selected", "shape", "size",
            "sizes", "slot", "span", "spellcheck", "src", "srcdoc", "srclang", "srcset", "start", "step", "style", "summary",
            "tabindex", "target", "title", "translate", "type", "usemap", "value", "width", "wrap",  
            # ARIA атрибуты
            "aria-activedescendant", "aria-atomic", "aria-autocomplete", "aria-busy", "aria-checked", "aria-colcount",
            "aria-colindex", "aria-colspan", "aria-controls", "aria-current", "aria-describedby", "aria-details", "aria-disabled",
            "aria-dropeffect", "aria-errormessage", "aria-expanded", "aria-flowto", "aria-grabbed", "aria-haspopup", "aria-hidden",
            "aria-invalid", "aria-keyshortcuts", "aria-label", "aria-labelledby", "aria-level", "aria-live", "aria-modal",
            "aria-multiline", "aria-multiselectable", "aria-orientation", "aria-owns", "aria-placeholder", "aria-posinset",
            "aria-pressed", "aria-readonly", "aria-relevant", "aria-required", "aria-roledescription", "aria-rowcount",
            "aria-rowindex", "aria-rowspan", "aria-selected", "aria-setsize", "aria-sort", "aria-valuemax", "aria-valuemin",
            "aria-valuenow", "aria-valuetext",
            # CSS атрибуты
            "align-content", "align-items", "align-self", "all", "animation", "animation-delay", "animation-direction",
            "animation-duration", "animation-fill-mode", "animation-iteration-count", "animation-name", "animation-play-state",
            "animation-timing-function", "appearance", "aspect-ratio", "backdrop-filter", "backface-visibility", "background",
            "background-attachment", "background-blend-mode", "background-clip", "background-color", "background-image",
            "background-origin", "background-position", "background-repeat", "background-size", "block-size", "border",
            "border-block", "border-block-color", "border-block-end", "border-block-end-color", "border-block-end-style",
            "border-block-end-width", "border-block-start", "border-block-start-color", "border-block-start-style",
            "border-block-start-width", "border-block-style", "border-block-width", "border-bottom", "border-bottom-color",
            "border-bottom-left-radius", "border-bottom-right-radius", "border-bottom-style", "border-bottom-width",
            "border-collapse", "border-color", "border-end-end-radius", "border-end-start-radius", "border-image",
            "border-image-outset", "border-image-repeat", "border-image-slice", "border-image-source", "border-image-width",
            "border-inline", "border-inline-color", "border-inline-end", "border-inline-end-color", "border-inline-end-style",
            "border-inline-end-width", "border-inline-start", "border-inline-start-color", "border-inline-start-style",
            "border-inline-start-width", "border-inline-style", "border-inline-width", "border-left", "border-left-color",
            "border-left-style", "border-left-width", "border-radius", "border-right", "border-right-color",
            "border-right-style", "border-right-width", "border-spacing", "border-start-end-radius", "border-start-start-radius",
            "border-style", "border-top", "border-top-color", "border-top-left-radius", "border-top-right-radius",
            "border-top-style", "border-top-width", "border-width", "bottom", "box-decoration-break", "box-shadow",
            "box-sizing", "break-after", "break-before", "break-inside", "caption-side", "caret-color", "clear", "clip",
            "clip-path", "color", "column-count", "column-fill", "column-gap", "column-rule", "column-rule-color",
            "column-rule-style", "column-rule-width", "column-span", "column-width", "columns", "contain", "content",
            "counter-increment", "counter-reset", "cursor", "direction", "display", "empty-cells", "filter", "flex",
            "flex-basis", "flex-direction", "flex-flow", "flex-grow", "flex-shrink", "flex-wrap", "float", "font",
            "font-family", "font-feature-settings", "font-kerning", "font-language-override", "font-optical-sizing",
            "font-size", "font-size-adjust", "font-stretch", "font-style", "font-synthesis", "font-variant",
            "font-variant-alternates", "font-variant-caps", "font-variant-east-asian", "font-variant-ligatures",
            "font-variant-numeric", "font-variant-position", "font-variation-settings", "font-weight", "gap", "grid",
            "grid-area", "grid-auto-columns", "grid-auto-flow", "grid-auto-rows", "grid-column", "grid-column-end",
            "grid-column-gap", "grid-column-start", "grid-gap", "grid-row", "grid-row-end", "grid-row-gap", "grid-row-start",
            "grid-template", "grid-template-areas", "grid-template-columns", "grid-template-rows", "hanging-punctuation",
            "height", "hyphens", "image-rendering", "inline-size", "inset", "inset-block", "inset-block-end",
            "inset-block-start", "inset-inline", "inset-inline-end", "inset-inline-start", "isolation", "justify-content",
            "justify-items", "justify-self", "left", "letter-spacing", "line-break", "line-height", "list-style",
            "list-style-image", "list-style-position", "list-style-type", "margin", "margin-block", "margin-block-end",
            "margin-block-start", "margin-bottom", "margin-inline", "margin-inline-end", "margin-inline-start",
            "margin-left", "margin-right", "margin-top", "mask", "mask-border", "mask-border-mode", "mask-border-outset",
            "mask-border-repeat", "mask-border-slice", "mask-border-source", "mask-border-width", "mask-clip",
            "mask-composite", "mask-image", "mask-mode", "mask-origin", "mask-position", "mask-repeat", "mask-size",
            "mask-type", "max-block-size", "max-height", "max-inline-size", "max-width", "min-block-size", "min-height",
            "min-inline-size", "min-width", "mix-blend-mode", "object-fit", "object-position", "offset", "offset-anchor",
            "offset-distance", "offset-path", "offset-position", "offset-rotate", "opacity", "order", "orphans", "outline",
            "outline-color", "outline-offset", "outline-style", "outline-width", "overflow", "overflow-anchor",
            "overflow-block", "overflow-clip-box", "overflow-inline", "overflow-wrap", "overflow-x", "overflow-y", "overscroll-behavior",
            "overscroll-behavior-block", "overscroll-behavior-inline", "overscroll-behavior-x", "overscroll-behavior-y",
            "padding", "padding-block", "padding-block-end", "padding-block-start", "padding-bottom", "padding-inline",
            "padding-inline-end", "padding-inline-start", "padding-left", "padding-right", "padding-top", "page-break-after",
            "page-break-before", "page-break-inside", "paint-order", "perspective", "perspective-origin", "place-content",
            "place-items", "place-self", "pointer-events", "position", "quotes", "resize", "right", "rotate", "row-gap",
            "ruby-align", "ruby-position", "scale", "scroll-behavior", "scroll-margin", "scroll-margin-block",
            "scroll-margin-block-end", "scroll-margin-block-start", "scroll-margin-bottom", "scroll-margin-inline",
            "scroll-margin-inline-end", "scroll-margin-inline-start", "scroll-margin-left", "scroll-margin-right",
            "scroll-margin-top", "scroll-padding", "scroll-padding-block", "scroll-padding-block-end", "scroll-padding-block-start",
            "scroll-padding-bottom", "scroll-padding-inline", "scroll-padding-inline-end", "scroll-padding-inline-start",
            "scroll-padding-left", "scroll-padding-right", "scroll-padding-top", "scroll-snap-align", "scroll-snap-stop",
            "scroll-snap-type", "scrollbar-color", "scrollbar-gutter", "scrollbar-width", "shape-image-threshold",
            "shape-margin", "shape-outside", "tab-size", "table-layout", "text-align", "text-align-last", "text-combine-upright",
            "text-decoration", "text-decoration-color", "text-decoration-line", "text-decoration-style", "text-indent",
            "text-justify", "text-orientation", "text-overflow", "text-rendering", "text-shadow", "text-transform",
            "text-underline-offset", "text-underline-position", "top", "touch-action", "transform", "transform-box",
            "transform-origin", "transform-style", "transition", "transition-delay", "transition-duration",
            "transition-property", "transition-timing-function", "translate", "unicode-bidi", "user-select", "vertical-align",
            "visibility", "white-space", "widows", "width", "will-change", "word-break", "word-spacing", "word-wrap",
            "writing-mode", "z-index", "zoom",

            # JavaScript
            "abstract", "arguments", "await", "boolean", "break", "byte", "case", "catch", 
            "char", "class", "const", "continue", "debugger", "default", "delete", "do", 
            "double", "else", "enum", "eval", "export", "extends", "false", "final", 
            "finally", "float", "for", "function", "goto", "if", "implements", "import", 
            "in", "instanceof", "int", "interface", "let", "long", "native", "new", 
            "null", "package", "private", "protected", "public", "return", "short", 
            "static", "super", "switch", "synchronized", "this", "throw", "throws", 
            "transient", "true", "try", "typeof", "var", "void", "volatile", "while", 
            "with", "yield",
            
            # JavaScript Глобальные объекты и функции
            "Array", "Date", "eval", "function", "hasOwnProperty", "Infinity", "isFinite", 
            "isNaN", "isPrototypeOf", "length", "Math", "NaN", "name", "Number", "Object", 
            "prototype", "String", "toString", "undefined", "valueOf",
            
            # JavaScript Методы
            "apply", "bind", "call", "charAt", "concat", "constructor", "copyWithin", 
            "defineProperty", "entries", "every", "fill", "filter", "find", "findIndex", 
            "forEach", "from", "includes", "indexOf", "join", "keys", "lastIndexOf", 
            "map", "pop", "push", "reduce", "reduceRight", "reverse", "shift", "slice", 
            "some", "sort", "splice", "toLocaleString", "unshift", "values",
            
            # JavaScript ES6+
            "Symbol", "Promise", "Proxy", "Reflect", "Set", "Map", "WeakSet", "WeakMap", 
            "Generator", "async", "await", "ArrayBuffer", "DataView", "Int8Array", 
            "Uint8Array", "Float32Array", "Float64Array", "BigInt", "BigInt64Array", 
            "BigUint64Array",
            
            # JavaScript DOM API
            "document", "window", "navigator", "getElementById", "querySelector", 
            "addEventListener", "removeEventListener", "dispatchEvent", "localStorage", 
            "sessionStorage", "fetch", "Request", "Response", "Headers",

            # Добавлено еще 2025_09_10
            "allSettled", "ankiTtsSetLanguage", "ankiTtsSpeak", "ankiTtsStop", "any",
            "appendChild", "assign", "cancelAnimationFrame", "cancelIdleCallback", "center",
            "charCodeAt", "checkValidity", "classList", "clientHeight", "clientLeft",
            "clientTop", "clientWidth", "cloneNode", "closest", "codePointAt",
            "console", "contains", "create", "createDocumentFragment", "createElement",
            "createTextNode", "cssRules", "currentTarget", "defineProperties", "deleteRule",
            "endsWith", "exec", "exitFullscreen", "findLast", "findLastIndex",
            "flat", "flatMap", "freeze", "fromCharCode", "fromCodePoint",
            "fromEntries", "geolocation", "getAttribute", "getAttributeNode", "getBoundingClientRect",
            "getClientRects", "getComputedStyle", "getDate", "getElementsByClassName", "getElementsByTagName",
            "getOwnPropertyDescriptor", "getOwnPropertyDescriptors", "getOwnPropertyNames", "getOwnPropertySymbols", "getPrototypeOf",
            "getTime", "getTimezoneOffset", "getUserMedia", "getUTCDate", "hasAttribute",
            "hasChildNodes", "hostname", "innerHTML", "insertAdjacentElement", "insertAdjacentHTML",
            "insertAdjacentText", "insertBefore", "insertRule", "isArray", "isExtensible",
            "isFrozen", "isSealed", "localeCompare", "location", "match",
            "matchAll", "matches", "matchMedia", "normalize", "offsetHeight",
            "offsetLeft", "offsetParent", "offsetTop", "offsetWidth", "onchange",
            "onclick", "ondblclick", "onfocus", "oninput", "onkeydown",
            "onkeyup", "onload", "onmouseover", "onresize", "onsubmit",
            "outerHTML", "padEnd", "padStart", "parentElement", "parentNodetoLocaleLowerCase",
            "preventDefault", "preventExtensions", "querySelectorAll", "querySelectorAll", "race",
            "reject", "removeAttribute", "removeAttributeNode", "removeChild", "repeat",
            "replace", "replaceAll", "replaceChild", "reportValidity", "requestAnimationFrame",
            "requestFullscreen", "requestIdleCallback", "resolve", "scrollBy", "scrollHeight",
            "scrollIntoView", "scrollLeft", "scrollTo", "scrollTop", "scrollWidth",
            "seal", "search", "selectedIndex", "selectedOptions", "setAttribute",
            "setAttributeNode", "setCustomValidity", "setDate", "setPrototypeOf", "setTime",
            "setUTCDate", "speak", "SpeechSynthesisUtterance", "startsWith", "stopImmediatePropagation",
            "styleSheets", "substring", "test", "textContent", "toDateString",
            "toggleAttribute", "toJSON", "toLocaleDateString", "toLocaleLowerCase", "toLocaleTimeString",
            "toLocaleUpperCase", "toLowerCase", "toTimeString", "toUpperCase", "toUTCString",
            "trim", "trimEnd", "trimLeft", "trimRight", "trimStart",
            "valueAsDate", "valueAsNumber"
        ]
        # убираем дубли если будет и отсортируем
        self.html_tags = sorted(list(set(self.html_tags)))

        template_codes = config.get("TEMPLATE_CODE", [])  # Извлекаем TEMPLATE_CODE или пустой список
        # Заменяем табуляцию на символ ⇥ для отображения
        template_codes = [tag.replace("\t", "⇥") for tag in template_codes]
        self.html_tags.extend(template_codes)  # Добавляем шаблоны в html_tags
         
   

    def setup_pair_highlight(self, edit_area: QTextEdit):
        # Подключаем обработчик изменения выделения
        edit_area.selectionChanged.connect(lambda: self.delayed_pair_highlight(edit_area))
        

    def delayed_pair_highlight(self, edit_area):
        # Через 100 мс вызываем подсветку пары
        self.sel_par_timer.stop()        
        self.sel_par_timer.start()


    def find_first_backslash_position(self, text, pos_in_line):
        """
        Ищет с конца строки первое вхождение из 2 символов "\\\\" (ближайшее к началу строки),
        которое не является частью ":\\\\", игнорируя символы внутри 
        строковых литералов и комментариев.
        
        Args:
            text: строка для поиска
            pos_in_line: позиция, с которой начинать поиск (обычно позиция курсора)
        
        Returns:
            int: позиция найденного "\\\\" или -1 если не найдено
        """
        if pos_in_line <= 1:  # Нужно как минимум 2 символа для поиска
            return -1
        
        i = pos_in_line - 1  # начинаем с позиции перед курсором
        stack = []  # стек для отслеживания открытых строк/комментариев
        found_pos = -1  # позиция найденной пары обратных слешей
        
        while i >= 1:  # Нужно как минимум 2 символа для проверки
            char = text[i]
            
            # Проверяем, находимся ли мы внутри строки/комментария
            if stack:
                # Если внутри строки/комментария, проверяем закрытие
                top = stack[-1]
                
                if top == '`' and char == '`':
                    # Проверяем экранирование для ` (нет экранирования в `)
                    stack.pop()
                    i -= 1
                    continue
                    
                elif top == '"' and char == '"':
                    # Проверяем экранирование для "
                    if i > 0 and text[i-1] == '\\':
                        # Экранированная кавычка, пропускаем
                        i -= 2
                        continue
                    else:
                        stack.pop()
                        i -= 1
                        continue
                        
                elif top == "'" and char == "'":
                    # Проверяем экранирование для '
                    if i > 0 and text[i-1] == '\\':
                        # Экранированная кавычка, пропускаем
                        i -= 2
                        continue
                    else:
                        stack.pop()
                        i -= 1
                        continue
                        
                elif top == '*/' and i >= 1 and text[i-1:i+1] == '/*':
                    # Закрытие многострочного комментария
                    stack.pop()
                    i -= 2
                    continue
                    
                elif top == '-->' and i >= 3 and text[i-3:i+1] == '<!--':
                    # Закрытие HTML комментария
                    stack.pop()
                    i -= 4
                    continue
                    
                # Если внутри строки/комментария, просто пропускаем символ
                i -= 1
                continue
            
            # Если не внутри строки/комментария, проверяем открытие
            if char == '`':
                stack.append('`')
                i -= 1
                continue
                
            elif char == '"':
                # Проверяем экранирование
                if i > 0 and text[i-1] == '\\':
                    # Экранированная кавычка, не открываем строку
                    i -= 2
                    continue
                else:
                    stack.append('"')
                    i -= 1
                    continue
                    
            elif char == "'":
                # Проверяем экранирование
                if i > 0 and text[i-1] == '\\':
                    # Экранированная кавычка, не открываем строку
                    i -= 2
                    continue
                else:
                    stack.append("'")
                    i -= 1
                    continue
                    
            elif i >= 1 and text[i-1:i+1] == '*/':
                stack.append('*/')
                i -= 2
                continue
                
            elif i >= 3 and text[i-3:i+1] == '<!--':
                stack.append('-->')
                i -= 4
                continue
                
            # Ищем два обратных слеша подряд
            elif i >= 1 and text[i-1] == '\\' and char == '\\':
                # Проверяем, не является ли это частью ':\\\\'
                if i >= 2 and text[i-2] == ':':
                    # Это ':\\\\', пропускаем
                    i -= 3
                    continue
                else:
                    # Нашли '\\\\', запоминаем позицию первого слеша
                    found_pos = i - 1
                    # Продолжаем искать ближе к курсору
                    i -= 2
                    continue
                    
            i -= 1
        
        return found_pos



    def highlight_pair(self, edit_area):        
        """подсветка парных скобок, тегов"""
               

        cursor = edit_area.textCursor()
        text = edit_area.toPlainText()
        sel = cursor.selectedText()
        extra_selections = []
        
        

        # Цвет подсветки
        fmt = QTextCharFormat()
        if theme_night:
            fmt.setBackground(QColor("#cfcf6d"))
            fmt.setForeground(QColor("#e80af7"))
        else:
            fmt.setBackground(QColor("#cfcf6d"))
            fmt.setForeground(QColor("#e80af7"))


        if not sel:
            char = cursor.document().characterAt(cursor.position()) 
        else:
            char = sel[0]
        
        pairs = {'<': '>', '{': '}', '(': ')', '[': ']', '}': '{', ')': '(', ']': '['}
        open_chars = '{(['
        close_chars = '})]'

        if char in open_chars:
            direction = 1
        elif char in close_chars:
            direction = -1
        else:
            direction = 1
        

        # === Скобки ===
        if char in pairs:
            try:
                edit_area.setUpdatesEnabled(False)
                match = pairs[char]
                stack = 1                
                cur = QTextCursor(edit_area.document())                                
                cur.setPosition(cursor.selectionStart())
                next_c = ""
                prev_c = ""
                comm = False
                find_comm = ""                
                len_find_comm = 0
                findNR = False    
                nextN = 0            
                n = 0
                while True:
                    moved = cur.movePosition(NextCharacter if direction == 1 else PreviousCharacter)
                    if not moved:
                        break
                    c = cur.document().characterAt(cur.position())
                    next_c = ""
                    if direction == -1: # если назад поиск, то заглянем на 1 далее
                        movedN = cur.movePosition(PreviousCharacter)
                        if movedN:
                            next_c = cur.document().characterAt(cur.position())
                            cur.movePosition(NextCharacter) # возрат позиции назад

                    prev_c += c
                    if c == "\u2029": # PARAGRAPH SEPARATOR.
                        findNR = True                                            

                    n += 1
                    if n > 40:
                        prev_c = prev_c[-5:]
                        n = 5

                    if nextN != 0: # проматываем к // если поиск с конца в начало
                        if nextN > 0:
                            nextN -= 1                           
                        continue 

                    if not comm:
                        if direction == 1:
                            if n == 1:
                                s1 = prev_c[-1:] 
                                if s1 == "'":
                                    comm = True
                                    find_comm = "'"
                                    len_find_comm = 1
                                    continue   
                                if s1 == '"':
                                    comm = True
                                    find_comm = '"'
                                    len_find_comm = 1
                                    continue   
                                if s1 == '`':
                                    comm = True
                                    find_comm = '`'
                                    len_find_comm = 1
                                    continue 

                            if n == 2:   
                                s2 = prev_c[-2:]  
                                if s2 == "//":
                                    comm = True
                                    find_comm = "\u2029" # PARAGRAPH SEPARATOR.
                                    len_find_comm = 1
                                    continue  

                            if n >= 2:
                                s1 = prev_c[-1:]
                                s2 = prev_c[-2:] 
                                if s1 == "'" and s2 != "\\'":
                                    comm = True
                                    find_comm = "'"
                                    len_find_comm = 1
                                    continue   
                                if s1 == '"' and s2 != '\\"':
                                    comm = True
                                    find_comm = '"'
                                    len_find_comm = 1                                    
                                    continue    
                                if s1 == '`':
                                    comm = True
                                    find_comm = '`'
                                    len_find_comm = 1
                                    continue                                                             
                                if s2 == "//" and (n ==2 or prev_c[-3:] != "://"):
                                    comm = True
                                    find_comm = "\u2029" # PARAGRAPH SEPARATOR.
                                    len_find_comm = 1
                                    continue
                                if s2 == "/*":
                                    comm = True
                                    find_comm = "*/"
                                    len_find_comm = 2
                                    continue    

                            if n >= 3:
                                s2 = prev_c[-2:]
                                s3 = prev_c[-3:] 
                                if s2 == "//" and s3 != "://":
                                    comm = True
                                    find_comm = "\u2029" # PARAGRAPH SEPARATOR.
                                    len_find_comm = 1
                                    continue                                

                            if n >= 4: 
                                if prev_c[-4:] == "<!--":                            
                                    find_comm = "-->"
                                    len_find_comm = 3
                                    # if char == "<":
                                    #     stack -= 1
                                    continue

                        else: # поиск назад
                            if n == 1 or (findNR and c != "\u2029" and c != "\u2028"):
                                findNR = False
                                nextN = 0
                                cur_line = cur.block().text() # Получаем текущую строку, где находится курсор 
                                pos_in_line = cur.position() - cur.block().position() # Позиция курсора в строке 
                                backslash_pos = self.find_first_backslash_position(cur_line, pos_in_line)
                                if backslash_pos != -1:
                                    nextN = pos_in_line - backslash_pos; 
                                    continue     

                            if n >= 1:
                                s1 = prev_c[-1:] 
                                if s1 == "'" and next_c != "\\":
                                    comm = True
                                    find_comm = "'"
                                    len_find_comm = 1
                                    continue   
                                if s1 == '"' and next_c != "\\":
                                    comm = True
                                    find_comm = '"'
                                    len_find_comm = 1
                                    continue
                                if s1 == '`':
                                    comm = True
                                    find_comm = '`'
                                    len_find_comm = 1
                                    continue
                            if n >= 2:
                                s2 = prev_c[-2:]
                                if s2 == "/*":
                                    comm = True
                                    find_comm = "*/"
                                    len_find_comm = 2
                                    continue
                            if n >= 3: 
                                if prev_c[-3:] == ">--":                            
                                    find_comm = "--!<"
                                    len_find_comm = 4
                                    # if char == ">":
                                    #     stack -= 1
                                    continue

                            # if n >= 2:                                
                            #     # if findNR and c != "\u2029" and c != "\u2028":                                     
                            #     #     findNR = False
                            #     #     findSS = False                                    
                            #     #     cur_line = cur.block().text() # Получаем текущую строку, где находится курсор                                    
                            #     #     pos_in_line = cur.position() - cur.block().position() # Позиция курсора в строке                                    
                            #     #     idx = cur_line.find("//") # Проверяем, есть ли // в строке до позиции курсора
                            #     #     # если найдено будет :// то это не комментарий, а URL
                            #     #     if (idx < 1 or cur_line[idx-1] != ":") and (idx != -1) and (idx < pos_in_line):
                            #     #         # После // не должно быть */ и -->
                            #     #         after = cur_line[idx+2:]
                            #     #         if "*/" not in after and "-->" not in after:
                            #     #             findNR = True                                            
                            #     #             continue  
                            #     #     if idx != -1:    
                            #     #         findSS = True                               

                            #     s2 = prev_c[-2:]
                            #     if s2 == "//":
                            #         comm = True
                            #         # find_comm = "\u2029" # PARAGRAPH SEPARATOR  
                            #         # len_find_comm = 1
                            #         find_comm = "//"
                            #         len_find_comm = 2
                            #         continue
                      
                        
                    else: # если идет комментарий
                        s2 = prev_c[-len_find_comm:]                        
                        if s2 == find_comm and (find_comm=="'" or find_comm=='"'): 
                            if (direction == 1 and prev_c[-len_find_comm-1:] != '\\"' and prev_c[-len_find_comm-1:] != "\\'") or (direction != 1 and next_c != "\\"):                                
                                comm = False
                                find_comm = ""
                                len_find_comm = 0
                            else:
                                continue                                    
                        else:
                            if s2 == find_comm:
                                comm = False
                                find_comm = ""
                                len_find_comm = 0
                            else:
                                continue     


                    if c == char:
                        stack += 1
                    elif c == match:
                        stack -= 1
                        if stack == 0:
                            sel1 = QTextEdit.ExtraSelection()
                            sel1.cursor = edit_area.textCursor()
                            sel1.cursor.setPosition(cur.position())
                            cur2 = QTextCursor(cur)
                            cur2.movePosition(NextCharacter, KeepAnchor)
                            sel1.cursor.setPosition(cur2.position(), KeepAnchor)
                            sel1.format = fmt
                            extra_selections.append(sel1)
                            break
               
                edit_area.setExtraSelections(extra_selections)                                
            finally:
                edit_area.setUpdatesEnabled(True)
            return
        
        else:
            if not sel:
                edit_area.setExtraSelections([])                
                return
            

        # --- Теги ---
        import re
        try:
            edit_area.setUpdatesEnabled(False)
            pos = cursor.selectionStart()
            tag_match = re.match(r'([a-zA-Z0-9]+)', sel)
            if tag_match:
                tag_name = tag_match.group(1)
                left = "" 
                left2 = ""
                if pos > 0:                
                    cur = edit_area.textCursor()                
                    cur.movePosition(PreviousCharacter) # сбросит выделение
                    cur.movePosition(PreviousCharacter) # переместит назад                
                    left = cur.document().characterAt(cur.position()) 
                    if pos > 1:                 
                        cur.movePosition(PreviousCharacter) # переместит назад                
                        left2 = cur.document().characterAt(cur.position())                            
                single_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
                is_single_tag = tag_name.lower() in single_tags

                if left == "<":                                    
                    # ищем закрывающий
                    stack = 1
                    cur = edit_area.textCursor()   
                    cur.movePosition(NextCharacter) # сбросит выделение и перейдет за него
                    cur.movePosition(PreviousCharacter) # переместит назад  
                    find_self_closing_tag = True
                    cprev = "" # предыдущий символ
                    prev_c = ""
                    n = 0
                    comm = False
                    
                    while cur.movePosition(NextCharacter): # перемещаемся к следующему символу
                        c = cur.document().characterAt(cur.position())   
                        prev_c += c
                        n += 1
                        if n > 40:
                            prev_c = prev_c[-5:]
                            n = 5


                        if not comm:
                            if n > 4:
                                if prev_c[-4:] == "<!--":                                    
                                    comm = True
                                    cprev = c
                                    continue                                
                        else:
                            if n > 3:
                                if prev_c[-3:] == "-->":                                    
                                    comm = False
                                    cprev = c
                            continue


                        if find_self_closing_tag and c == ">":       
                            find_self_closing_tag = False                            
                            # Если одиночный тег (br, img и др.) — подсветить только >
                            # Самозакрывающийся тег, подсветить только >
                            if cprev == "/" or is_single_tag:                                      
                                sel1 = QTextEdit.ExtraSelection()
                                sel1.cursor = edit_area.textCursor()
                                sel1.cursor.setPosition(cur.position())    
                                sel1.cursor.setPosition(cur.position()+1, KeepAnchor)
                                sel1.format = fmt
                                extra_selections.append(sel1)
                                edit_area.setExtraSelections(extra_selections)
                                return         

                        if c == "<": # требуется проверка на <tag_name или </tag_name 
                            find_self_closing_tag = False 
                            temp_cur = QTextCursor(cur) 
                            open_tag = True                                                        
                            find_tag_name = ""
                            if temp_cur.movePosition(NextCharacter):
                                tc = temp_cur.document().characterAt(temp_cur.position())  
                                if tc == "/":
                                     open_tag = False
                                else:
                                   find_tag_name += tc
                                while temp_cur.movePosition(NextCharacter):                                    
                                    tc = temp_cur.document().characterAt(temp_cur.position())  
                                    if tc == ">" or tc == " ":
                                        break
                                    find_tag_name += tc
                            if find_tag_name == tag_name:
                                if open_tag:
                                    stack += 1
                                else:
                                    stack -= 1
                                if stack == 0:
                                    sel1 = QTextEdit.ExtraSelection()
                                    sel1.cursor = edit_area.textCursor()
                                    sel1.cursor.setPosition(temp_cur.position()-1-len(tag_name))    
                                    sel1.cursor.setPosition(temp_cur.position(), KeepAnchor)
                                    sel1.format = fmt
                                    extra_selections.append(sel1)
                                    break
                        cprev = c

                    edit_area.setUpdatesEnabled(True)
                    edit_area.setExtraSelections(extra_selections)
                    return


                elif left == "/" and left2 == "<":
                    # Закрывающий тег: ищем назад открывающий
                    stack = 1
                    cur = edit_area.textCursor()   
                    
                    cur.movePosition(PreviousCharacter) # сбросит выделение
                    cur.movePosition(PreviousCharacter) # переместит назад (на /)
                    cur.movePosition(PreviousCharacter) # переместит назад (на <)
                    prev_c = ""
                    n = 0
                    comm = False

                    while cur.movePosition(PreviousCharacter): # перемещаемся к предыдущему символу
                        c = cur.document().characterAt(cur.position())                           
                        prev_c += c
                        n += 1
                        if n > 40:
                            prev_c = prev_c[-5:]
                            n = 5

                        if not comm:
                            if n > 3:
                                if prev_c[-3:] == ">--":
                                    comm = True
                                    continue                                
                        else:
                            if n > 4:
                                if prev_c[-4:] == "--!<":
                                    comm = False
                            continue

                        if c == "<": # требуется проверка на <tag_name или </tag_name 
                            temp_cur = QTextCursor(cur)                            
                            open_tag = True                                                        
                            find_tag_name = ""
                            if temp_cur.movePosition(NextCharacter):
                                tc = temp_cur.document().characterAt(temp_cur.position())  
                                if tc == "/":
                                     open_tag = False
                                else:
                                   find_tag_name += tc
                                while temp_cur.movePosition(NextCharacter):                                    
                                    tc = temp_cur.document().characterAt(temp_cur.position())  
                                    if tc == ">" or tc == " ":
                                        break
                                    find_tag_name += tc
                            if find_tag_name == tag_name:
                                if open_tag:
                                    stack -= 1
                                else:
                                    stack += 1
                                if stack == 0:
                                    sel1 = QTextEdit.ExtraSelection()
                                    sel1.cursor = edit_area.textCursor()
                                    sel1.cursor.setPosition(temp_cur.position()-len(tag_name))    
                                    sel1.cursor.setPosition(temp_cur.position(), KeepAnchor)
                                    sel1.format = fmt
                                    extra_selections.append(sel1)
                                    break
                   

                    edit_area.setUpdatesEnabled(True)
                    edit_area.setExtraSelections(extra_selections)
                    return

            # Если ничего не найдено — снять подсветку
            edit_area.setExtraSelections([])

        finally:
            edit_area.setUpdatesEnabled(True)



    def setup_close_event_handler(self, card_layout: QWidget):
        """Подключает обработчик закрытия окна редактора шаблонов."""
        original_close_event = card_layout.closeEvent

        def custom_close_event(event):
            global focus_watcher            
            focus_watcher.activate_trigger = False
            self.update_timer.stop()                                                         
            original_close_event(event) # Вызов оригинального обработчика
        card_layout.closeEvent = custom_close_event

    def setup_hide_event_handler(self, card_layout: QWidget):
        """Подключает обработчик скрытия окна редактора шаблонов."""
        original_hide_event = card_layout.hideEvent

        def custom_hide_event(event):
            global focus_watcher            
            focus_watcher.activate_trigger = False
            self.update_timer.stop()                                               
            original_hide_event(event) # Вызов оригинального обработчика
        card_layout.hideEvent = custom_hide_event


    def setup_show_event_handler(self, card_layout: QWidget):
        """Подключает обработчик показа окна редактора шаблонов."""
        original_show_event = card_layout.showEvent        
        def custom_show_event(event):
            global focus_watcher            
            focus_watcher.activate_trigger = True
            self.update_timer.start()                                  
            original_show_event(event) # Вызов оригинального обработчика
        card_layout.showEvent = custom_show_event



    def sanitize_filename(self, file_name: str, keep_last_dot: bool = True) -> str:
        """
        Удаляет недопустимые символы из имени файла.
        :param file_name: Имя файла или папки.
        :param keep_last_dot: Оставлять последнюю точку (например, для расширения файла).
        :return: Очищенное имя файла.
        """
        # Удаляем недопустимые символы
        sanitized_name = re.sub(r'[\\/:*?"<>|\x00-\x1F]', '', file_name)

        # Разделяем имя и расширение, если точка присутствует
        if '.' in sanitized_name and keep_last_dot:
            parts = sanitized_name.rsplit('.', 1)  # Разделяем на имя и расширение
            parts[0] = re.sub(r'[().]', '_', parts[0])  # Заменяем () и . в имени
            parts[1] = re.sub(r'[().]', '_', parts[1])  # Заменяем () и . в расширении
            sanitized_name = '.'.join(parts)  # Собираем обратно
        else:
            # Заменяем () и . во всем имени, если точка не сохраняется
            sanitized_name = re.sub(r'[().]', '_', sanitized_name)

        # Удаляем лишние пробелы в начале и конце
        return sanitized_name.strip()
    

    def open_in_external_editor(self, edit_area: QTextEdit):
        """Сохраняет текст и позицию курсора, открывает внешний редактор."""
        global template_name

        # Устанавливаем курсор в режим "песочные часы"
        QGuiApplication.setOverrideCursor(WaitCursor)

        try:
            # Получаем текущий текст и позицию курсора
            cursor = edit_area.textCursor()
            current_position = cursor.position()
            text = edit_area.toPlainText()

            user_dir = os.path.expanduser("~")
            user_dir = os.path.join(user_dir, "anki_backup")            
            if not os.path.exists(user_dir): # Проверяем, существует ли папка и создаем ее, если она отсутствует
                os.makedirs(user_dir)  
            user_dir_model = user_dir
            if thisCardLayout.model["name"]:                 
                user_dir_model = os.path.join(user_dir, self.sanitize_filename(thisCardLayout.model["name"], False) )
                if not os.path.exists(user_dir_model): # Проверяем, существует ли папка и создаем ее, если она отсутствует
                    os.makedirs(user_dir_model)                

            if not template_name:
                template_name = "template"  # Если имя шаблона не найдено, используем значение по умолчанию

            # Определяем суффикс в зависимости от текущей кнопки
            if self.current_button == "front_button":
                suffix = "_front.html"
                str1 = "<!-- File modified by anki: %% -->"
            elif self.current_button == "back_button":
                suffix = "_back.html"
                str1 = "<!-- File modified by anki: %% -->"
            else:
                suffix = "_style.css"
                str1 = "/* File modified by anki: %% */"

            # Получаем текущее время и добавляем 3 секунды
            current_time = datetime.now() + timedelta(seconds=3)
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

            # Заменяем %% в str1 на текущее время
            str1 = str1.replace("%%", formatted_time)

            # Находим позицию первого разделителя строки
            newline_index = text.find("\n")
            # Проверяем, есть ли разделитель строки
            if newline_index != -1:
                # Извлекаем первую строку
                first_line = text[:newline_index]
                # Проверяем, содержит ли первая строка "File modified by anki:"
                if "File modified by anki:" in first_line:
                    # Удаляем первую строку из текста
                    text = text[newline_index + 1:]
                    current_position -= (len(first_line)+1)

            # Добавляем str1 в начало текста
            text = f"{str1}\n{text}"

            # Обновляем содержимое edit_area
            edit_area.setPlainText(text)

            # Восстанавливаем позицию курсора с учетом добавленной строки
            current_position += len(str1) + 1 # +1 для символа новой строки
            cursor.setPosition(current_position)
            edit_area.setTextCursor(cursor)

            # Формируем уникальное имя файла
            if suffix != "_style.css":
                file_name = f"{template_name}{suffix}"
            else:
                template_name_nocard = re.sub(r"_card\d{1,3}$", "", template_name)
                file_name = f"{template_name_nocard}{suffix}"

            file_name = self.sanitize_filename(file_name)  # Удаляем недопустимые символы
            temp_file_path = os.path.join(user_dir_model, file_name)

            # Сохраняем текст в файл
            with open(temp_file_path, "w", encoding="utf-8") as temp_file:
                temp_file.write(text)

            # Формируем команду для открытия VS Code с указанием позиции курсора
            line = text[:current_position].count("\n") + 1  # Номер строки
            column = current_position - text.rfind("\n", 0, current_position)  # Номер столбца  

            command_str = configF("GLOBAL_SETTINGS", "external_code_editor", "code.cmd -g \"{file}:{line}:{column}\"")
            formatted = command_str.format(file=temp_file_path, line=line, column=column) # подставляем значения
            command = shlex.split(formatted) # разбиваем на список аргументов (shlex учитывает кавычки, экранирование и т.д.)

            try:
                self.update_timer.stop()   
                self.update_timer.start() # таймер проверки обновления перезапустить             
                # Запускаем внешний редактор
                subprocess.Popen(command)
                tooltip(localizationF("Menu_Open1", "Please wait. Opening external code editor."))                
            except FileNotFoundError:
                tooltip(localizationF("Menu_Open2","Could not find external code editor. Make sure it is installed and available in PATH."))
            
        finally:
            # Возвращаем курсор в нормальное состояние
            QGuiApplication.restoreOverrideCursor()




    def needs_update_from_external_editor(self, edit_area: QTextEdit):
        """требуется обновить текст если файл был модифицирован"""
        global template_name, thisCardLayout

        if thisCardLayout and hasattr(thisCardLayout, "ignore_change_signals") and thisCardLayout.ignore_change_signals:
            QTimer.singleShot(150, lambda: needs_update_from_external_editor(edit_area) )
            return

        # Устанавливаем курсор в режим "песочные часы"
        QGuiApplication.setOverrideCursor(WaitCursor)

        try:            
            user_dir = os.path.expanduser("~")
            user_dir = os.path.join(user_dir, "anki_backup")            
            if not os.path.exists(user_dir): # Проверяем, существует ли папка и создаем ее, если она отсутствует
                os.makedirs(user_dir)  
            user_dir_model = user_dir
            if thisCardLayout.model["name"]: 
                user_dir_model = os.path.join(user_dir, self.sanitize_filename(thisCardLayout.model["name"], False) )
                if not os.path.exists(user_dir_model): # Проверяем, существует ли папка и создаем ее, если она отсутствует
                    os.makedirs(user_dir_model)     

            
            
            # Получаем уникальное имя файла
            if not template_name:
                template_name = "template"  # Если имя шаблона не найдено, используем значение по умолчанию

            # Определяем суффикс в зависимости от текущей кнопки
            if self.current_button == "front_button":
                suffix = "_front.html"
            elif self.current_button == "back_button":
                suffix = "_back.html"
            else:
                suffix = "_style.css"

            # Формируем имя файла
            if suffix != "_style.css":
                file_name = f"{template_name}{suffix}"
            else:
                template_name_nocard = re.sub(r"_card\d{1,3}$", "", template_name)
                file_name = f"{template_name_nocard}{suffix}"

            file_name = self.sanitize_filename(file_name)  # Удаляем недопустимые символы
            temp_file_path = os.path.join(user_dir_model, file_name)
            
            # Проверяем, существует ли файл
            if not os.path.exists(temp_file_path):
                # tooltip(localizationF("Menu_Update1","File not found. It may not have been created yet.") 
                #         + " (file: " + temp_file_path + ")"  )
                return False

            # Читаем первую строку файла
            with open(temp_file_path, "r", encoding="utf-8") as temp_file:
                first_line = temp_file.readline()
                file_content = temp_file.read()  # Остальной текст файла

            # Проверяем, содержит ли первая строка "File modified by anki:"
            if "File modified by anki:" not in first_line:
                # tooltip(localizationF("Menu_Update2","First line of file does not contain expected text."))
                return False

            text = edit_area.toPlainText()
            # Находим позицию первого разделителя строки
            newline_index = text.find("\n")
            # Проверяем, есть ли разделитель строки
            if newline_index != -1:
                # Извлекаем первую строку
                first_lineT = text[:newline_index]
            else:
                first_lineT = text
            # Проверяем, содержит ли первая строка "File modified by anki:"
            if "File modified by anki:" not in first_lineT:
                return False

            # если строки первые не равны, то уже надо обновить
            if first_lineT.strip() != first_line.strip():
                # Файл был модифицирован, так что надо сообщить об этом
                tooltip(localizationF("Menu_Update6","Update from external file [F5] or cancel by pressing save [Ctrl+S]"), parent=thisCardLayout)
                return True


            # Извлекаем время из первой строки
            try:            
                file_time_str = first_line.split("File modified by anki:")[1].strip()
                # Удаляем лишние символы после времени
                file_time_str = file_time_str.split()[0] + " " + file_time_str.split()[1]
                file_time = datetime.strptime(file_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # tooltip(localizationF("Menu_Update3","Incorrect time format in first line of file."))
                return False

            # Получаем время последней модификации файла
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(temp_file_path))

            # Сравниваем время из файла с временем модификации
            if file_mod_time > file_time:
                # Файл был модифицирован, так что надо сообщить об этом
                tooltip(localizationF("Menu_Update6","Update from external file [F5] or cancel by pressing save [Ctrl+S]"), parent=thisCardLayout)
                return True
            else:
                return False

        except Exception as e:        
            # logError(e)
            return False
        finally:
            # Возвращаем курсор в нормальное состояние
            QGuiApplication.restoreOverrideCursor()





    def check_and_update_from_external_editor(self, edit_area: QTextEdit):
        """Проверяет файл, читает время из первой строки и обновляет редактор, если файл был модифицирован."""
        global template_name

        # Устанавливаем курсор в режим "песочные часы"
        QGuiApplication.setOverrideCursor(WaitCursor)

        try:
            user_dir = os.path.expanduser("~")
            user_dir = os.path.join(user_dir, "anki_backup")            
            if not os.path.exists(user_dir): # Проверяем, существует ли папка и создаем ее, если она отсутствует
                os.makedirs(user_dir)  
            user_dir_model = user_dir
            if thisCardLayout.model["name"]: 
                user_dir_model = os.path.join(user_dir, self.sanitize_filename(thisCardLayout.model["name"], False) )
                if not os.path.exists(user_dir_model): # Проверяем, существует ли папка и создаем ее, если она отсутствует
                    os.makedirs(user_dir_model)        
            
            
            # Получаем уникальное имя файла
            if not template_name:
                template_name = "template"  # Если имя шаблона не найдено, используем значение по умолчанию

            # Определяем суффикс в зависимости от текущей кнопки
            if self.current_button == "front_button":
                suffix = "_front.html"
            elif self.current_button == "back_button":
                suffix = "_back.html"
            else:
                suffix = "_style.css"

            # Формируем имя файла            
            if suffix != "_style.css":
                file_name = f"{template_name}{suffix}"
            else:
                template_name_nocard = re.sub(r"_card\d{1,3}$", "", template_name)
                file_name = f"{template_name_nocard}{suffix}"    

            file_name = self.sanitize_filename(file_name)  # Удаляем недопустимые символы
            temp_file_path = os.path.join(user_dir_model, file_name)
            
            # Проверяем, существует ли файл
            if not os.path.exists(temp_file_path):
                tooltip(localizationF("Menu_Update1","File not found. It may not have been created yet.") 
                        + " (file: " + temp_file_path + ")"  )
                return

            # Читаем первую строку файла
            with open(temp_file_path, "r", encoding="utf-8") as temp_file:
                first_line = temp_file.readline()
                file_content = temp_file.read()  # Остальной текст файла

            # Проверяем, содержит ли первая строка "File modified by anki:"
            if "File modified by anki:" not in first_line:
                tooltip(localizationF("Menu_Update2","First line of file does not contain expected text."))
                return


            text = edit_area.toPlainText()
            # Находим позицию первого разделителя строки
            newline_index = text.find("\n")
            # Проверяем, есть ли разделитель строки
            if newline_index != -1:
                # Извлекаем первую строку
                first_lineT = text[:newline_index]
            else:
                first_lineT = text
            # Проверяем, содержит ли первая строка "File modified by anki:"
            if "File modified by anki:" not in first_lineT:
                return False


            # Извлекаем время из первой строки
            try:            
                file_time_str = first_line.split("File modified by anki:")[1].strip()
                # Удаляем лишние символы после времени
                file_time_str = file_time_str.split()[0] + " " + file_time_str.split()[1]
                file_time = datetime.strptime(file_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                tooltip(localizationF("Menu_Update3","Incorrect time format in first line of file."))
                return

            # Получаем время последней модификации файла
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(temp_file_path))

            # Сравниваем время из файла с временем модификации
            if (first_lineT.strip() != first_line.strip()) or (file_mod_time > file_time):
                # Файл был модифицирован, обновляем редактор
                cursor = edit_area.textCursor()
                saved_position = cursor.position()  # Сохраняем текущую позицию курсора

                # Сохраняем текст вокруг позиции курсора
                text_before_cursor = edit_area.toPlainText()[:saved_position][-80:]  # 80 символов до курсора
                text_after_cursor = edit_area.toPlainText()[saved_position:saved_position + 80]  # 80 символов после курсора

                old_content = edit_area.toPlainText()
                
                # заменяем время у 1 строки на текущее плюс 3 секунды
                if self.current_button == "style_button":
                    str1 = "/* File modified by anki: %% */"                
                else:                
                    str1 = "<!-- File modified by anki: %% -->"
                # Получаем текущее время и добавляем 2 секунды
                current_time = datetime.now() + timedelta(seconds=2)
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                # Заменяем %% в str1 на текущее время
                first_line = str1.replace("%%", formatted_time) + "\n"
                
                # Читаем содержимое файла temp_file_path
                with open(temp_file_path, "r", encoding="utf-8") as temp_file:
                    lines = temp_file.readlines()
                # Заменяем первую строку на first_line
                lines[0] = first_line
                # Сохраняем изменения обратно в файл temp_file_path
                with open(temp_file_path, "w", encoding="utf-8") as temp_file:
                    temp_file.writelines(lines)

                new_content = first_line + file_content
                # Обновляем содержимое редактора
                edit_area.setPlainText(new_content)

                # Восстанавливаем позицию курсора
                new_position = None

                # Ищем текст до курсора
                if text_before_cursor:
                    before_index = new_content.find(text_before_cursor)
                    if before_index != -1:
                        new_position = before_index + len(text_before_cursor)

                # Если текст до курсора не найден, ищем текст после курсора
                if new_position is None and text_after_cursor:
                    after_index = new_content.find(text_after_cursor)
                    if after_index != -1:
                        new_position = after_index

                # Если ничего не найдено, возвращаемся к сохраненной позиции
                if new_position is None:
                    new_position = saved_position

                # Устанавливаем позицию курсора
                cursor.setPosition(min(new_position, len(new_content)))
                edit_area.setTextCursor(cursor)

                tooltip(localizationF("Menu_Update4","Editor updated from external file."))
            else:
                tooltip(localizationF("Menu_Update5","File has not been modified."))

        finally:
            # Возвращаем курсор в нормальное состояние
            QGuiApplication.restoreOverrideCursor()



    def load_file_into_editor(self, edit_area: QTextEdit):
        """Открывает папку с временными файлами, позволяет выбрать файл и загружает его содержимое в редактор."""
        global template_name
        
        user_dir = os.path.expanduser("~")
        user_dir = os.path.join(user_dir, "anki_backup")            
        if not os.path.exists(user_dir): # Проверяем, существует ли папка и создаем ее, если она отсутствует
            os.makedirs(user_dir)  
        user_dir_model = user_dir
        

        # Получаем уникальное имя файла
        if not template_name:
            template_name = "template"  # Если имя шаблона не найдено, используем значение по умолчанию

        # Определяем суффикс в зависимости от текущей кнопки
        if self.current_button == "front_button":
            suffix = "_front"
        elif self.current_button == "back_button":
            suffix = "_back"
        else:
            suffix = "_style"

        # Формируем имя файла
        file_name = f"{template_name}{suffix}"
        file_name = self.sanitize_filename(file_name, False)  # Удаляем недопустимые символы       
        temp_file_path = os.path.join(user_dir_model, file_name)

        # Открываем диалог выбора файла
        if self.current_button == "style_button":           
            openTypes = "CSS Files (*.css);;All Files (*)" 
        else:
            openTypes = "HTML Files (*.html);;All Files (*)" 
                

        file_path, _ = QFileDialog.getOpenFileName(
            edit_area.window(),  # Указываем родительское окно
            localizationF("Menu_Load1","Select file to upload"), temp_file_path, openTypes)

        # Проверяем, выбрал ли пользователь файл
        if not file_path:            
            edit_area.setFocus()            
            QTimer.singleShot(250, lambda: tooltip(localizationF("Menu_Load2","No file selected.")) )
            return

        # Устанавливаем курсор в режим "песочные часы"
        QGuiApplication.setOverrideCursor(WaitCursor)
        try:            
            try:
                # Читаем содержимое выбранного файла
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()

                # Заменяем содержимое редактора
                edit_area.setPlainText(file_content)

                # Устанавливаем курсор в начало
                cursor = edit_area.textCursor()
                cursor.setPosition(0)
                edit_area.setTextCursor(cursor)

                edit_area.setFocus() 
                ltxt = localizationF("Menu_Load3","File uploaded successfully")
                QTimer.singleShot(250, lambda: tooltip(f"{ltxt}: '{file_path}'") )                
            except Exception as e:
                edit_area.setFocus() 
                ltxt = localizationF("Menu_Load4","Error uploading file")
                QTimer.singleShot(250, lambda: tooltip(f"{ltxt}: {e}") )                
                        
        finally:
            # Возвращаем курсор в нормальное состояние
            QGuiApplication.restoreOverrideCursor()
            QTimer.singleShot(150, lambda: edit_area.setFocus())



    def save_with_backup(self, edit_area: QTextEdit):
        """Сохраняет текущий текст с созданием резервной копии, если это необходимо."""
        global template_name

        user_dir = os.path.expanduser("~")
        user_dir = os.path.join(user_dir, "anki_backup")            
        if not os.path.exists(user_dir): # Проверяем, существует ли папка и создаем ее, если она отсутствует
            os.makedirs(user_dir)  
        user_dir_model = user_dir
        if thisCardLayout.model["name"]: 
            user_dir_model = os.path.join(user_dir, self.sanitize_filename(thisCardLayout.model["name"], False) )
            if not os.path.exists(user_dir_model): # Проверяем, существует ли папка и создаем ее, если она отсутствует
                os.makedirs(user_dir_model) 

        
        # Устанавливаем курсор в режим "песочные часы"
        QGuiApplication.setOverrideCursor(WaitCursor)


        try:
            # Получаем текущий текст и позицию курсора
            cursor = edit_area.textCursor()
            current_position = cursor.position()
            text = edit_area.toPlainText()

            # Проверяем, есть ли первая строка с "File modified by anki:"
            newline_index = text.find("\n")
            if newline_index != -1:
                first_line = text[:newline_index]
            else:
                first_line = text

            # Формируем имя файла
            if not template_name:
                template_name = "template"  # Если имя шаблона не найдено, используем значение по умолчанию

            # Определяем суффикс в зависимости от текущей кнопки
            if self.current_button == "front_button":
                suffix = "_front.html"
            elif self.current_button == "back_button":
                suffix = "_back.html"
            else:
                suffix = "_style.css"

            # Формируем имя основного файла
            if suffix != "_style.css":
                file_name = f"{template_name}{suffix}"
            else:
                template_name_nocard = re.sub(r"_card\d{1,3}$", "", template_name)
                file_name = f"{template_name_nocard}{suffix}"

            file_name = self.sanitize_filename(file_name)  # Удаляем недопустимые символы
            temp_file_path = os.path.join(user_dir_model, file_name)

            # Формируем имя файла backup_file
            current_time = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
            if self.current_button == "front_button":                                
                file_name = self.sanitize_filename(f"{template_name}_front {current_time}.html")
            elif self.current_button == "back_button":
                file_name = self.sanitize_filename(f"{template_name}_back {current_time}.html")
            else:
                template_name_nocard = re.sub(r"_card\d{1,3}$", "", template_name)
                file_name = self.sanitize_filename(f"{template_name_nocard}_style {current_time}.css")
            backup_file_path = os.path.join(user_dir, file_name)

            # Если первая строка содержит "File modified by anki:"
            if "File modified by anki:" in first_line:
                # Обновляем время в первой строке
                new_time = (datetime.now() + timedelta(seconds=3)).strftime("%Y-%m-%d %H:%M:%S")
                if self.current_button == "style_button":
                    str1 = "/* File modified by anki: %% */"
                else:
                    str1 = "<!-- File modified by anki: %% -->"
                str1 = str1.replace("%%", new_time)

                # Обновляем текст с новой первой строкой
                #text = f"{first_line}\n{text[newline_index + 1:]}" if newline_index != -1 else f"{first_line}\n"

                # Удаляем первую строку из текста
                text = text[newline_index + 1:]
                current_position -= (len(first_line)+1)
                # Добавляем str1 в начало текста
                text = f"{str1}\n{text}"
                # Обновляем содержимое edit_area
                edit_area.setPlainText(text)

                # Восстанавливаем позицию курсора с учетом добавленной строки
                current_position += len(str1) + 1 # +1 для символа новой строки
                cursor.setPosition(current_position)
                edit_area.setTextCursor(cursor)

                # Сохраняем файл резервной копии
                with open(backup_file_path, "w", encoding="utf-8") as backup_file:
                    backup_file.write(text)

                # Сохраняем основной файл
                with open(temp_file_path, "w", encoding="utf-8") as temp_file:
                    temp_file.write(text)
                
                ltxt1 = localizationF("Menu_Save1","Files saved")
                ltxt2 = localizationF("Menu_Save2","Backup")
                ltxt3 = localizationF("Menu_Save3","Main file")
                tooltip(f"{ltxt1}:\n{ltxt2}: {backup_file_path}\n{ltxt3}: {temp_file_path}")
            else:
                # Если первой строки с "File modified by anki:" нет, сохраняем только резервную копию
                with open(backup_file_path, "w", encoding="utf-8") as backup_file:
                    backup_file.write(text)
                ltxt = localizationF("Menu_Save4","File saved as backup")
                tooltip(f"{ltxt}: {backup_file_path}")           
        
        finally:
            # Возвращаем курсор в нормальное состояние
            QGuiApplication.restoreOverrideCursor()
        

    
    def make_new_context_menu(self, edit_area: QTextEdit):             
        context_menu = edit_area.createStandardContextMenu()        
        context_menu.addSeparator() # Добавляем разделительную линию
        # Добавляем действия 
        open_external_action = QAction(localizationF("Menu_F2", "save to file and transfer to external editor"), edit_area)
        open_external_action.setShortcut("F2")
        open_external_action.triggered.connect(lambda: self.open_in_external_editor(edit_area))
        context_menu.addAction(open_external_action)

        # Добавляем пункт меню для поиска 
        find_action = QAction(localizationF("Find","Find a substring")+"...", edit_area)  
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(lambda: findT(edit_area, mw.app.activeWindow()))
        context_menu.addAction(find_action)        

        # Добавляем пункт меню для поиска F3 
        findF3_action = QAction(localizationF("FindF3","Search next"), edit_area)        
        findF3_action.setShortcut("F3")
        findF3_action.triggered.connect(lambda: findF3T(edit_area, mw.app.activeWindow()))
        context_menu.addAction(findF3_action)

        # Добавляем пункт меню для замены 
        replace_action = QAction(localizationF("Find_and_Replace","Find and Replace")+"...", edit_area)  
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(lambda: show_find_replace_dialog(edit_area))
        context_menu.addAction(replace_action)  


        # Подсветить все как выделенное F4
        showF4_action = QAction(localizationF("Highlight_all_selected","Highlight all as selected"), edit_area)        
        showF4_action.setShortcut("F4")
        showF4_action.triggered.connect(lambda: edit_area.highlighter.rehighlight_code())
        context_menu.addAction(showF4_action)
        

        update_action = QAction(localizationF("Menu_F5","update from previously saved file"), edit_area)
        update_action.setShortcut("F5")
        update_action.triggered.connect(lambda: self.check_and_update_from_external_editor(edit_area))
        context_menu.addAction(update_action)

        save_action = QAction(localizationF("Menu_CtrlS", "save backup copy (and to file)"), edit_area)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self.save_with_backup(edit_area))
        context_menu.addAction(save_action)

        load_action = QAction(localizationF("Menu_CtrlO", "load from previously saved file"), edit_area)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(lambda: self.load_file_into_editor(edit_area))
        context_menu.addAction(load_action)
        
        # Отображаем меню
        context_menu.exec(QCursor.pos())




    def setup_context_menu(self, card_layout: CardLayout):
        # Устанавливаем пользовательское контекстное меню

        edit_areas = card_layout.findChildren(QTextEdit, 'edit_area')        
        if not edit_areas:
            return        
        edit_area = edit_areas[0]

        edit_area.setContextMenuPolicy(CustomContextMenu)        
        edit_area.customContextMenuRequested.connect(lambda: self.make_new_context_menu(edit_area))

        # Устанавливаем фильтр событий для перехвата F3, F4
        # edit_area.installEventFilter(self)

        # Добавляем обработку сочетания клавиш
        shortcut_f2 = QShortcut(QKeySequence("F2"), edit_area)
        shortcut_f2.activated.connect(lambda: self.open_in_external_editor(edit_area))
        shortcut_f3 = QShortcut(QKeySequence("F3"), edit_area)
        shortcut_f3.activated.connect(lambda: findF3T(edit_area, mw.app.activeWindow()))
        shortcut_Shiftf3 = QShortcut(QKeySequence("Shift+F3"), edit_area)
        shortcut_Shiftf3.activated.connect(lambda: findShiftF3T(edit_area, mw.app.activeWindow()))
        shortcut_f4 = QShortcut(QKeySequence("F4"), edit_area)
        shortcut_f4.activated.connect(lambda: edit_area.highlighter.rehighlight_code())
        shortcut_CtrlF = QShortcut(QKeySequence("Ctrl+F"), edit_area)
        shortcut_CtrlF.activated.connect(lambda: findT(edit_area, mw.app.activeWindow()))
        shortcut_CtrlH = QShortcut(QKeySequence("Ctrl+H"), edit_area)
        shortcut_CtrlH.activated.connect(lambda: show_find_replace_dialog(edit_area))
        shortcut_f5 = QShortcut(QKeySequence("F5"), edit_area)
        shortcut_f5.activated.connect(lambda: self.check_and_update_from_external_editor(edit_area))
        shortcut_CtrlS = QShortcut(QKeySequence("Ctrl+S"), edit_area)
        shortcut_CtrlS.activated.connect(lambda: self.save_with_backup(edit_area))
        shortcut_CtrlO = QShortcut(QKeySequence("Ctrl+O"), edit_area)
        shortcut_CtrlO.activated.connect(lambda: self.load_file_into_editor(edit_area))  
        shortcut_CtrlG = QShortcut(QKeySequence("Ctrl+G"), edit_area)
        shortcut_CtrlG.activated.connect(lambda: gotoN(edit_area, mw.app.activeWindow()))

        shortcut_CtrlF3 = QShortcut(QKeySequence("Ctrl+F3"), edit_area)
        shortcut_CtrlF3.activated.connect(lambda: CtrlF3())
        shortcut_CtrlF4 = QShortcut(QKeySequence("Ctrl+F4"), edit_area)
        shortcut_CtrlF4.activated.connect(lambda: CtrlF4())



    def update_current_completion(self, text: str):
        """Обновляет текущий выбор в списке автодополнения."""
        self.current_completion = text


    def update_completer_model(self):
        """Обновляет модель QCompleter с учетом недавно использованных элементов."""
        all_tags = self.recently_used_tags + self.html_tags + self.wordsFromEdit_Area    
        all_tags = list(dict.fromkeys(all_tags))  # Убираем дубликаты, сохраняя порядок
        self.completer.model().setStringList(all_tags)



    def setup_autocomplete(self, edit_area: QTextEdit):
        """Настраивает автодополнение для HTML-тегов."""        
        # Создаем QCompleter
        completer = QCompleter(self.html_tags, edit_area)
        if pyqt_version == "PyQt6":
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        else:
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setWidget(edit_area)

        # Устанавливаем стиль для окна автодополнения
        completer.popup().setStyleSheet("""
            QAbstractItemView {
                background-color: #2b2b2b;  /* Темный фон */
                color: #ffffff;            /* Белый текст */
                border: 1px solid #555555; /* Граница */
                selection-background-color: #444444; /* Цвет выделения */
                selection-color: #ffffff; /* Цвет текста при выделении */
            }
        """)

        # Подключаем событие завершения
        completer.activated.connect(lambda text: self.insert_autocomplete(edit_area, text))
        # Подключаем событие завершения
        completer.highlighted.connect(lambda text: self.update_current_completion(text))

        # Отслеживаем ввод текста
        edit_area.textChanged.connect(lambda: self.show_autocomplete(edit_area, completer))

        # Сохраняем completer как атрибут
        self.completer = completer


    def get_cursor_position_relative_to_text_edit(self, edit_area: QTextEdit):
        """Возвращает координаты курсора относительно верхнего левого угла QTextEdit."""
        cursor_rect = edit_area.cursorRect()  # Прямоугольник курсора
        relative_position = cursor_rect.topLeft()  # Верхний левый угол прямоугольника
        return relative_position

    def show_autocomplete(self, edit_area: QTextEdit, completer: QCompleter):
        """Показывает список автодополнения, если введен символ < aA-zZ_ и фильтрует по введенному тексту."""
        cursor = edit_area.textCursor()
        current_position = cursor.position()
        selected_text = cursor.selectedText()

        if( len(selected_text) != 0 ):
            return

        cntErr = 10000
        # Перемещаем курсор влево, пока не найдем символ начала слова или не достигнем начала текста        
        while current_position > 0:
            cursor.movePosition(QTextCursor.MoveOperation.Left, KeepAnchor)
            current_position -= 1
            selected_text = cursor.selectedText()
            # Проверяем, начинается ли выделенный текст с буквы или подчеркивания
            if selected_text and not (selected_text[0].isalnum() or selected_text[0] in "-_<%"): # not (selected_text[0].isalpha() or selected_text[0] == "_" or selected_text[0] == "<" or selected_text[0] == "%")
                while selected_text:
                    cursor.movePosition(QTextCursor.MoveOperation.Right, KeepAnchor)
                    current_position += 1
                    selected_text = cursor.selectedText()
                    if selected_text and (selected_text[0].isalpha() or selected_text[0] == "_" or selected_text[0] == "<" or selected_text[0] == "%"):
                        break
                break    
            cntErr -= 1
            if(cntErr <= 0):
                current_position = 0
                log.error("cntErr def show_autocomplete(self, edit_area: QTextEdit, completer: QCompleter):  while current_position > 0:")  # Запись в лог
                break 

        selected_text = cursor.selectedText()        
                    
        if selected_text and (selected_text[0].isalpha() or selected_text[0] == "_" or selected_text[0] == "<" or selected_text[0] == "%"):                
            completer.setCompletionPrefix(selected_text)  # Устанавливаем фильтр для автодополнения
            if completer.completionCount() > 0:  # Показываем список, если есть совпадения
                completer.complete()  # Показываем список автодополнения
                cursor_position = self.get_cursor_position_relative_to_text_edit(edit_area)
                
                popup = completer.popup()
                cursor_rect = edit_area.cursorRect()
                popup.setGeometry(edit_area.mapToGlobal(cursor_rect.bottomLeft()).x() + 40,
                    edit_area.mapToGlobal(cursor_rect.bottomLeft()).y() + 15,
                    450, # popup.sizeHint().width(),
                    popup.sizeHint().height() )
            else:
                # если показан то скрываем
                if self.completer.popup().isVisible():                    
                    # Закрываем список автодополнения
                    self.completer.popup().hide()
            return
        else:
            # если показан то скрываем
            if self.completer.popup().isVisible():                    
                # Закрываем список автодополнения
                self.completer.popup().hide()
            return

    

    def insert_autocomplete(self, edit_area: QTextEdit, text: str):
        """Вставляет выбранный тег из автодополнения, заменяя уже введенный текст."""
        cursor = edit_area.textCursor()        
        current_position = cursor.position()              

        cntErr = 10000
        # Перемещаем курсор влево, пока не найдем символ начала слова или не достигнем начала текста
        while current_position > 0:
            cursor.movePosition(QTextCursor.MoveOperation.Left, KeepAnchor)
            current_position -= 1
            selected_text = cursor.selectedText()
            # Проверяем, начинается ли выделенный текст с буквы или подчеркивания
            if selected_text and not (selected_text[0].isalnum() or selected_text[0] in "-_<%"): # not (selected_text[0].isalpha() or selected_text[0] == "_" or selected_text[0] == "<" or selected_text[0] == "%")
                while selected_text:
                    cursor.movePosition(QTextCursor.MoveOperation.Right, KeepAnchor)
                    current_position += 1
                    selected_text = cursor.selectedText()
                    if selected_text and (selected_text[0].isalpha() or selected_text[0] == "_" or selected_text[0] == "<" or selected_text[0] == "%"):
                        break
                break
            cntErr -= 1
            if(cntErr <= 0):
                current_position = 0
                log.error("cntErr def insert_autocomplete(self, edit_area: QTextEdit, text: str):  while current_position > 0:")  # Запись в лог
                break 
    

        text_before_cursor = cursor.selectedText()  
        cursor.removeSelectedText()    

        # Если текст начинается с '%', удаляем имя шаблона (до первого пробела)
        if text.startswith("%"):
            newText = text.split(" ", 1)[1]  # Удаляем имя шаблона и пробел
            textR = newText.replace("⇥", "\t")            
            textR = textR.replace("$$", self.selTextBeforeShift)
            cursor.insertText(f"{textR}") 
            # Проверяем, есть ли в тексте символы '%%'
            if "%%" in newText:
                # Находим позицию '%%'
                start_position = cursor.position() - len(textR) + textR.index("%%")
                end_position = start_position + 2  # Длина '%%' — 2 символа
                # Устанавливаем курсор на '%%' и выделяем их
                cursor.setPosition(start_position)
                cursor.setPosition(end_position, KeepAnchor)
            else:
                # Если '%%' нет, устанавливаем курсор в конец текста
                #cursor.movePosition(QTextCursor.MoveOperation.End)
                pass
            # Применяем изменения к текстовому полю
            edit_area.setTextCursor(cursor)
        else:
            textR = text.replace("⇥", "\t")
            cursor.insertText(f"{textR}") 


        # Добавляем элемент в список недавно использованных
        if text not in self.recently_used_tags:
            self.recently_used_tags.insert(0, text)  # Добавляем в начало списка
            if len(self.recently_used_tags) > 10:  # Ограничиваем размер списка
                self.recently_used_tags.pop()
        
        # Обновляем модель QCompleter
        self.update_completer_model()

        # Закрываем список автодополнения
        self.completer.popup().hide()
        return
    

    def enhance_text_edit(self, edit_area):
        self.cur_edit_area = edit_area
        edit_area.line_number_area = LineNumberArea(edit_area)
        edit_area.line_number_area_width = lambda: self.line_number_area_width(edit_area)
        edit_area.textChanged.connect(lambda: self.update_line_number_area_width(edit_area))
        edit_area.verticalScrollBar().valueChanged.connect(lambda: edit_area.line_number_area.update())        
        # пока подсветку уберем, мешает для подсветки парных {}
        #edit_area.cursorPositionChanged.connect(lambda: self.highlight_current_line(edit_area))        

        edit_area.resizeEvent = lambda event: self.custom_resize_event(edit_area, event)
        self.update_line_number_area_width(edit_area)
        # Light or dark theme =br= Tema claro ou escuro 
        edit_area.setStyleSheet("""
            QTextEdit {
                background-color: {colors["background_color"]};
                color: {colors["text_color"]};
                selection-background-color: {colors["selection_background_color"]};
                selection-color: {colors["selection_text_color"]};
            }
        """)

        # Добавляем статусную строку (QLabel)
        if not hasattr(edit_area, "status_label"):            
            status_label = QLabel()
            status_label.setStyleSheet("font-size: 10pt; color: #888; padding: 2px;")
            edit_area.status_label = status_label
            # Добавляем QLabel под редактор (или куда нужно)
            parent_layout = edit_area.parentWidget().layout()
            if parent_layout:
                parent_layout.addWidget(status_label)

        def update_status():
            try:
                cursor = edit_area.textCursor()
                block = cursor.block()
                line = block.blockNumber() + 1
                
                # try тут не поможет, необходима проверка на ignore_change_signals
                if not hasattr(thisCardLayout, "ignore_change_signals") or not thisCardLayout.ignore_change_signals:
                    col = cursor.position() - block.position() + 1
                    if cursor.hasSelection():
                        ch = cursor.selectedText()[0]
                    else:
                        ch = cursor.document().characterAt(cursor.position())

                    hex_code = f"U+{ord(ch):04X}" if ch else ""
                    unicodename = unicodedata.name(ch, "Unknown").lower()
                    len_sl = len(cursor.selectedText())
                    selLn = ""
                    if len_sl > 0:
                        selLn = f"(The first character out of {str(len_sl)} selected)"

                    status = f"Ln: {line}  Col: {col}  Sm: '{ch}'  {hex_code}  {unicodename}   {selLn}"
                    edit_area.status_label.setText(status)

            except Exception as e:
                logError(e)

        edit_area.cursorPositionChanged.connect(update_status)
        edit_area.selectionChanged.connect(update_status)
        update_status()  

        


    def line_number_area_width(self, edit_area):
        digits = len(str(max(1, edit_area.document().blockCount())))
        space = 3 + edit_area.fontMetrics().horizontalAdvance('9') * digits
        return space + 10

    def update_line_number_area_width(self, edit_area):
        edit_area.setViewportMargins(edit_area.line_number_area_width(), 0, 0, 0)
        edit_area.line_number_area.update()

    def custom_resize_event(self, edit_area, event):
        QTextEdit.resizeEvent(edit_area, event)
        cr = edit_area.contentsRect()
        edit_area.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                                    edit_area.line_number_area_width(), cr.height()))
        edit_area.line_number_area.update()

    # def highlight_current_line(self, edit_area):
    #     """подсветка текущей строки"""
    #     extra_selections = []       
    #     if not edit_area.isReadOnly():
    #         selection = QTextEdit.ExtraSelection()
    #         selection.format.setBackground(QColor(colors["current_line_color"]))
    #         selection.format.setProperty(QTextFormat.Property.FullWidthSelection if pyqt_version == "PyQt6" else QTextFormat.FullWidthSelection, True)
    #         selection.cursor = edit_area.textCursor()
    #         selection.cursor.clearSelection()
    #         extra_selections.append(selection)
    #         # extra_selections.append(edit_area.ExtraSelection())
    #     edit_area.setExtraSelections(extra_selections)


        

    def setup_formatting_buttons(self, card_layout: CardLayout):
        edit_areas = card_layout.findChildren(QTextEdit, 'edit_area')        
        if not edit_areas:
            return        
        edit_area = edit_areas[0]
        self.setup_autocomplete(edit_area)
        
        self.enhance_text_edit(edit_area)
        self.setup_context_menu(card_layout)  # Настраиваем контекстное меню

        highlighter = HtmlSyntaxHighlighter(edit_area.document())
        # edit_area.document().contentsChange.connect(lambda: highlighter.rehighlight())
        edit_area.highlighter = highlighter 
        highlighter.setup_selection_change_handler(edit_area)
        highlighter.cur_edit_area = edit_area

        
        original_key_press = edit_area.keyPressEvent
        edit_area.keyPressEvent = lambda event: self.handle_key_press(event, edit_area, original_key_press)
                
        button_B = localization["button_B"]
        button_I = localization["button_I"]
        button_U = localization["button_U"]
        button_M = localization["button_M"]
        button_D = localization["button_▼"]
        button_T = localization["button_Tc"]
        button_BC = localization["button_Bc"]
        button_BR = localization["button_Br"]        
        button_Help = localization["button_?"]  
        formatting_buttons = [
            {"text": "B", "tooltip": f"{button_B}", "tag": "b", "method": self.apply_tag, "style": "font-weight: bold;"},
            {"text": "I", "tooltip": f"{button_I}", "tag": "i", "method": self.apply_tag, "style": "font-style: italic;"},
            {"text": "U", "tooltip": f"{button_U}", "tag": "u", "method": self.apply_tag, "style": "text-decoration: underline;"},
            {"text": "M", "tooltip": f"{button_M}", "tag": "mark", "method": self.apply_tag, "style": "background-color: yellow;"},
            {"text": "▼", "tooltip": f"{button_D}", "method": self.apply_details_tag, "style": ""},
            {"text": "Tc", "tooltip": f"{button_T}", "method": self.choose_text_color, "style": "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b6b, stop:1 #ff4757); color: white;"},
            {"text": "Bc", "tooltip": f"{button_BC}", "method": self.choose_background_color, "style": "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #3742fa); color: white;"},
            {"text": "Br", "tooltip": f"{button_BR}", "method": self.insert_line_break, "style": "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2ed573, stop:1 #7bed9f); color: white;"},
            {"text": "?", "tooltip": f"{button_Help}", "method": self.show_help_dialog_hotkey, "style": ""},
        ]
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        for btn_config in formatting_buttons:
            button = QPushButton(btn_config["text"])
            button.setStyleSheet(f"""
                QPushButton {{ 
                    font-weight: bold; 
                    border: 1px solid gray; 
                    border-radius: 3px; 
                    padding: 2px 5px;
                    max-width: 40px;
                    {btn_config.get('style', '')}
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
                QPushButton:pressed {{
                    opacity: 0.6;
                }}
            """)
            button.setToolTip(btn_config["tooltip"])
            button.setAutoDefault(False)  # Отключаем автоматическую активацию по Enter
            button.setDefault(False)     # Отключаем активацию по Enter

            if 'tag' in btn_config:
                button.clicked.connect(lambda checked, 
                                    edit=edit_area, 
                                    tag=btn_config["tag"], 
                                    method=btn_config["method"]: 
                                    method(edit, tag))
            else:
                button.clicked.connect(lambda checked, 
                                    edit=edit_area, 
                                    method=btn_config["method"]: 
                                    method(edit))
            buttons_layout.addWidget(button)
        
        group_box = QGroupBox()
        group_box.setLayout(buttons_layout)
        card_layout.buttons.insertWidget(1, group_box)

        # =ru= Фильтруем только интересующие нас кнопки
        radio_buttons = card_layout.findChildren(QRadioButton)
        if radio_buttons:
            self.radio_buttons = {btn.objectName(): btn for btn in radio_buttons if btn.objectName() in ["front_button", "back_button", "style_button"]}            
            for name, button in self.radio_buttons.items():
                button.toggled.connect(lambda checked, btn_name=name: self.handle_radio_toggle(btn_name, checked))
        else:
            print("ERROR! Radio buttons not found in card_layout")

        # =ru= Подключаемся к изменению позиции курсора
        edit_area = card_layout.findChild(QTextEdit, 'edit_area')
        if edit_area:
            edit_area.cursorPositionChanged.connect(lambda: self.save_cursor_position(edit_area))

        self.current_button = "front_button"  # По умолчанию активна front_button

        # подсветка пары для выделения
        self.setup_pair_highlight(edit_area)

    

    def save_cursor_positions_to_prefs21(self):
        """Сохраняет позиции курсора в файл prefs21"""
        global gl_model_name
        try:            
            data = {}            
            # Сохраняем данные для текущей модели           
            data[gl_model_name] = {
                "cursor_positions": self.cursor_positions,
                "timestamp": time.time()  # добавляем временную метку
            }            
            mw.pm.profile[gl_model_name] = data                      
        except Exception as e:
            print(f"Oshibka_pri_sokhranenii_pozitsii_kursora {e}")


    def load_cursor_positions_from_prefs21(self, model_name=None):
        """Загружает позиции курсора из файла prefs21 для указанной или текущей модели"""
        global gl_model_name
        try:
            data = mw.pm.profile.get(model_name, [])            
            # Если имя модели не указано, используем текущую
            if model_name is None:
                model_name = gl_model_name
            
            if model_name in data:
                # Преобразуем строковые ключи обратно в целые числа
                loaded_positions = data[model_name]["cursor_positions"]
                converted_positions = {}
                
                for key, value in loaded_positions.items():
                    try:
                        # Пробуем преобразовать ключ в число
                        int_key = int(key)
                        converted_positions[int_key] = value
                    except ValueError:
                        # Если не получается, оставляем как строку
                        converted_positions[key] = value
                
                self.cursor_positions = converted_positions                
                return True
            else:                
                return False
                
        except Exception as e:
            print(f"Oshibka pri zagruzke pozitsii kursora: {e}")
            return False

    
    def save_cursor_position(self, edit_area):
        """Сохраняет текущую позицию курсора и вертикального скроллинга для активной кнопки, если edit_area имеет фокус."""
        global thisCardLayout
        if edit_area.hasFocus():
            cursor = edit_area.textCursor()
            vertical_scroll = edit_area.verticalScrollBar().value()
            # для стиля всегда сохраняем в нулевую
            if self.current_button == "style_button":
                pos_data = self.cursor_positions[0][self.current_button]
            else:
                pos_data = self.cursor_positions[thisCardLayout.ord][self.current_button]
            pos_data["cursor_position"] = cursor.selectionStart()
            pos_data["cursor_position_end"] = cursor.selectionEnd()
            pos_data["vertical_scroll"] = vertical_scroll   

            # Автоматически сохраняем в профиль при каждом изменении
            self.save_cursor_positions_to_prefs21()              


    def restore_cursor_position(self, edit_area, button_name):
        """Восстанавливает позицию курсора и вертикального скроллинга для указанной кнопки."""
        try:
            global thisCardLayout
            cursor = edit_area.textCursor()

            # Для стиля всегда используем индекс 0
            if button_name == "style_button":
                index = 0
            else:
                index = thisCardLayout.ord

            # Проверяем существование ключа
            if index not in self.cursor_positions:
                # Если ключа нет, создаем пустые значения
                self.cursor_positions[index] = {
                    "front_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0},
                    "back_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0},
                    "style_button": {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0}
                }

            position_data = self.cursor_positions[index].get(button_name, {
                "cursor_position": 0, 
                "cursor_position_end": 0, 
                "vertical_scroll": 0
            })

            # # для стиля всегда получаем из нулевой
            # if button_name == "style_button":
            #     position_data = self.cursor_positions[0].get(button_name, {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0})
            # else:
            #     print("button_name=", button_name)
            #     position_data = self.cursor_positions[thisCardLayout.ord].get(button_name, {"cursor_position": 0, "cursor_position_end": 0, "vertical_scroll": 0})
            
            cursor_position = position_data["cursor_position"]
            cursor_position_end = position_data["cursor_position_end"] 
            vertical_scroll = position_data["vertical_scroll"]
            
            QTimer.singleShot(50, lambda:cursor.setPosition(cursor_position) )
            QTimer.singleShot(75, lambda: cursor.setPosition(cursor_position_end, KeepAnchor) )     

            # Применяем изменения к текстовому полю
            QTimer.singleShot(100, lambda: edit_area.setTextCursor(cursor) )
            # Восстанавливаем вертикальный скроллинг
            QTimer.singleShot(125, lambda: edit_area.verticalScrollBar().setValue(vertical_scroll))
            # Устанавливаем фокус на текстовое поле
            QTimer.singleShot(150, lambda: edit_area.setFocus())
            self.historyN = 0
        except Exception as e:
            print(f"Oshibka_pri_vosstanovlenii_pozitsii_kursora {e}")

    

    def show_help_dialog_hotkey(self, edit_area: QTextEdit):        
        if theme_night:
            colorTag = "yellow"
        else:
            colorTag = "#0000BB"

        Hotkey = localizationF("Hotkey","Hotkey") 
        Menu_F2 = localizationF("Menu_F2","save to file and transfer to external editor") 
        Menu_CtrlF = localizationF("Menu_CtrlF", "search for a substring")
        Menu_F3 = localizationF("Menu_F3", "search next (what was previously searched for by Ctrl+F)")
        Menu_ShiftF3 = localizationF("Menu_ShiftF3", "search back (what was previously searched for by Ctrl+F)")
        Menu_Tab = localizationF("Menu_Tab", "Insert 4 spaces (and if selected, before lines)")
        Menu_LShiftTab = localizationF("Menu_LShiftTab", "delete back 4 spaces (and if selected, before lines)")
        Menu_RShiftTab = localizationF("Menu_RShiftTab", "insert a tab character (if needed in the code tag and other similar ones)")        
        Menu_Home = localizationF("Menu_Home","go to the beginning of the text, and if already there, then to the beginning of the line")
        Menu_End = localizationF("Menu_End","go to the end of the line, and if already there, then to the end of the text")
        Menu_Enter = localizationF("Menu_Enter","insert with spaces if at the beginning of the text or at the end (special cases for {}). If the autocomplete window is open, Enter and Tab enter the top one from the list")
        Menu_CtrlV = localizationF("Menu_CtrlV", "insert as text (tabs are replaced with 4 spaces)")
        Menu_CtrlShiftV = localizationF("Menu_CtrlShiftV", "insert as text (without replacing tabs)") 
        Menu_CtrlShiftInsert = localizationF("Menu_CtrlShiftInsert", "insert plain HTML (b, i, u and some others)") 
        Menu_CtrlShifAltInsert = localizationF("Menu_CtrlShifAltInsert", "insert plain HTML with color preservation") 
        Menu_F4 = localizationF("Menu_F4", "update the highlight and highlight all as selected")
        Menu_F5 = localizationF("Menu_F5","update from previously saved file")
        Menu_CtrlS = localizationF("Menu_CtrlS","save backup copy (and to file)") 
        Menu_CtrlO = localizationF("Menu_CtrlO","load from previously saved file") 
        Menu_CtrlEnter = localizationF("Menu_CtrlEnter","save and close")
        Search_forward = localizationF("Search_forward","Search forward")
        Search_back = localizationF("Search_back","Search back")
        Show_Code_completion = localizationF("Show_Code_completion","Show Code completion")
        Menu_F1 = localizationF("Menu_F1","show this window")
        Menu_CtrlH = localizationF("Menu_F1","show this window")        
        Menu_CtrlShiftTB = localizationF("Menu_CtrlShiftTB","if the selected color code is in the format #RRGGBB, then it will change only it") 
        goto = localizationF("Menu_goto","go to line with number")  
        Menu_AltLeft = localizationF("Menu_AltLeft","to the previous cursor position (where the cursor changed position with keys)")  
        Menu_AltRight = localizationF("Menu_AltRight","to the next cursor position (where the cursor changed position with keys)")          

        content = f"""<h3 style="text-align: center;">{Hotkey}</h3>
<div style="font-size: 1.5rem;">        
<br><span style="color: {colorTag};">&#60;b&#62;...&#60;/b&#62;</span> - Ctrl+B
<br><span style="color: {colorTag};">&#60;i&#62;...&#60;/i&#62;</span> - Ctrl+I
<br><span style="color: {colorTag};">&#60;u&#62;...&#60;/u&#62;</span> - Ctrl+U
<br><span style="color: {colorTag};">&#60;mark&#62;...&#60;/mark&#62;</span> - Ctrl+M
<br><span style="color: {colorTag};">&#60;details&#62;...&#60;/details&#62;</span> - Ctrl+Shift+D
<br><span style="color: {colorTag};">&#60;span style="color:  &#62;...&#60;/span&#62;</span> - Ctrl+Shift+T
<br><span style="color: {colorTag};">&#60;span style="background-color:  &#62;...&#60;/span&#62;</span> - Ctrl+Shift+B
<br><span style="color: {colorTag};">&#60;br&#62;</span> - Shift+Enter
<br><span style="color: {colorTag};">&#60;blockquote&#62;...&#60;/blockquote&#62;</span> - Ctrl+Q
<br><span style="color: {colorTag};">&#60;sub&#62;...&#60;/sub&#62;</span> - Ctrl+=
<br><span style="color: {colorTag};">&#60;sup&#62;...&#60;/sup&#62;</span> - Ctrl+Shift+=
<br><span style="color: {colorTag};">&#60;h1&#62;...&#60;/h1&#62;</span> - Ctrl+Shift+1 (+!)
<br><span style="color: {colorTag};">&#60;h2&#62;...&#60;/h2&#62;</span> - Ctrl+Shift+2 (+@)
<br><span style="color: {colorTag};">&#60;h3&#62;...&#60;/h3&#62;</span> - Ctrl+Shift+3 (+#)
<br><span style="color: {colorTag};">&#60;h4&#62;...&#60;/h4&#62;</span> - Ctrl+Shift+4 (+$)
<br><span style="color: {colorTag};">&#60;h5&#62;...&#60;/h5&#62;</span> - Ctrl+Shift+5 (+%)
<br><span style="color: {colorTag};">&#60;h6&#62;...&#60;/h6&#62;</span> - Ctrl+Shift+6 (+^)
<br><span style="color: {colorTag};">&#60;p&#62;...&#60;/p&#62;</span> - Ctrl+Shift+7 (+&)
<br><span style="color: {colorTag};">&#60;div&#62;...&#60;/div&#62;</span> - Ctrl+Shift+8 (+*)
<br><span style="color: {colorTag};">&#60;!-- ... --&#62;</span> - Ctrl+/
<br><span style="color: {colorTag};">/* ... */</span> - Ctrl+Shift+/
<br><span style="color: {colorTag};">&amp;nbsp;</span> - Ctrl+Shift+Space

<br>F1 — {Menu_F1}
<br>Alt+0 — {Menu_F1}
<br>Tab — {Menu_Tab}
<br>RShift+Tab — {Menu_RShiftTab}
<br>LShift+Tab — {Menu_LShiftTab}
<br>Ctrl+Tab — {Search_forward} %%
<br>Ctrl+Shift+Tab — {Search_back} %%
<br>Ctrl+Space — {Show_Code_completion}
<br>F2 — {Menu_F2}
<br>F4 — {Menu_F4}
<br>F5 — {Menu_F5}
<br>Ctrl+F — {Menu_CtrlF}
<br>F3 — {Menu_F3}
<br>Shift+F3 — {Menu_ShiftF3}
<br>Ctrl+H — {Menu_CtrlH}
<br>Ctrl+G — {goto}
<br>Ctrl+S — {Menu_CtrlS}
<br>Ctrl+O — {Menu_CtrlO}   
<br>Ctrl+V — {Menu_CtrlV}
<br>Ctrl+Shift+V — {Menu_CtrlShiftV}
<br>Ctrl+Shift+Insert — {Menu_CtrlShiftInsert}
<br>Ctrl+Shift+Alt+Insert — {Menu_CtrlShifAltInsert}
<br>Home — {Menu_Home}
<br>End — {Menu_End} 
<br>Enter — {Menu_Enter} 
<br>Ctrl+Enter — {Menu_CtrlEnter} 
<br>Ctrl+Shift+T or Ctrl+Shift+B — {Menu_CtrlShiftTB}
<br>Alt+Left — {Menu_AltLeft}
<br>Alt+Right — {Menu_AltRight}
</div>
"""
        show_text_dialog(f"{Hotkey}", content, True)

    def toggle_wrapping_by_tags(self, edit_area, cursor, prefix, suffix, add_space=False):
        """Оборачиваем тегами или удаляем, сохраняя выделение"""
        if not cursor.hasSelection():
            return
                
        doc = edit_area.document()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        selTxt = cursor.selectedText()        

        # Поиск влево (ищем prefix с учётом пробелов)
        left_pos = start       
        while left_pos >= len(prefix):
            snippet = ''.join(doc.characterAt(left_pos - i - 1) for i in range(len(prefix)))[::-1]
            if snippet == prefix:
                break
            if doc.characterAt(left_pos - 1).isspace():
                left_pos -= 1
            else:
                left_pos = -1
                break

        # Поиск вправо (ищем suffix с учётом пробелов)
        right_pos = end        
        while right_pos + len(suffix) < doc.characterCount():
            snippet = ''.join(doc.characterAt(right_pos + i) for i in range(len(suffix)))
            if snippet == suffix:
                break
            if doc.characterAt(right_pos).isspace():
                right_pos += 1
            else:
                right_pos = -1
                break

        if left_pos != -1 and right_pos != -1:            
            # Уже обёрнуто — удаляем prefix + suffix
            cursor.setPosition(left_pos - len(prefix))
            cursor.setPosition(right_pos + len(suffix), KeepAnchor)
            cursor.insertText(selTxt)
            lenSelTxt = len(selTxt)            
            # Перемещение курсора на длину вставленного текста назад
            cursor.setPosition(left_pos - len(prefix))
            cursor.setPosition(left_pos - len(prefix) + lenSelTxt, KeepAnchor)
        else:
            # Оборачиваем
            cursor.setPosition(start)
            cursor.setPosition(end, KeepAnchor)
            selected = cursor.selectedText().replace('\u2029', '\n')
            lenPref = len(prefix) 
            if add_space:
                wrapped = f'{prefix} {selected} {suffix}'
                lenPref += 1                
            else:
                wrapped = f'{prefix}{selected}{suffix}'

            cursor.insertText(wrapped)            
            # Восстанавливаем выделение
            cursor.setPosition(start + lenPref)
            cursor.setPosition(start + lenPref + len(selected), KeepAnchor)

        edit_area.setTextCursor(cursor)



    def find_and_select_double_percent(self, edit_area: QTextEdit, forward=True):
        """Ищет подстроку '%%' начиная с текущей позиции курсора и выделяет ее.        
        forward - Направление поиска вперед или нет
        """
        cursor = edit_area.textCursor()
        current_position = cursor.position()
        text = edit_area.toPlainText()

        if forward:
            # Получаем текст от текущей позиции до конца документа
            text_after_cursor = text[current_position:]
            # Ищем подстроку '%%'
            index = text_after_cursor.find("%%")
            if index != -1:
                # Если '%%' найдено, перемещаем курсор и выделяем подстроку
                start_position = current_position + index
                end_position = start_position + 2  # Длина '%%' — 2 символа
                cursor.setPosition(start_position)
                cursor.setPosition(end_position, KeepAnchor)
                edit_area.setTextCursor(cursor)
            else: # если не найдено, то в начало и поиск оттуда
                if current_position > 0:
                    current_position = 0
                    text_after_cursor = text[current_position:]
                    # Ищем подстроку '%%'
                    index = text_after_cursor.find("%%")
                    if index != -1:
                        # Если '%%' найдено, перемещаем курсор и выделяем подстроку
                        start_position = current_position + index
                        end_position = start_position + 2  # Длина '%%' — 2 символа
                        cursor.setPosition(start_position)
                        cursor.setPosition(end_position, KeepAnchor)
                        edit_area.setTextCursor(cursor)
        else:
            # Получаем текст от начала документа до текущей позиции
            text_before_cursor = text[:current_position-2]            
            # Ищем последнее вхождение подстроки '%%'
            index = text_before_cursor.rfind("%%")            
            if index != -1:
                # Если '%%' найдено, перемещаем курсор и выделяем подстроку
                start_position = index
                end_position = start_position + 2  # Длина '%%' — 2 символа
                cursor.setPosition(start_position)
                cursor.setPosition(end_position, KeepAnchor)
                edit_area.setTextCursor(cursor)
        # Если '%%' не найдено, ничего не делаем


    def simplify_html_from_clipboard(self, edit_area, save_color = False):
        """получить простой HTML из буфера обмена"""
        clipboard = QGuiApplication.clipboard()
        md = clipboard.mimeData()
        html = md.html()
        if not html:    
            paste_without_tab_replace = True
            edit_area.paste()
            paste_without_tab_replace = False       
            return

        soup = BeautifulSoup(html, "html.parser")        
        html_str = str(soup)    
        #html_str = re.sub(r'(?<!>)\n(?!<)', ' ', html_str) # избавляемся от \n лишних (из word) заменяя на пробел
        html_str = re.sub(r'\n', ' ', html_str) # избавляемся от \n лишних (из word) заменяя на пробел
        html_str = html_str.replace("&lt;!--", "<!--").replace("--&gt;", "-->")              
        # Затем удаляем всё между <!-- и -->
        html_str = re.sub(r'<!--.*?-->', '', html_str, flags=re.DOTALL)
        
        soup = BeautifulSoup(html_str, "html.parser")

        # Разрешённые теги и их замены
        allowed_tags = {
            "b": "b", "strong": "b",
            "i": "i", "em": "i",
            "u": "u",
            "span": "span",
            "div": "div",
            "p": "p",
            "mark": "mark",
            "sub": "sub",
            "sup": "sup",
            "blockquote": "blockquote",
            "br": "br",
            "h1": "h1",
            "h2": "h2",
            "h3": "h3",
            "h4": "h4",
            "h5": "h5",
            "h6": "h6",
            "pre": "pre",
            "code": "code",
            "samp": "samp",
            "kbd": "kbd"            
        }
        # Очистить всё лишнее
        for tag in soup.find_all(True):
            if tag.name in allowed_tags:
                tag.name = allowed_tags[tag.name]
                if tag.name == "span" and save_color:
                    # Оставляем только color и background-color в style
                    style = tag.get("style", "")
                    # Извлекаем только нужные свойства
                    allowed_styles = []
                    for part in style.split(";"):
                        part = part.strip()
                        if part.startswith("color:") or part.startswith("background-color:") or part.startswith("background:"):
                            allowed_styles.append(part)
                    # Собираем обратно строку style
                    if allowed_styles:
                        tag.attrs = {"style": "; ".join(allowed_styles)}
                    else:
                        tag.attrs = {}
                else:
                    tag.attrs = {}  # удалить все атрибуты
            else:
                tag.unwrap()  # удалить тег, сохранить текст

        simplified = str(soup) # Получить упрощённый HTML
        simplified = simplified.replace("\u00A0", "&nbsp;")  
        # Перед <p> добавить \n, если перед ним нет перевода строки
        simplified = re.sub(r'(?<!\n)<p\b', r'\n<p', simplified)
        # После </p> добавить \n, если после него нет перевода строки
        simplified = re.sub(r'</p>(?!\n)', r'</p>\n', simplified)
        simplified = re.sub(r'(</b><b>)|(</i><i>)|(</u><u>)', '', simplified, flags=re.DOTALL)
        simplified = re.sub(r'(</b></i><i><b>)|(</i></b><b><i>)', '', simplified, flags=re.DOTALL)
        simplified = simplified.strip()
        cursor = edit_area.textCursor() # Вставляем измененный текст
        cursor.insertText(simplified)
        return



    def handle_enter_with_indent(self, edit_area):
        """особый алгоритм нажатия ENTER"""
        try:
            cursor = edit_area.textCursor()
            doc = edit_area.document()
            block = cursor.block()
            text = block.text()
            pos_in_block = cursor.position() - block.position()

            # Получаем ведущие пробелы/табуляции
            import re
            m = re.match(r'^([ \t]*)', text)
            leading_ws = m.group(1) if m else ""

            # Проверяем, стоит ли курсор перед первым непробельным символом
            first_non_ws = len(leading_ws)
            is_before_first_non_ws = pos_in_block == first_non_ws

            # Проверяем, стоит ли курсор в самом конце строки
            is_at_end = pos_in_block == len(text)
            # перед концом, а в конце символ }
            is_at_end1 = False
            if pos_in_block == len(text)-1:
                after = text[:pos_in_block+1].rstrip() 
                is_at_end1 = after.endswith('}')

            # Если курсор перед первым непробельным символом
            if is_before_first_non_ws:
                #edit_area.insertPlainText('\n' + leading_ws)                
                cursor = edit_area.textCursor()
                cursor.insertText('\n' + leading_ws)
                return True  # обработали Enter

            # Если перед курсором есть непробельный символ (тот, что видим пользователю)
            # а далее идут до конча строки пробельные символы (зрительно пользователь не видит их)
            # то необходимо все символы до конца удалить                 
            if pos_in_block > 0 and not text[pos_in_block-1].isspace():
                after_cursor = text[pos_in_block:]
                if after_cursor.strip() == "":
                    # Удаляем все пробелы/табуляции после курсора до конца строки
                    cursor.setPosition(block.position() + pos_in_block)
                    cursor.setPosition(block.position() + len(text), KeepAnchor)
                    cursor.removeSelectedText()                    
                    is_at_end = True # Теперь считаем, что курсор в конце строки

            # Если курсор в конце строки (или в конце между {})
            if is_at_end or is_at_end1:
                # Проверяем, есть ли перед курсором символ {
                before = text[:pos_in_block].rstrip()
                has_brace = before.endswith('{')                

                # Считаем длину отступа в "пробелах"
                ws_len = 0
                first_char = leading_ws[0] if leading_ws else ' '
                for ch in leading_ws:
                    ws_len += 4 if ch == '\t' else 1

                if has_brace:
                    # Увеличиваем отступ до ближайшего большего, кратного 4, плюс ещё 4
                    ws_len = ((ws_len // 4) + 1) * 4
                # Формируем новый отступ
                if first_char == '\t':
                    new_ws = '\t' * (ws_len // 4)
                else:
                    new_ws = ' ' * ws_len

                #edit_area.insertPlainText('\n' + new_ws)                
                cursor = edit_area.textCursor()
                if has_brace and is_at_end1: # случай когда в конце между {}
                    cursor.insertText('\n' + new_ws + '\n' + leading_ws)                                         
                    cursor.setPosition( cursor.position() - len(leading_ws) - 1 )
                    edit_area.setTextCursor(cursor)
                else:
                    cursor.insertText('\n' + new_ws)
                return True  # обработали Enter

            # В остальных случаях — стандартное поведение
            return False
            
        finally:
            pass

      

    def handle_home_key(self, edit_area, shift_press):
        cursor = edit_area.textCursor()
        block = cursor.block()
        text = block.text()
        pos_in_block = cursor.position() - block.position()

        # Получаем ведущие пробелы/табуляции
        import re
        m = re.match(r'^([ \t]*)', text)
        leading_ws = m.group(1) if m else ""
        first_non_ws = len(leading_ws)

        # Определяем якорь выделения (при зажатом Shift)
        if cursor.hasSelection() and shift_press:
            anchor = cursor.anchor()  # Сохраняем начальную позицию выделения
        else:
            anchor = cursor.position()  # Нет выделения - якорь на текущей позиции

        # Целевая позиция курсора
        if pos_in_block == first_non_ws and pos_in_block != 0:
            target_pos = block.position()  # Переход в начало строки
        elif pos_in_block != first_non_ws:
            target_pos = block.position() + first_non_ws  # Переход к первому непробельному
        else:
            target_pos = cursor.position()  # Уже в нужной позиции

        # Если есть модификатор Shift - создаем/расширяем выделение
        if shift_press:
            # Создаем выделение от якоря до целевой позиции
            new_cursor = QTextCursor(cursor)
            new_cursor.setPosition(anchor)
            new_cursor.setPosition(target_pos, KeepAnchor)
            edit_area.setTextCursor(new_cursor)
        else:
            # Без Shift - просто перемещаем курсор
            cursor.setPosition(target_pos)
            edit_area.setTextCursor(cursor)
        
        return True
    


    def handle_end_key(self, edit_area, shift_press):
        cursor = edit_area.textCursor()
        block = cursor.block()
        text = block.text()
        pos_in_block = cursor.position() - block.position()
        
        # Определяем якорь выделения (при зажатом Shift)
        if cursor.hasSelection() and shift_press:
            anchor = cursor.anchor()  # Сохраняем начальную позицию выделения
        else:
            anchor = cursor.position()  # Нет выделения - якорь на текущей позиции

        stripped_text = text.rstrip()
        last_non_ws = len(stripped_text)
        
        # Определяем целевую позицию
        if pos_in_block != len(text):
            target_pos = block.position() + len(text)  # Конец строки
        elif last_non_ws > 0 and pos_in_block != last_non_ws:
            target_pos = block.position() + last_non_ws  # После последнего непробельного
        else:
            target_pos = cursor.position()  # Уже в нужной позиции

        # Если есть модификатор Shift - создаем/расширяем выделение
        if shift_press:
            new_cursor = QTextCursor(cursor)
            new_cursor.setPosition(anchor)
            new_cursor.setPosition(target_pos, KeepAnchor)
            edit_area.setTextCursor(new_cursor)
        else:
            cursor.setPosition(target_pos)
            edit_area.setTextCursor(cursor)
        
        return True


    def save_unique_position_history(self, edit_area):
        """
        Сохраняет в историю текущую позицию курсора и вертикального скроллинга для активной кнопки, если edit_area имеет фокус.
        Если такая позиция cursor_position уже есть (с допуском от cursor_position-600 до cursor_position+600), то перемещает в 0 позиции эту запись и меняет уже в ней.
        Если такой позиции с учетом допуска нет, то делает как для save_new_position_history.
        """
        global thisCardLayout
        if not edit_area.hasFocus():
            return

        cursor = edit_area.textCursor()
        vertical_scroll = edit_area.verticalScrollBar().value()
        cur_pos = cursor.selectionStart()
        cur_pos_end = cursor.selectionEnd()
        # для стиля всегда в нулевой хранится
        if self.current_button == "style_button":
            history = self.cursor_positions[0][self.current_button]["position_history"]
        else:
            history = self.cursor_positions[thisCardLayout.ord][self.current_button]["position_history"]

        # Поиск похожей позиции в истории (с допуском ±400)
        found_idx = None
        for idx, entry in enumerate(history):
            if abs(entry["cursor_position"] - cur_pos) <= 400:
                found_idx = idx
                break

        new_entry = {
            "cursor_position": cur_pos,
            "cursor_position_end": cur_pos_end,
            "vertical_scroll": vertical_scroll
        }

        if found_idx is not None:
            # Перемещаем найденную запись в начало и обновляем её
            history.pop(found_idx)
            history.insert(0, new_entry)
        else:
            # Сдвигаем историю вниз и добавляем новую запись в начало
            history.pop(-1)
            history.insert(0, new_entry)


    def restore_position_history(self, edit_area, n):
        """Восстанавливает позицию курсора из истории, где n есть номер сохранения от 0 и до 6"""
        global thisCardLayout
        cursor = edit_area.textCursor()

        # для стиля всегда получаем из нулевой
        if self.current_button == "style_button":
            history = self.cursor_positions[0][self.current_button]["position_history"]
        else:
            history = self.cursor_positions[thisCardLayout.ord][self.current_button]["position_history"]
                 
        position_data = history[n]

        cursor_position = position_data["cursor_position"]
        cursor_position_end = position_data["cursor_position_end"] 
        vertical_scroll = position_data["vertical_scroll"]
        
        QTimer.singleShot(40, lambda:cursor.setPosition(cursor_position) )
        QTimer.singleShot(60, lambda: cursor.setPosition(cursor_position_end, KeepAnchor) )     

        # Применяем изменения к текстовому полю
        QTimer.singleShot(70, lambda: edit_area.setTextCursor(cursor) )
        # Восстанавливаем вертикальный скроллинг
        QTimer.singleShot(85, lambda: edit_area.verticalScrollBar().setValue(vertical_scroll))
        # Устанавливаем фокус на текстовое поле
        QTimer.singleShot(100, lambda: edit_area.setFocus())



             
            
            
    def handle_key_press(self, event, edit_area, original_key_press):     
        cursor = edit_area.textCursor()
        position = cursor.position()        
        
        key = event.key()
        scan_code = event.nativeScanCode()
        # print("scan_code", scan_code)
        modifiers = event.modifiers()
        Ctrl = bool(modifiers & (ControlModifier | MetaModifier))
        Shift = bool(modifiers & ShiftModifier)
        Alt = bool(modifiers & AltModifier)    
        # print("Alt", Alt, "Ctrl", Ctrl, "Shift", Shift)    
        if event.nativeScanCode() == 54:      
            self.RShift = True # если нажат именно правый Shift
        if event.nativeScanCode() == 42 or not Shift:
            self.RShift = False # если нажат именно правый Shift

        if scan_code == 331 and Alt and not Ctrl and not Shift: # scan_code == 331 KEY_LEFT
            if self.historyN < 6:
                self.historyN += 1
            else:
                self.historyN = 6            
            self.restore_position_history(edit_area, self.historyN)
            return
        
        if scan_code == 333 and Alt and not Ctrl and not Shift: # scan_code == 333 KEY_RIGHT            
            if self.historyN > 0:
                self.historyN -= 1
            else:
                self.historyN = 0            
            self.restore_position_history(edit_area, self.historyN)
            return
            
        if not Alt and not Ctrl:     
            self.historyN = 0
            block = cursor.block()
            line = block.blockNumber() + 1
            self.save_unique_position_history(edit_area)
            # # если номер существенно меняется (>=10 то запомним как новую позицию, а иначе запоминаем как есть)
            # if abs(line - self.lineN) >= 10 and self.lineN >= 0:
            #     self.save_new_position_history(edit_area)
            # else:
            #     self.save_position_history(edit_area)
            # self.lineN = line # номер текущей строки

        
        self.delayed_pair_highlight(edit_area)

        # вставка текста с преобразование в жирное, курсив, подчеркивание        
        if scan_code == 338 and Ctrl and Shift: # scan_code == 338 KEY_INSERT            
            if Alt:
                self.simplify_html_from_clipboard(edit_area, True) # вставка текста из буфера обмена с сохранением цвета
            else:
                self.simplify_html_from_clipboard(edit_area)
            return


        if not Ctrl and not Alt and Shift:
            if key == Key_Return:
                cursor = edit_area.textCursor()
                cursor.insertText('<br>')
                return  

        if Ctrl and not Alt and Shift:
            if key == Key_Space:
                cursor = edit_area.textCursor()
                cursor.insertText('&nbsp;')
                return  
            

        if Shift and not Ctrl and not Alt and (key ==  Key_Percent or scan_code == 6):            
            self.selTextBeforeShift = cursor.selectedText() # выделенный текст до нажатия Shift+5 или просто %

        # поиск %% если он будет
        if Ctrl and not Alt and key in (Key_Tab, Key_Backtab):
            if not Shift:
                self.find_and_select_double_percent( edit_area )
                return
            else: # иначе с Shift поиск назад   
                self.find_and_select_double_percent( edit_area, False )
                return
                
        if Ctrl and not Shift and not Alt and key == Key_Space:

            # пересчитаем список атодополнения по всем словам из текста            
            text = edit_area.toPlainText()
            pattern = r'(?<!</)(?<!<)\b[a-zA-Z_-][0-9a-zA-Z_-]*\b'
            self.wordsFromEdit_Area = re.findall(pattern, text)
            self.update_completer_model()

            # Показываем окно автодополнения 
            #self.show_autocomplete(edit_area, self.completer) - делаем показ без фильтра ниже
            self.completer.setCompletionPrefix("")  # Устанавливаем фильтр для автодополнения
            if self.completer.completionCount() > 0:  # Показываем список, если есть совпадения
                self.completer.complete()  # Показываем список автодополнения
                cursor_position = self.get_cursor_position_relative_to_text_edit(edit_area)                
                popup = self.completer.popup()
                cursor_rect = edit_area.cursorRect()
                popup.setGeometry(edit_area.mapToGlobal(cursor_rect.bottomLeft()).x() + 40,
                    edit_area.mapToGlobal(cursor_rect.bottomLeft()).y() + 15,
                    popup.sizeHint().width(),
                    popup.sizeHint().height())
            return

        # Проверяем, активен ли список автодополнения
        if self.completer.popup().isVisible():
            if key in (Key_Enter, Key_Return) or (key == Key_Tab):
                # Получаем выбранный элемент, если не выбран — берем верхний
                idx = self.completer.popup().currentIndex()
                if not idx.isValid():
                    # Если ничего не выбрано, выбираем верхний элемент
                    idx = self.completer.popup().model().index(0, 0)
                text = idx.data()
                self.completer.popup().hide()
                self.insert_autocomplete(edit_area, text)
                return          
            elif key == Key_Escape:
                # Закрываем список автодополнения
                self.completer.popup().hide()
                return
            elif key in (Key_Up, Key_Down):
                # Передаем управление списку автодополнения
                self.completer.popup().event(event)
                return
            
        
            
        
        global paste_without_tab_replace
        # вставка текста (особая, так как стандартная будет заменять Tab на 4 пробела)
        if key == Key_V and Ctrl and Shift and not Alt:   
            paste_without_tab_replace = True
            edit_area.paste()
            paste_without_tab_replace = False
            return
        
        if not Ctrl and not Alt and not Shift and key == Key_Return:                                  
            if self.handle_enter_with_indent(edit_area):
                original_key_press = 0
                return            

        if not Ctrl and not Alt and key == Key_Home:
            self.handle_home_key(edit_area, Shift)
            return
        
        if not Ctrl and not Alt and key == Key_End:
            self.handle_end_key(edit_area, Shift)
            return
        
        if not Ctrl and not Alt and not Shift:
            if key == Key_F1: 
                self.show_help_dialog_hotkey(edit_area)
                return
            
        if not Ctrl and not Alt:
            if  key in (Key_Tab, Key_Backtab):
                cursor = edit_area.textCursor()
                if not cursor.hasSelection(): # Если нет выделения                         
                    if not Shift: # просто добавляем 4 пробела
                        cursor.insertText('    ')
                    elif not self.RShift: # с левым шифтом удаление назад                              
                        block = cursor.block()
                        line_text = block.text()
                        pos_in_line = cursor.position() - block.position()        
                        selN = min(pos_in_line, 4)
                        cursor.setPosition(cursor.position() - selN, KeepAnchor)
                        selected = cursor.selectedText()                        
                        if "\t" in selected: # Если есть табуляция, заменяем её на 4 пробела 
                            replacement = selected.replace("\t", "    ") # Заменяем все табуляции на пробелы
                            cursor.insertText(replacement)
                            pos_in_line = cursor.position() - block.position()        
                            selN = min(pos_in_line, 4)
                            cursor.setPosition(cursor.position() - selN, KeepAnchor)
                            selected = cursor.selectedText()
                        # если выделение пустое, то просто удаляем его
                        if selected.strip() == "":
                            cursor.removeSelectedText()
                        else:
                            cursor.clearSelection()
                    else: # а с RShift вставка обычной табуляции                                                
                        cursor.insertText('\t')                        
                    return                

                # Получаем выделенный текст
                selection_start = cursor.selectionStart()
                selection_end = cursor.selectionEnd()
                # Устанавливаем курсор в начало выделения
                cursor.setPosition(selection_start)
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                start_block = cursor.blockNumber()
                # Устанавливаем курсор в конец выделения
                cursor.setPosition(selection_end)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                end_block = cursor.blockNumber()

                cursor.beginEditBlock()  # Начинаем групповое редактирование
                try:
                    # Устанавливаем курсор на начало первого блока
                    cursor.setPosition(selection_start)
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)

                    if not Shift:
                        # Добавляем 4 пробела перед каждой строкой
                        for block_number in range(start_block, end_block + 1):
                            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                            cursor.insertText('    ')
                            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
                    else:
                        # Удаляем до 4 пробелов перед каждой строкой
                        for block_number in range(start_block, end_block + 1):
                            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)  # Перемещаемся в начало строки
                            while cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, KeepAnchor):
                                if "\t" in cursor.selectedText(): # Если выделенный текст содержит табуляцию, заменяем её на 4 пробела
                                    # Заменяем табуляцию на 4 пробела
                                    replacement = cursor.selectedText().replace("\t", "    ")
                                    cursor.insertText(replacement)
                                    # Обновляем выделение, чтобы включить новые пробелы
                                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                                    cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, KeepAnchor, len(replacement))
                                if not cursor.selectedText().isspace() and "\t" not in cursor.selectedText():  # Проверяем, что символ не пробел и не табуляция
                                    cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, KeepAnchor)  # Возвращаемся на один символ назад
                                    break
                            # Удаляем выделенные пробелы
                            if cursor.selectedText().isspace():
                                if len(cursor.selectedText()) > 4:
                                    # Если пробелов больше 4, удаляем только 4
                                    cursor.setPosition(cursor.position() - len(cursor.selectedText()) + 4, KeepAnchor)
                                cursor.removeSelectedText()
                            


                            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
                finally:
                    cursor.endEditBlock()  # Завершаем групповое редактирование
                return   

        if not Ctrl and Alt and not Shift:
            if key == Key_0 or scan_code == 11: 
                self.show_help_dialog_hotkey(edit_area)
                return
                 

        if Ctrl:
            if not Shift and not Alt:                
                if key == Key_Slash or scan_code == 53:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<!--", "-->", True)
                    return
                if key == Key_B:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<b>", "</b>", False)                    
                    return
                if key == Key_I:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<i>", "</i>", False)
                    return
                if key == Key_U:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<u>", "</u>", False)
                    return     
                if key == Key_K:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<a href=\"\">", "</a>", False)
                    return    
                if key == Key_M:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<mark>", "</mark>", False)
                    return
                if key == Key_Q:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<blockquote>", "</blockquote>", False)
                    return 
                if key == Key_Equal or scan_code == 13:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<sub>", "</sub>", False)
                    return

            if Shift and not Alt:
                if key == Key_Slash or scan_code == 53:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "/*", "*/", True)
                    return
                if key == Key_Plus or scan_code == 13:
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<sup>", "</sup>", False)
                    return
                
                if key == Key_Exclam or scan_code == 2: # 1                    
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<h1>", "</h1>", False)
                    return 
                if key == Key_At or scan_code == 3: # 2
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<h2>", "</h2>", False)
                    return
                if key == Key_NumberSign or scan_code == 4: # 3
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<h3>", "</h3>", False)
                    return
                if key == Key_Dollar or scan_code == 5: # 4
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<h4>", "</h4>", False)
                    return
                if key == Key_Percent or scan_code == 6: # 5
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<h5>", "</h5>", False)
                    return
                if key == Key_AsciiCircum or scan_code == 7: # 6
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<h6>", "</h6>", False)
                    return      
                if key == Key_Ampersand or scan_code == 8: # 7
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<p>", "</p>", False)
                    return 
                if key == Key_Asterisk or scan_code == 9: # 8
                    self.toggle_wrapping_by_tags(edit_area, cursor, "<div>", "</div>", False)
                    return 

                
                if key == Key_D:
                    self.apply_details_tag(edit_area)
                    return
                if key == Key_T:
                    self.choose_text_color(edit_area)
                    return
                if key == Key_B:
                    self.choose_background_color(edit_area)
                    return

              

        if not auto_insert:
            original_key_press(event)
            return
        
        if key == Key_BraceLeft:
            original_key_press(event)
            cursor.insertText("}")
            cursor.setPosition(position + 1)
            edit_area.setTextCursor(cursor)
            return
        elif key == Key_BracketLeft:
            original_key_press(event)
            cursor.insertText("]")
            cursor.setPosition(position + 1)
            edit_area.setTextCursor(cursor)
            return
        elif key == Key_ParenLeft:
            original_key_press(event)
            cursor.insertText(")")
            cursor.setPosition(position + 1)
            edit_area.setTextCursor(cursor)
            return
        elif key == Key_QuoteDbl:
            original_key_press(event)
            cursor.insertText("\"")
            cursor.setPosition(position + 1)
            edit_area.setTextCursor(cursor)
            return
        elif key == Key_Apostrophe:
            original_key_press(event)
            cursor.insertText("'")
            cursor.setPosition(position + 1)
            edit_area.setTextCursor(cursor)
            return
    
        if key == Key_Minus:
            original_key_press(event)
            cursor.setPosition(position + 1)
            cursor.movePosition(QTextCursor.MoveOperation.Left, KeepAnchor, 4)
            text_before = cursor.selectedText()
            if text_before == "<!--":
                cursor.setPosition(position + 1)
                cursor.insertText("  -->")
                cursor.setPosition(position + 2)
                edit_area.setTextCursor(cursor)
            return
    
        if key == Key_Asterisk:
            original_key_press(event)
            cursor.setPosition(position + 1)
            cursor.movePosition(QTextCursor.MoveOperation.Left, KeepAnchor, 2)
            text_before = cursor.selectedText()
            if text_before == "/*":
                cursor.setPosition(position + 1)
                cursor.insertText("  */")
                cursor.setPosition(position + 2)
                edit_area.setTextCursor(cursor)
            return
       
    
        if key == Key_Greater:
            original_key_press(event)
            cursor.setPosition(position+1)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, KeepAnchor)
            text_before = cursor.selectedText().rstrip()
    
            for no_close_tag in self.no_close_tags:
                if text_before.endswith(no_close_tag):
                    cursor.setPosition(position + 1)
                    edit_area.setTextCursor(cursor)
                    return
    
            for open_tag, close_tag in self.auto_close_tags.items():
                if text_before.endswith(open_tag):
                    cursor.setPosition(position + 1)
                    cursor.insertText(close_tag)
                    cursor.setPosition(position + 1)
                    edit_area.setTextCursor(cursor)
                    return
            
            if '<a ' in text_before and ('href=' in text_before or 'href =' in text_before):
                cursor.setPosition(position + 1)
                cursor.insertText("</a>")
                cursor.setPosition(position + 1)
                edit_area.setTextCursor(cursor)
                return        
            elif '<audio ' in text_before and ('src=' in text_before or 'src =' in text_before):            
                cursor.setPosition(position + 1)
                cursor.insertText("</audio>")
                cursor.setPosition(position + 1)
                edit_area.setTextCursor(cursor)
                return
            elif '<video ' in text_before and ('src=' in text_before or 'src =' in text_before):             
                cursor.setPosition(position + 1)
                cursor.insertText("</video>")
                cursor.setPosition(position + 1)
                edit_area.setTextCursor(cursor)
                return
            return
    
            
    
        original_key_press(event)
    

    def apply_tag(self, edit_area: QTextEdit, tag: str):
        cursor = edit_area.textCursor()
        self.toggle_wrapping_by_tags(edit_area, cursor, f"<{tag}>", f"</{tag}>", False)       
    

    def apply_details_tag(self, edit_area: QTextEdit):
        cursor = edit_area.textCursor()
        if not cursor.hasSelection():
            return
        selected_text = cursor.selectedText()
        resposta = localization["response"]
        details_text = (
            '<details>\n'
            f'  <summary>{resposta}</summary>\n'
            f'  {selected_text}\n'
            '</details>'
        )
        cursor.insertText(details_text)
    


    def choose_text_color(self, edit_area: QTextEdit):
        cursor = edit_area.textCursor()
        if not cursor.hasSelection():
            return
        selected_text = cursor.selectedText()
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        full_text = edit_area.toPlainText()

        # Поиск <span style="color: ...">...</span> вокруг выделения
        pattern_span = re.compile(
            r'<span\s+style="color:\s*([^";]+)[^"]*"\s*>(.*?)</span>',
            re.IGNORECASE | re.DOTALL
        )
        match = None
        for m in pattern_span.finditer(full_text):
            tag_start = m.start(2)
            tag_end = m.end(2)
            if tag_start <= sel_start and tag_end >= sel_end:
                match = m
                break

        color_code = None        
        dialog_title = localizationF("choose_text_color_set", "Set text color")
        pattern_color = re.compile(r'#([A-Fa-f0-9]{6,8})')
        match_color = pattern_color.fullmatch(selected_text.strip())
        if match:
            color_code = match.group(1)
            dialog_title = localizationF("choose_text_color_change", "Change text color")
        elif match_color:
            color_code = selected_text.strip()
            dialog_title = localizationF("change_color_code", "Change color code only")

        color = QColor(color_code) if color_code else QColor()
        color = QColorDialog.getColor(color, edit_area, dialog_title)
        if not color.isValid():
            return

        color_name = color.name(QColor.NameFormat.HexArgb if color.alpha() < 255 else QColor.NameFormat.HexRgb)

        cursor.beginEditBlock()
        if match:
            # Меняем только цвет в существующем теге
            new_tag = f'<span style="color: {color_name};">{match.group(2)}</span>'
            cursor.setPosition(match.start(), MoveAnchor)
            cursor.setPosition(match.end(), KeepAnchor)
            cursor.insertText(new_tag)
            # Восстанавливаем выделение только на исходном тексте
            new_sel_start = match.start() + len(f'<span style="color: {color_name};">')
            cursor.setPosition(new_sel_start)
            cursor.setPosition(new_sel_start + len(match.group(2)), KeepAnchor)
        elif match_color:
            # Просто заменить код цвета на новый, без тегов
            cursor.removeSelectedText()
            cursor.insertText(color_name)
            # Восстановить выделение на новом коде
            cursor.setPosition(sel_start)
            cursor.setPosition(sel_start + len(color_name), KeepAnchor)
        else:
            # Вставляем новый тег, выделяем только текст
            cursor.removeSelectedText()
            cursor.insertText(f'<span style="color: {color_name};">{selected_text}</span>')
            new_sel_start = sel_start + len(f'<span style="color: {color_name};">')
            cursor.setPosition(new_sel_start)
            cursor.setPosition(new_sel_start + len(selected_text), KeepAnchor)
        edit_area.setTextCursor(cursor)
        cursor.endEditBlock()



    def choose_background_color(self, edit_area: QTextEdit):
        cursor = edit_area.textCursor()
        if not cursor.hasSelection():
            return
        selected_text = cursor.selectedText()
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        full_text = edit_area.toPlainText()

        # Поиск <p style="background-color: ...">...</p> вокруг выделения
        pattern_p = re.compile(
            r'<p\s+style="background-color:\s*([^";]+)[^"]*"\s*>(.*?)</p>',
            re.IGNORECASE | re.DOTALL
        )
        match = None
        for m in pattern_p.finditer(full_text):
            tag_start = m.start(2)
            tag_end = m.end(2)
            if tag_start <= sel_start and tag_end >= sel_end:
                match = m
                break

        color_code = None
        dialog_title = localizationF("choose_bg_color_set", "Set background color")
        pattern_color = re.compile(r'#([A-Fa-f0-9]{6,8})')
        match_color = pattern_color.fullmatch(selected_text.strip())
        if match:
            color_code = match.group(1)
            dialog_title = localizationF("choose_bg_color_change", "Change background color")
        elif match_color:
            color_code = selected_text.strip()
            dialog_title = localizationF("change_color_code", "Change color code only")
        


        color = QColor(color_code) if color_code else QColor()
        color = QColorDialog.getColor(color, edit_area, dialog_title)
        if not color.isValid():
            return

        color_name = color.name(QColor.NameFormat.HexArgb if color.alpha() < 255 else QColor.NameFormat.HexRgb)

        cursor.beginEditBlock()
        if match:
            new_tag = f'<p style="background-color: {color_name};">{match.group(2)}</p>'
            cursor.setPosition(match.start(), MoveAnchor)
            cursor.setPosition(match.end(), KeepAnchor)
            cursor.insertText(new_tag)
            new_sel_start = match.start() + len(f'<p style="background-color: {color_name};">')
            cursor.setPosition(new_sel_start)
            cursor.setPosition(new_sel_start + len(match.group(2)), KeepAnchor)
        elif match_color:
            # Просто заменить код цвета на новый, без тегов
            cursor.removeSelectedText()
            cursor.insertText(color_name)
            cursor.setPosition(sel_start)
            cursor.setPosition(sel_start + len(color_name), KeepAnchor)
        else:
            cursor.removeSelectedText()
            cursor.insertText(f'<p style="background-color: {color_name};">{selected_text}</p>')
            new_sel_start = sel_start + len(f'<p style="background-color: {color_name};">')
            cursor.setPosition(new_sel_start)
            cursor.setPosition(new_sel_start + len(selected_text), KeepAnchor)
        edit_area.setTextCursor(cursor)
        cursor.endEditBlock()



    
    def insert_line_break(self, edit_area: QTextEdit):
        cursor = edit_area.textCursor()
        cursor.insertText('<br>')



    def handle_radio_toggle(self, button_name, checked):
        """Обрабатывает переключение между кнопками."""                
        if checked:
            edit_area = mw.app.activeWindow().findChild(QTextEdit, 'edit_area')
            self.cur_edit_area = edit_area
            if not edit_area:
                return            
            self.update_timer.stop() 
            # Переключаемся на новую кнопку
            self.current_button = button_name
            # Восстанавливаем позицию для новой кнопки
            self.restore_cursor_position(edit_area, button_name)
            # self.needs_update_from_external_editor(self.cur_edit_area)
            # QTimer.singleShot(2000, lambda: self.needs_update_from_external_editor(self.cur_edit_area) )
            self.update_timer.start()

    def timer_needs_update(self):
        """таймер проверит нужно ли обновление"""        
        global focus_watcher       
        self.update_timer.stop()        
        # if not self.cur_edit_area or QApplication.activeWindow() is None:
        if self is None or self.cur_edit_area is None: 
            self.update_timer.start()
            return
        
        blisV = self.cur_edit_area.isVisible()
        if not blisV:                        
            self.update_timer.start()
            return

        if focus_watcher.activate_trigger:
            if not self.needs_update_from_external_editor(self.cur_edit_area):
                focus_watcher.activate_trigger = False
        self.update_timer.start()
        







# Initialize addon
def initialize_html_js_highlighting_addon():
    global html_js_highlighting_addon
    html_js_highlighting_addon = HtmlJavaScriptHighlightingAddon()

initialize_html_js_highlighting_addon()
