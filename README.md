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
In the screenshots below, the highlighting is implemented using the add-on [https://ankiweb.net/shared/info/1621264520](https://ankiweb.net/shared/info/1621264520)

When installing the add-on, you can change the configuration. Here you can see what languages ​​the add-on is translated into. In the configuration, you can disable code autocompletion, autoinsert, you can set up commands to launch an external editor, set up the add-on language or it will automatically detect the language in the anki. There is only one highlighting theme, but if necessary, you can add it yourself or change the standard one.

![Anki_Card_Templates_4](https://github.com/user-attachments/assets/5800408c-3da9-4625-9939-bf307e1d4189)
![Anki_Card_Templates_5](https://github.com/user-attachments/assets/ed0d2cf0-fac0-4a9c-9da0-c110be2f1652)

In the configuration you can also set your own templates. They start with a percent sign and are entered in the same way. Double percent indicates the cursor position (see the help for how to navigate these positions). Double dollar signs indicate the positions where the text selected before calling this template will be inserted.

![Anki_Card_Templates_6](https://github.com/user-attachments/assets/bb165757-f3b4-4466-9fbd-6e4ad33d065a)

Important operators, such as a cycle, can be highlighted especially, as well as important ones such as exiting a function, interruptions - they are highlighted in bright red.
Here on the screen at the very beginning there are many blue underlining lines - this indicates that tabulation was applied. And it is better to replace tabulation with 4 spaces (you can copy the entire text and paste it again, then the replacement will be made automatically). Red underlining lines are possible - this is some kind of sign, some kind of indistinguishable space and it may interfere with you, so pay attention.

If you need to comment out a group of lines or uncomment them, then be sure to select them all, otherwise simply deleting the start and end tags may not always give the correct highlighting result, but you can fix this yourself by pressing the F4 button and if none of the characters are selected.

Switching card types here is changed from F3, F4 to Ctrl+F3, Ctrl+F4 since I needed my own hot keys for F3 and F4
I have 7 cursor position histories so far. The algorithm is not quite usual, that is, when you roll back, you do not delete positions. The position history allows you to quickly go back and forth to the code you need.
Please note that pressing "End" again is not quite standard, but it allows you to go to the end of the visible part of the line, and pressing here to move to a new line will result in the extra left spaces being removed.

The highlighting code is not the most ideal, but it is quite acceptable for simple use. A large number of lines can load the highlighting algorithms, but it seems that up to 1500 lines of code do not highlight everything for a long time and most likely there will be no problems.















