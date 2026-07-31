# Folder Structure Example:

/data/
  /lvl_mvp/
    /rooms/
      startroom.json
      hallway.json
      crypt.json
      hallway2.json
      staircase.json
      hallway3.json
      crypt2.json
      ...
    /exits/
      door.json
      door2.json
      crawlspace.json
      trapdoor.json
      door3.json
      hole.json
      ...
    /entities/
      goblin.json
      goblin2.json
      goblin3.json
      dragon.json
      hobo.json
      hobo2.json
    /objects/
      flask.json
      sword.json
      sword2.json
      book.json
      necronomicon.json
      ...
  /lvl_01/
    ...

# JSON Structure:

## Rooms
```json
{
    "id": "start", // This has to be EXACTLY the same string like the filename
    "name": "Dungeon Entrance", // Ingame Name
    "fragments": {
      "see": ["dark stone entrance", "cracks in the walls"],
      "hear": ["footsteps echo against stone"],
      "smell": ["stale air"],
      "feel": ["rough stone surface"]
    },
    "exits": ["door","trapdoor","door2"],
    "objects": ["sword12","torch4","Necronomicon"],
    "creatures": ["giant_spider","giant_spider2"]
}
```

to find the exits for example that are mentioned here: "door", "trapdoor" and "door2", the game cats them like this: "data/rooms/"+"door"+".json" 
to find the file. So the id of the objects are thier file-names

## Exits
```json
{

    "id": "crawlspace", // This has to be EXACTLY the same string like the filename
    "name": "Crawlspace", // Ingame Name
    "room_a": "startroom",
    "room_b": "hallway",
    "a": {
        "fragments": {
            "see": ["a hole at the bottom of the wall"],
            "hear": ["a faint breeze of fresh air"],
            "smell": ["dust in the air"],
            "feel": ["rough stone surface"]
        },
        "use_requirements": ["key1"],
        "check_requirements": ["light"]
    },
    "b": {
        "fragments": {
            "see": ["a hole at the bottom of the wall"],
            "hear": ["a faint breeze of fresh air"],
            "smell": ["dust in the air"],
            "feel": ["rough stone surface"]
        },
        "use_requirements": ["key1"],
        "check_requirements": ["light"]
    },
    
}
```

## Objects

## Entities
