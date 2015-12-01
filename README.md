#roll_one_for_me: README.md
This repository contains source code for Reddit bot /u/roll_one_for_me.
Generates an instance of a random table in a Reddit submission.



**Command Lexicon**

* Currently, the only use is to summon the bot by saying its name.
  (Some prefer to chant the bot's name, shrouding themselves in darkness and calling to the corners of creation.
  It has not been confirmed if this behavior produces qualitatively different outcomes.)

* Current thoughts for planned features:  Hard brackets to denote targeted tables, with another (optional) internal set of brackets indicating any desired effects. Additional tables can be specified with additional bracketed items.  A *Table Reference* will be (1) a link to another table, (2) the keyword "OP" to refer to the submission in which a comment is contained, or (3) the keyword "comments" to refer to all top-level comments in a thread.  If no specifics are given, default behavior is to roll one of everything.  If no brackets are given, the default behavior will be "[OP] [comments]".  
    * [Table reference 1 [ Table 1 specific choices (format TBD) ] ] [Table reference 2]
* [This section to be updated as additional features are added]

**Current Features:**

* Parses tables main post
* Parses top-level comments
* Parses in-line tables
* Capable of parsing tables with ranges.  Excepts digits separated by a hyphens.  Does not parse in-line subtables containing ranges.
* Also monitors new posts and announces seeds a top-level comment for better organization of roll requests.

**Planned Features:**

* Follow links to find other tables.  This will be limited to direct links to Reddit posts (submissions or comments both) only; links off-site or additional links on the targeted post will be ignored.
* PM Requests:  Once links are worked out, you will be able to PM the bot with links and it will respond with an instance.
* Parse multiple dice: resolve <n>d<k> for n > 1
* Selective rolling: Specify which items you would like rolled, to ignore / include comment tables, et cetera
* Multiple rolling: Allowing some or all items to be rolled multiply, either with or without repetition of outcome

**Wishlist Features (Stuff I'll probably never do):**

* Generate, post somewhere, and link a .pdf if a link is not provided.

**Backend things that need work but you probably won't notice:**

* Error handling and logging
* Clean up source code, drop some items to classes for better abstraction, stop using global variables.
* As links are processed, comments / PMs might approach the character limit.  In this case, messages will need to be split and delayed enough to allow passage through Reddit's spam filtering.
* The constant struggle, it's real.

**How It Works:**

* If you start a line with d<X>, the bot considers that line a Header.  It will look for <X> lines immediately following that begin with a number, considering them to be possible outcomes.

* If any of those outcomes include another d<Y>, it will try to find an in-line table. For instance, if I was rolling for an animal, an outcome might be "4. Bird (d4): 1. eagle; 2. falcon; 3. sparrow; 4. swallow."  It tries to find where the numbers 1 through <Y> land and splits up the sub-outcomes based on that positioning.

**Known Issues:**

* Since the bot constantly strips punctuation so as to avoid parsing Reddit's markup, it will leave parentheses and the like open, drop a plural's possessive, and so on if an entry were to end or begin with them.  I might add a check later that closes any parens, but it's low-priority.

* If fewer than the expected number of items exist in a table, you'll get a silly line of "(d1 -> 1:) Could not parse" instead of a meaningful error message.

* A header of <n>d<k> will be parsed as 1d<k> for the time being.