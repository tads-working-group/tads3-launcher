# The TADS 3 Launcher

The TADS 3 Launcher provides a simple unified launcher for **all TADS 3 game
files**, *including* Web UI files *and* regular game files.

This is designed to solve one of the biggest complaints with TADS 3 from a
player's perspective, which is that there is no easy to use, self-contained
player that you can use to run Web UI games, and even if there was, there's no
*ex ante* way to tell whether a TADS 3 game file is a Web UI file or a regular
one, and regular interpreters can't play Web UI files and Web UI files can't
play regular HTML TADS game files, so you'd have to figure it out by trial and
error.

TADS 3 Launcher solves this problem by checking the plain-text symbols in the
binary game file it is provided for whether it includes the Web UI network
library or not. If it is a Web UI game, it uses the correct Web UI-enabled
runner (either t3run or frobTADS depending on your platform) behind the scenes to run the game
server, and provides you with an inline webview to the Web UI game, thus
appearing like a normal self-contained interpreter. If it is *not* a Web UI
game, but a regular HTML TADS or text-only TADS game, it launches QTADS under
the hood and embeds the QTADS window as a frameless widget, so that this also
gives the appearance of being perfectly self contained.

This way, not only has TADS 3 Launcher, for the first time ever, provided an easy
way to play *Web UI* games, but for the first time it provides a unified means
of playing *all* TADS 3 games!

## Screenshots

Screenshot of the launcher:

![A screenshot of the TADS 3 Launcher. It has a purple background with large
white text saying "Play a T3 File" above smaller gray text saying "Drag and drop
the file into this window or click the button below" and a large lighter purple
button that says "Open game".](screenshots/one.png)

Screenshot of the launcher playing a Web UI demo game:

![A screenshot of the TADS 3 Launcher playing a Web UI game. The previous purple
interface has been completely replaced by a web view that fills the screen
completely, showing the Web UI game, which is a yellow-on-black split screen
with a live-updating map of graphical tiles on one half and the actual
transcript of the game on the other, and buttons on the bottom.](screenshots/two.png)

Screenshot of the launcher playing a regular HTML TADS game:

![A screenshot of the TADS 3 Launcher playing a regular HTML TADS game. It looks
identical to QTADS except for the window title, since it is just seamlessly
embedding QTADS.](screenshots/three.png)
