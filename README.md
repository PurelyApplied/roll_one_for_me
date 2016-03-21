#roll_one_for_me: README.md
This repository contains source code for Reddit bot /u/roll_one_for_me.
Generates an instance of a random table in a Reddit submission.

**How It Works:**

* The bot looks for "headers", lines starting with "d<X>" (ignoring punctuation, and where <X> is some number>.  Looking at the lines following the header, the bot looks for <X> lines that begin with a digit.  These lines are taken to be the possible outcomes of the table.

* If any of those outcomes include another "d<Y>", it will try to find an in-line table. For instance, if I was rolling for an animal, an outcome might be "4. Bird (d4): 1. eagle; 2. falcon; 3. sparrow; 4. swallow."  It tries to find where the numbers 1 through <Y> land and splits up the sub-outcomes based on that positioning.

**Known Issues:**

* Since the bot constantly strips punctuation so as to avoid parsing Reddit's markup, it will leave parentheses and the like open, drop a plural's possessive, and so on if an entry were to end or begin with them.  I might add a check later that closes any parens, but it's low-priority.

* If an error occurs, it won't say anything on the user-end.  If a table doesn't get rolled, it's probably due to a parsing error.

* A header of <n>d<k> will be parsed as 1d<k> for the time being.

* If a table contains an outcome with any "d<k>" text, that table will not be rolled; it will attempt to parse it as an inline table and fail.

* If a section header or anything similar contains a number, it may get parsed as a table outcome and then be ignored when the number of items does not match the die-roll value.

* Ranges fail if anything other than a hyphen is used.  Em-dashes and En-dashes break, but should be included in the future.

**Command Lexicon**

* Mentions: Call the bot by using /u/roll_one_for_me in any comment
  post.  (The slashes are important.)  This will look for tables in
  the OP and top-level comments.  Alternatively, if a link is
  provided, it will look for tables at the links *instead*.

* Private Messages: You may also send the bot a PM with links and it
  will reply with a roll.

* Current thoughts for planned features:  Hard brackets to denote targeted tables, with another (optional) internal set of brackets indicating any desired effects. Additional tables can be specified with additional bracketed items.  A *Table Reference* will be (1) a link to another table, (2) the keyword "OP" to refer to the submission in which a comment is contained, or (3) the keyword "comments" to refer to all top-level comments in a thread.  If no specifics are given, default behavior is to roll one of everything.  If no brackets are given, the default behavior will be "[OP] [comments]".  
    * [Table reference 1 [ Table 1 specific choices (format TBD) ] ] [Table reference 2]
* [This section to be updated as additional features are added]

**Current Features:**

* Parses tables main post
* Parses top-level comments
* Parses in-line tables
* Capable of parsing tables with ranges.  Excepts digits separated by (a) hyphen(s).  This may appear both at the top-level and in inline subtables.
* Also monitors new posts to /r/DnDBehindTheScreen and announces seeds a top-level comment for better organization of roll requests.
* Capable of processing links to other other tables.  Links must link to Reddit and not use redd.it redirecting.  Currently only able to process submission links, not links to comments.
* Capable of processing PMs.

**Planned Features:**

* Allow links to comments containing tables, not only Submission posts.
* Parse multiple dice: resolve <n>d<k> for n > 1
* Selective rolling: Specify which items you would like rolled, to ignore / include comment tables, et cetera
* Multiple rolling: Allowing some or all items to be rolled multiply, either with or without repetition of outcome

**Wishlist Features (Stuff I'll probably never do):**

* Generate, post somewhere, and link a .pdf if a link is not provided.

**Backend things that need work -- these things always need work -- but you probably won't notice:**

* Error handling and logging
* Clean up source code, drop some items to classes for better abstraction, stop using global variables.
* As links are processed, comments / PMs might approach the character limit.  In this case, messages will need to be split and delayed enough to allow passage through Reddit's spam filtering.
* The constant struggle, it's real.