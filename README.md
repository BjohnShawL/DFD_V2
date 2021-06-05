"# DFD_V2" 
This repo is for the python remake of DiceForDiscord - a JS dice roller app I built a year or so ago. I've learned quite a lot since then (including the very important fact that I prefer python) and we've been using the JS version for several months as a tool for online roleplay sessions. A few things came up - 
- 1) no one used the Hidden roll functionality. It's kinda janky, and relies on having roles assigned, and you can see when the GM is making a hidden roll. It's not great
- 2) In a game like RoleMaster, or DnD, or anything where the stats are modified regularly, being able to add plusses or minuses to your roll at point of contact is pretty important. It speeds up the flow of the game, and in an online session, not having to whip the calculators out (play RM or Shadowrun with no calculator and come back to me) is pretty useful.

So to deal with that, I implemented modifiers, and (KISS) removed the GM hidden roll functionality. I might set up a small SQLite db interface so you can name your favourite rolls - I'd like to get to the point where I can say !Roll Initiative and have it do the roll, with modifiers - but that's in the future.

Until then, if you're reading this, you're probably wanting to take a look over the code. main.py is the entry point, and the Classes folder contains rolls.py and modifiers.py. The api used is http://roll.diceapi.com - and is almost exactly what I need (yeah, explosion would be cool, but I can probably implement that myself if I need it)

Enjoy