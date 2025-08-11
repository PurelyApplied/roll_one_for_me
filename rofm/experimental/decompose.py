#!/usr/bin/env python3
from string import punctuation, whitespace

from rofm.classes import STARTS_WITH_ROLL_REGEX


def text_to_tables(raw_text):
    # Steps:
    # - Identify any line that has a roll in it?
    # - See if the lines that follow are enumerated or bulletted.
    # - If they are, and if the weights sum the correct amount, build the table.
    # - If there are rolls that don't appear to have a table to chase them... Report that?

    lines = raw_text.split('\n')
    lines_that_start_with_die_rolls = [i for i, l in enumerate(lines)
                                       if STARTS_WITH_ROLL_REGEX.match(l.lstrip(punctuation + whitespace))]
    pass


def test():
    text_to_tables(EXPLICIT)

EXPLICIT="""After producing a god, try writing a quick description like it was a writing prompt.
The categories are interpretative;
 a god symbolized by a torture device may be an S&M enthusiast or may have been tortured,
 leading to a whip or a cross.
A god hated and loved because of nature might be responsible for wild chaos (owlbears, bullets)
 and responsible for conventional animals (deer, rabbits).

---

d8 This God Is

1-2. a God

3-4. a Goddess

5-8. is not a god or goddess

d3 This God is

1. Evil

2. Good

3. Neutral

d3 and

1. Lawful

2. Neutral

3. Chaotic

---

# **6d99 - 100 The god's symbol is a**

1. hand holding a (roll again and combine)

2. quiver full of (roll again and combine)

3. Raven

4. Winged Man

5. Winged Woman

6. Dove

7. Torture Device

8. Horse

9. Child

10. Fish

11. Shark

12. Shield

13. Spear

14. Sword

15. Arrows

16. Bow

17. Dice

18. Eye

19. Dog

20. Wolf

21. Skeleton

22. Book

23. Compass

24. God's Face

25. Spy glass

26. Boat with full sails

27. Ship with destroyed sails

28. Owl

29. Falcon

30. Sandals

31. Boots

32. Slippers

33. Precious gem

34. Precious metal

35. Base metal

36. Storm cloud

37. Sun

38. Castle

39. golem/construct

40. single tree

41. forest

42. desiccated forest

44. Mountain

45. Forge/Smithy

46. Hearth

47. Fire

48. Wheat

49. Crops

50. Cattle

51. Deer

52. Plate with food

53. Plate with scraps

54. Quill

55. Lips

56. Wide mouth

57. Mouth with something coming out of it (roll again and combine)

58. Basic shape

59. Basic shape with something inside (roll again and combine)

60. Complex shape

61. Complex shape with something inside (roll again and combine)

62. Helmet

63. Headstone

64. Forked river

65. Homogeneous group of people holding hands

66. Heterogeneous group of people holding hands

67. Rare herb or plant

68. Aquatic beast

69. Washcloth

70. Closed gate

71. Open gate

72. Ghost

73. Full moon

74. Empty moon

75. Crescent moon

76. Star

77. Wineskin

78. Instrument

79. Shepard's Crook

80. Shroud, which obscures a (roll again and combine)

81. Goblet

82. Snake

83. Vermin

84. Insect/Arachnid

85. A multi-limbed creature

86. Bear

87. Jewelry

88. Mask

89. Fist, clutching a (roll again and combine)

90. Dragon

91. Swarming tentacles

92. Pixie/Fairy

93. Crustacean

94. Lion

95. Turtle

96. Dinosaur

97. Laughing (roll again and combine)

98. Muhsroom

99. big argument. Who knows?

100. Combine 3 options.

---

d12 The god is negatively associated with...

1. Suffering

2. Loss

3. Sacrifice

4. Pain

5. Death

6. Greed

7. Proselytization

8. Disease

9. Weather

10. Labor

11. Death

12. Famine

d12 as well as

1. Floods
2. Golems
3. Violence
4. Children
5. Magic
6. Nature
7. Fire
8. Secrets
9. Necromancy
10. The Seasons
11. Chance/Luck
12. Time

---

d12 The god is celebrated for...

1. Suffering

2. Sacrifice

3. Labor

4. Weather

5. Harvest

6. Death

7. Magic

8. Nature

9. The Seasons

10. Chance/Luck

11. Knowledge

12. Justice

d12 ...as well as

1. Great Strength

2. Great Skill

3. Good Health

4. Wealth

5. Children

6. Music

7. Joy

8. Ocean/Water

9. Travel/Journeys

10. Peace

11. War

12. Mischief and shenanigans

---

d102 The god's followers must

1. Keep a fire roaring

2. Brand themselves

3. Pray at sunrise and sunset

4. Pray at moonrise and moonset

5. Read/Recite sacred texts during the day

6. Read/Recite sacred texts during the night

7. Regard a sundial for advice

8. Humbly cover their entire person during an event

9. Uncover their entire person during an event

10. Maintain a modest shrine at home

11. Maintain a large shrine in a public space

12. Bury their dead

13. Cremate their dead

14. Prostrate on the ground when praying

15. Burn incense/candles when praying

16. Consume a sacred meal

17. Consume a sacred drink

18. Season all food with a certain ingredient

19. Cultivate a plant or crop

20. Be self-sufficient

21. Take care of their families

22. Go on a travel without their families or any possessions

23. Create something

24. Discuss and debate regularly

25. Share and listen to stories

26. Recycle construction material

27. Only build something new

28. Pursue knowledge

29. Live in harmony with nature

30. Exert dominance over nature

31. Repent sins publicly

32. Denounce material possessions

33. Denounce sexual attraction/needs

34. Procreate once a year

35. Never reveal their faith to nonbelievers

36. Maintain a secret sign or code language to identify the faithful

37. Cut out the tongues of liars. Even their own

38. Keep a journal of secrets

39. Keep a journal of romantic exploits

40. Commit murder

41. Consume the flesh of all beasts

42. Practice the sacrifice of animals

43. Practice the sacrifice of sentient beings

44. Fight aberrations

45. Fight non-believers

46. Give to the less fortunate

47. Scorn the less fortunate

48. Collect bones

49. Eat only fruits and vegetables for a specified period

50. Burn all offerings

51. Participate in orgies

52. Be subservient to men

53. Be subservient to women

54. Be subservient to the eldest

55. Be subservient to the youngest

56. Participate in a ritual or festival to be considered an adult

57. Never marry

58. Marry several people

59. Hold an all-night prayer or festival during the full moon

60. Hold an all-night prayer or festival during the absent moon

61. Study magic. Only spell casters are considered "true" members.

62. Scorn magic. Arcane spell casters will never be members.

63. Learn to read an ancient language (draconic, primordial, etc)

63. Learn to read an elemental language (ignan, aquan, etc)

64. Learn to read a divine language (abyssal, infernal, celestial, etc)

65. Create something that benefits the community

66. Refuse food/water during a specified time

67. Pray to an effigy of the god's symbol

68. Carry the god's symbol and decorate the world with it

69. Denounce all other gods

70. Pray before killing an animal

71. Never quarrel with another member of the faith

72. Always treat nonbelievers well

73. Memorize the sacred texts

74. Seek out Evil

75. Seek out Good

75. Seek out Law

76. Seek out Chaos

77. Cause mischief

78. Study under another member until adulthood

79. Journey to a sacred site

80. Hide during storms

81. Rejoice during storms

82. Provide a burial at sea for the deceased

83. Always offer shelter to others from danger and harm

84. Never refuse a request for aid

85. Never forget what their god did for them

86. Respect the sanctity of life

87. Respect the peace of death

88. Respect the hallowed grounds of other faiths

89. Reserve time every week for fun and games

90. Pray before eating

91. Respond to all calls for holy wars/crusades

92. Offer free education

93. Consolidate power

94. Gather magic

95. Destroy magic

96. Punish the wicked

97. Save the wicked

98. Live in peace with all things

99. Destroy all things

100. Roll twice and combine

---

d20 The Holy Colors Are

1. Blue
2. Green
3. Brown
4. Red
5. Yellow
6. Purple
7. Blood
8. Rust
9. Black
10. Midnight
11. Dirt
12. Sky
13. Flesh tones (or literal flesh)
14. Stripes/Pokedots (roll again for colors)
15. Gray
16. Brick
17. Stone
18. Fur
19. Orange
20. Metal

---

d10 This god

1. Was once mortal, and ascended
2. Was born
3. Was created through the mysteries of the cosmos
4. Was created alongside the universe
5. Was created by worship
6. Was created by great magic
7. Has an obscure history
8. Has a history that is often argued about
9. Was once more powerful
10. Only recently obtained its power

---

d8 This god is

1. Feared
2. Loved
3. Respected
4. Tolerated
5. Observed out of mutual benefit
6. Ignored, as much as possible
7. Mistrusted
8. Hated

---

d20 This god recently

1. Gained much power
2. Lost much power
3. Confused the faithful
4. Protected the faithful
5. Scorned the wicked
6. Chose a divine champion
7. Lost a divine champion
8. Challenged another god
9. Allied with another god
10. Swore vengeance and damnation
11. Forgave a great misdeed
12. Reorganized the clergy
13. Released a new testament
14. Lost many followers to a great schism
15. Was betrayed by another god
16. Lost many followers to unfortunate circumstances
17. Gained many followers
18. Lost many followers, but gained new followers of a different perspective
19. Directly intervened in a battle, election, contest, or crowning ceremony
20. Gave a quest to the faithful

---

d8 This god likes to

1. Remain distant and mysterious, and never manifests before mortals
2. Celebrate holy events, and manifests during rituals and/or holidays
3. Embrace the faithful, and manifests often
4. Be gregarious, and manifests often (even during another god's ritual!)
5. Be disruptive, and only manifests when uninvited
6. Participate, and manifests during battles/hunts/contests (in spirit or physically)
7. Summon mortals to the god's plane/realm/hall/domain
8. Remain distant, and only communicates through intermediaries (angels, etc)
"""

if __name__ == "__main__":
    test()
