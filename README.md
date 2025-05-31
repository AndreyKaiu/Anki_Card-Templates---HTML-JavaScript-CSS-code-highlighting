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

Hotkey

<b>...</b> - Ctrl+B 
<i>...</i> - Ctrl+I 
<u>...</u> - Ctrl+U 
<mark>...</mark> - Ctrl+M 
<details>...</details> - Ctrl+Shift+D 
<span style="color: >...</span> - Ctrl+Shift+T 
<span style="background-color: >...</span> - Ctrl+Shift+B 
<br> - Shift+Enter 
<blockquote>...</blockquote> - Ctrl+Q 
<sub>...</sub> - Ctrl+= 
<sup>...</sup> - Ctrl+Shift+= 
<h1>...</h1> - Ctrl+Shift+1 (+!) 
<h2>...</h2> - Ctrl+Shift+2 (+@) 
<h3>...</h3> - Ctrl+Shift+3 (+#) 
<h4>...</h4> - Ctrl+Shift+4 (+$) 
<h5>...</h5> - Ctrl+Shift+5 (+%) 
<h6>...</h6> - Ctrl+Shift+6 (+^) 
<p>...</p> - Ctrl+Shift+7 (+&) 
<div>...</div> - Ctrl+Shift+8 (+*) 
<!-- ... --> - Ctrl+/ 
/* ... */ - Ctrl+Shift+/ 
F1 — show this window 
Alt+0 — show this window 
Tab — insert 4 spaces (and if selected, before lines. If the autocomplete window is open, Enter and Tab enter the top one from the list) 
RShift+Tab — insert a tab character (if needed in the code tag and other similar ones) 
LShift+Tab — delete back 4 spaces (and if selected, before lines) 
Ctrl+Tab — Search forward %% 
Ctrl+Shift+Tab — Search back %% 
Ctrl+Space — Show Code completion (and adds all the words from the text) 
F2 — Save to file and transfer to external editor 
F4 — update the highlight and highlight all as selected 
F5 — Update from previously saved file 
Ctrl+F — search for a substring 
F3 — search next (what was previously searched for by Ctrl+F) 
Shift+F3 — search back (what was previously searched for by Ctrl+F) 
Ctrl+H — show this window 
Ctrl+G — go to line with number 
Ctrl+S — Save backup copy (and to file) 
Ctrl+O — Load from previously saved file 
Ctrl+V — insert as text (tabs are replaced with 4 spaces) 
Ctrl+Shift+V — insert as text (without replacing tabs) 
Ctrl+Shift+Insert — insert plain HTML (b, i, u and some others) 
Ctrl+Shift+Alt+Insert — insert plain HTML with color preservation 
Home — go to the beginning of the text, and if already there, then to the beginning of the line 
End — go to the end of the line, and if already there, then to the end of the text 
Enter — insert with spaces if at the beginning of the text or at the end (special cases for {}). If the autocomplete window is open, Enter and Tab enter the top one from the list 
Ctrl+Enter — save and close 
Ctrl+Shift+T or Ctrl+Shift+B — if the selected color code is in the format #RRGGBB, then it will change only it 
Alt+Left — to the previous cursor position (where the cursor changed position with keys) 
Alt+Right — to the next cursor position (where the cursor changed position with keys) 





