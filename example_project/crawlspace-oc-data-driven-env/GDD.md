# Crawlspace Game-Design-Document
Crawlspace is a dark cli based Dungeon Crwaler. The Player creates a Character and
tries to escape a horrible Dungeon. With little to no resources the player has to 
navigate through the dungeon, fighting monsters and collecting whatever he can use
to stay alive and escape. Death is permanent and will result in a restart.
It will be simular to 'Fear and Hunger' but just cli based.

## Main Features
The whole game can be played in the cli. The missing visuals are compromised by the
very discriptive text output of the game. Most important Mechanics are: turn-based combat,
exploring the dungeon, leveling the character and collecting and managing items and interacting
with the enviroment or other living things.

## Target Platform / Audience
The target Platform are any computers that can run it in a terminal. It will be very light-weight
to support even old hardware. Target audience are fans of fantasy-dungeon-crawlers or rogue-like lovers.

---

# Implementation

## Game State / Mechanics

### Rooms
The whole gameenviroment is made out of rooms. Each room is connected to the others through Exits. A room can have multiple exits but have at least one.
Each room has a general visual description. A room can contain creatures and objects that can be interacted with. 
Using the look command for example, will display the general description, but will also metion all objects and creatures the player sees. (Depending on
player-stats some creatures / objects aren't seen)


## Commands

### hello
greets the player

### help
outputs all possible commands
if given another command name as an parameter it will display the discription of that command
`help hello`->`hello makes the game greet the player`

### move
move is required to get an parameter. each room will have possible exits that lead to other rooms, these exits names
have to be given. Then the character will move to the other room.
not giving any parameters will output all possible exits of the room the character knows about.

### look
look can be given an parameter to get a discription to get a visual disciption of an object in the current room.
if look is not given any parameters it will visually discripe the current room, highlighting any objects mentioned
in the output text, that could be looked at specifically later with look object_name


## GUI
The GUI is made of three sections. 

### Input Section
At the bottom is a cli to input commands. 
Typing in commands will assume and show possible commands and arguments.

### Information / Utils Section
Obove the CLI-Interface will be a kind of navbar, that will contain buttons like "Stats", "Inventory" and "Settings"
to switch between views. Over the Buttons will the selected view be shown, to display informations of the category.

### Output Section
Obove that will be the biggest section, containing the output of the game. It will be scrollable and resemble a chat,
like with an ai or a normal cli terminal, where given commands can be seen on the right, and the output on the left.


## Entities

### Stats
Monsters, Characters and the Player have the following stats: Strength, Constitution, Dexterity, Intelligence, Willpower, Intuition

### Body
Each entity has a body consisting out of different parts depending on the type of creature. The parts are attached to each other, if a part in a chain is lost completely, you lose all attached parts: if your should gets cut off, you loos the attached arm and hand too.
Instead of a health bar, a entity is dead if certian
conditions are met: Brain / Heart is destroyd, Blood loss or fatigue / starving. When entities are trying to do things, stats are multiplied by the
condition of the bodyparts involved. Reading and Understanding is multiplied by Brain-condition, Walking is multiplied by both Legs. But all bodyparts
involved only add up to 100%, so having two legs doens't lead to 200% Walking, it's 100%. So 100% is given when all parts involved are at max. Loss of 
one leg leads to 50% for example.
Additionally, there is some kind of hidden bars. Blood amount, Fatigue and Sustinance. 
These also multiply the quality of tasks.
A lifting check would look like this: 
All variables here usually are floats between 1 and 0, like 1 means maximum blood, and 0 means bleeded out
involved_parts_quality = involved_parts_quality_sum / invoved_parts_amount
consciousness = (blood * (1-fatigue) * minimum(1, 0.2+sustinance*2)) /3
lifting_quality = strength * involved_parts_quality * consciousness
and then you could check lifting_quality against what quality is needed for the check.

```
part_type: enum(eye,leg,arm,...) = arm
injuries = []
attached_parts = [Hand]
```

### Injuries
In combat, conditions or through enviromental means a entities Bodyparts can get injured. Injuries reduce the quality of a part until healed (if able).
The game has a long list of standart injuries, that are mapped to the parts that can get inflicted by this. (An Eye cannot be broken, a leg can).
Some parts also contain special injuries that can only apply to themselfs, if a injurie is caused a fitting injurie is chosen out of the possible pool.
Injuries have a quality_deficit that reduces the quality of that part by that amount. The quality of a part cant get reduced to less then 0 even if more
Injuries apply more then the maximum amount.
Healable injurie contains a heling_treshhold that has to be filled to heal trying to reach 100, unhealabe injuries have the healabe bool on false and will never be healed.
Also the injurie has a healing_speed modifier, that is multiplying the healing
A healing check is done after each action taken. That healing is applied to the healing_treshhold value.
healing check -> healing = constitution * blood * minimun(1, sustinance*2)
              -> healing_treshold += healing * healing_speed * maximum(0.8, willpower*2)
              -> sustinance -= healing*0.1
It also contins a float between 1 and 0 that controles the amount "relieve" the healing does to the quality_deficit. A 50/100 heald would with relieve 1 would only apply half the quality_deficit.
Injuries also have a followup variable that conatins a followup injurie or nothing if the healing is complete.

```
target_parts: Array = [leg,arm]
quality_deficit: float = 0.2
healable: bool = true
healing_threshold: int = 0
healing_speed: float = 1.0
relieve_factor: float = 1.0
followup_injury: Injurie = null
```

### Inventory
What can be carried will be determend by volume. 
Equipped Items fill hands, each hand has a volume treshhold that determins how much can be hold with them.
Additional space can only be gained by backpacks or other stashing equpment, that can be equipped without blocking a hand.
the weight is added up to calculate the amount of sustinance used per turn or movement action.
in addition if a specific weight value is met, like, weight_sum >= strength * 100, (weight_sum - strength * 100)/100 of fatigue is gained with each turn or action.
for this there should be specific functions added to calculate this automatically. like apply_inventory_sustinance_and_fatigue().