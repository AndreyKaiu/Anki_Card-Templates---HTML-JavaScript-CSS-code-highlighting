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

The highlighting code is not the most ideal, but it is quite acceptable for simple use. A large number of lines can load the highlighting algorithms, but it seems that up to 1500 lines of code do not highlight everything for long and most likely there will be no problems.

If you open the template code in a third-party editor by pressing F2, then do not forget to save the code when switching from it, and when you get to the Anki editor, you can get all the updates by pressing F5. If you make a change to the template code in Anki and you have a third-party editor open, then you also need to save when switching, then the third-party editor will usually notice the changes itself and there will be no problems.

**Changes for version 1.4**

Display issues with transparent colors have been fixed. Previously, if a fully transparent color was specified, it would be displayed as is, or rather, would not be visible.

Fixed an issue that caused Anki to completely crash if text was selected and F2 was pressed. The cause was a PyQT update, but we and the AI ​​couldn't pinpoint the exact cause, so it was easier to work around the issue and save hours of time.

The Alt+Left, Alt+Right, and Ctrl+Shift+Insert keys have been restored. Last year, Anki made changes, and this feature stopped working in newer versions. Now I've found the time to fix it. Let me reiterate that the Alt+Left and Alt+Right hotkeys are very important, as they allow you to navigate to specific positions in a long code. Simply place the cursor somewhere, move it left or right, and that position will be remembered. You can then press these hotkeys to quickly navigate to the desired position.

Added many new words for tooltips.

Now, if you make changes or change the cursor position, the last active card type and template are remembered. This is essential if you constantly switch between different note types. Of course, you'll have to wait 1-2 seconds for the algorithm to complete, but that's only true for very large codebases.

**VERSIONS**
- 1.2, date: 2026-02-23. Fixed display issues with transparent color, and restored the functionality of the Alt+Left, Alt+Right, and Ctrl+Shift+Insert hotkeys. Added many new words for tooltips. The last active card type and template are now remembered if you made changes or changed the cursor position.
 
- 1.1, date: 2025-09-22. I'm trying to fix an error accessing a component from a timer when the window was already closed. If I catch another similar error, I'll update it again from version 1.1.
  
- 1.1, date: 2025-09-10. Corrected and improved:
  
 — fixed the error when pressing F2 if the front side was not opened before.
 
 — error in the comment presentation if the long comment symbol \` was somewhere in "\`"
 
 — highlighting {{}} even if the field is specified in "" or in ''
 
 — highlighting of color words will be with a word boundary check
 
 — the "Home" and "End" buttons began to work correctly with the "Shift" key
 
 — &amp;nbsp; - Ctrl+Shift+Space
 
 — multi-line comment \`\` is now supported only with the equal sign =\`\`
 
 — fixed the error of searching backwards for brackets }
 
 — the most important thing is that saving the cursor position for each template has been added. This is very important if you have complex code in templates. The history of 7 cursor positions (which were moved along the line) is also saved for each template ("Alr+Left" or "Alr+Right" - view the history of the position)
 
 — search and replace are saved globally for all, and positions only for a specific file
 
 — some more keywords have been added for the drop-down hint  
 
- 1.0, date: 2025-06-01. First release













