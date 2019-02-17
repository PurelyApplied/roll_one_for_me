#roll_one_for_me: README.md

This repository contains source code for Reddit bot /u/roll_one_for_me, a.k.a. RofM.
It is a username-summoned bot who will generate an outcome provided by a random table,
typically in one of the D&D related subreddits like
/r/DnDBehindTheScreen and the affiliated
/r/BehindTheTables being the most common.

RofM makes heavy use of [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for parsing,
[Python-dice](https://github.com/borntyping/python-dice) for its dice roll lexicon,
and [anytree](https://github.com/c0fec0de/anytree) for workload management.

## Summoned behavior

The common use-case is to summon `/u/roll_one_for_me` via a username-mention, 
and the bot will roll "nearby" tables.  This includes, in order:

* Any tables found in the comment containing the user-mention
* Any tables found in comments or submissions linked in the summoning user-mention
* Any tables found the "OP" submission text
* Any tables found in any top-level comment to the submission.

Similarly, a private message can be sent to the bot, though the last two items do apply in this case.

## Additional behavior requests

Additional behavior may be requested by including a command in double-brackets, e.g., 
"[[COMMAND]]".  The following are valid commands:

* [[<DICE>]]: Rolls the requested `<DICE>` string, using the [Python-dice](https://github.com/borntyping/python-dice) library to parse and execute rolls.
Refer to their page for language specifics, but it works how you would expect.  For instance, 
  [[2d8]] or [[4d6^3]].
* More to come pending community discussion.

## Tables and formatting

With RofM 2.0, nearly all parsing is done via BeautifulSoup against the rendered html of text.
The bot will do well with most things using the table and enumeration formats.

A table-formatted table is expected to have a title-bar.  "Wide" tables are now supported.
If a die is specified, it should exist in the upper-left box of a formatted table.

An enumeration is expected to have a "header" before enumeration begins, but it is not required to do so.
An un-headered enumeration of <N> items is assumed to be rolled via 1d<N>.

## Future work

I would like to add the ability for tables to link each other or for certain table outcomes to produce additional rolls,
either of the "roll this table twice" outcomes, as the currently-disable "in-line" tables, or similar.

## Known Issues:

* Messages sent via chat are not supported.
The bot is backed by `praw`, and the chat does not have an officially documented API.
If chat ever leaves "beta" and an API is documented, chat will quickly become supported.

* With the 2.0 overhaul of core logic, the bot is more sensitive to formatting.
For best results, make sure that the post renders in Reddit as a formatted table or enumeration.
(A related benefit, however, is that links no longer have to be in the `[Text](link)` format.)

* v2.0 no longer rolls "in-line" tables due to its reliance on html formatting.
