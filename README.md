# Anki_Card-Templates---HTML-JavaScript-CSS-code-highlighting
The template editing window has a highlighting feature, more functions have been added to the editor, and most importantly, the window can remember the cursor position when, for example, you switch to look at something in the styles.

ATTENTION! The add-on was tested mainly on PyQt 6, although the code did work in PyQt 5 if possible, but it is a very complex code, with many states and checks. So consider this version not final, but will be tested by you. In this regard, you can not rate the add-on yet, and if you find a problem, write to the forum first. If not me, then someone else can give an answer faster, what can be changed in the code and remove the error found.

The original idea of ​​"HTML Buttons in Template" from the author: [https://ankiweb.net/shared/info/2063726776]
This code was corrected, improved and supplemented with other ideas:
- the most important thing that could be in Anki is saving the cursor position (selection) when switching between the front and back templates, css.
- the ability to save the code and open it with a third-party application (preferably Visual Studio Code). The Anki editor is not blocked and if you save in both applications, then even parallel work is possible. A copy of the template is also saved (by Ctrl + S) in the folder anki_backup (C:\Users\USERNAME\anki_backup\).
If necessary, such copies can be loaded later.
- code autocompletion, autoinsert, custom code templates.
- highlighting by code of all words, as in the current selection, ability to search for the desired word by code (Ctrl+F, and continue F3)
And other
