# The TADS 3 Web UI Runner

One of the main complains people tend to have with TADS 3 Web UI, and probably
the dominant reason it is considered "dead" by most, is that it is difficult to
figure out how to run it. Even if you have a proper HTML TADS interpreter
installed like QTADS, you still can't run Web UI games, because their virtual
machines simply don't support running as a headless server and TADS 3's network
features. The only way to properly run Web UI games is via FrobTADS, but
FrobTADS is difficult to install (must be compiled from source) and you have to
know how to use the command line and what options to use in order to use it to
play Web UI games. Moreover, it's a bit of a hassle, as it will start a local
server and give you a link, and then you have to go to that link in a separate
browser.

No longer!

This is a simple application that will accept TADS 3 Web UI game files dragged
and dropped into it, or selected via a file chooser dialog, and run a FrobTADS
server with them for you in the background, while presenting you with
a streamlined inline, self-contained view of the resulting game's web page, so
that the work flow looks and feels like using a traditional interpreter.

## TODO

- [x] Iron out the bugs that make drag and drop choosy about where you drop the
  file
- [ ] Fix the bug where the interpreter hangs if you give it a non Web UI file.
- [ ] Maybe open non Web UI files in QTADS instead?
