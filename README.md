# Anki_Card-Templates---HTML-JavaScript-CSS-code-highlighting
The template editing window has a highlighting feature, more functions have been added to the editor, and most importantly, the window can remember the cursor position when, for example, you switch to look at something in the styles.

ATTENTION! The add-on was tested mainly on PyQt 6, although the code did work in PyQt 5 if possible, but it is a very complex code, with many states and checks. So consider this version not final, but will be tested by you. In this regard, you can not rate the add-on yet, and if you find a problem, write to the forum first. If not me, then someone else can give an answer faster, what can be changed in the code and remove the error found.

The original idea of ​​"HTML Buttons in Template" from the author: [https://ankiweb.net/shared/info/2063726776](https://ankiweb.net/shared/info/2063726776)
This code was corrected, improved and supplemented with other ideas:
- the most important thing that could be in Anki is saving the cursor position (selection) when switching between the front and back templates, css.
- the ability to save the code and open it with a third-party application (preferably Visual Studio Code). The Anki editor is not blocked and if you save in both applications, then even parallel work is possible. A copy of the template is also saved (by Ctrl + S) in the folder anki_backup (C:\Users\USERNAME\anki_backup\).
If necessary, such copies can be loaded later.
- code autocompletion, autoinsert, custom code templates.
- highlighting by code of all words, as in the current selection, ability to search for the desired word by code (Ctrl+F, and continue F3)

And other...

![Anki_Card_Templates_1](https://github.com/user-attachments/assets/11369767-eea3-419a-82bd-83ea2fa8654e)

Note that the standard search is done both forward and backward.
The first line can be like this. This line is required for transferring to a third-party editor and monitoring file changes. Here, the highlighting for paired characters is also shown.
Important things are highlighted in red, here it is a style and highlighting for them separately, not like a line.
Color codes can have a background highlighting.
The cursor position and the character after it are shown under the text.
If you press the "?" button, you will be shown the help. Its contents for version 1.0:

![Anki_Card_Templates_2](https://github.com/user-attachments/assets/d95ffa57-2cf2-4626-b1d1-4d644517c855)
![Anki_Card_Templates_3](https://github.com/user-attachments/assets/32499371-5412-425d-a964-0202bd7204ba)

There may be a translation for your language, so install the add-on and check.

When installing the add-on, you can change the configuration. Here you can see what languages ​​the add-on is translated into. In the configuration, you can disable code autocompletion, autoinsert, you can set up commands to launch an external editor, set up the add-on language or it will automatically detect the language in the anchor. There is only one highlighting theme, but if necessary, you can add it yourself or change the standard one.

![Anki_Card_Templates_4](https://github.com/user-attachments/assets/5800408c-3da9-4625-9939-bf307e1d4189)












