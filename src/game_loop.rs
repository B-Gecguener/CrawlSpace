use crate::cmd_interpreter;
use crate::game_start::game_start;
use crate::helper::get_user_input;
use crate::world::exit::Exit;
use crate::world::item::Item;
use crate::world::room::Room;
use crate::world::{exit::load_exit, item::load_item, room::load_room};
use std::collections::HashMap;
use std::path::PathBuf;

pub struct GameState {
    pub current_room: String,
    pub level: Level,
}

pub struct Level {
    pub rooms: HashMap<String, Room>,
    pub exits: HashMap<String, Exit>,
    pub items: HashMap<String, Item>,
}

pub fn run() {
    let (level, command_map) = game_start(); // added game_start here

    let mut state: GameState = create_level(level);
    println!(
        "{}",
        cmd_interpreter::interpret_command("check".to_string(), &command_map, &mut state)
    );
    // getting all commands in a sorted list
    let mut names: Vec<&str> = command_map.keys().map(|k| k.as_str()).collect();
    names.sort();
    println!(
        "what do you want to do? your available options are: {}\n",
        names.join(", ")
    );
    // Game loop
    loop {
        let output: String =
            cmd_interpreter::interpret_command(get_user_input(), &command_map, &mut state);
        println!("{}", output);
    }
}

fn create_level(lvl: PathBuf) -> GameState {
    let start_room =
        load_room("start".to_string(), lvl.clone()).expect("Could not load start room");

    let mut game_state = GameState {
        current_room: "start".to_string(),

        level: Level {
            rooms: HashMap::new(),
            exits: HashMap::new(),
            items: HashMap::new(),
        },
    };

    game_state
        .level
        .rooms
        .insert(start_room.id.clone(), start_room.clone());

    for exit_name in &start_room.exits {
        let exit = load_exit(exit_name.clone(), lvl.clone()).expect("Could not load exit");

        let other_room = if exit.room_a == start_room.id {
            &exit.room_b
        } else {
            &exit.room_a
        };

        if !game_state.level.rooms.contains_key(other_room) {
            let room =
                load_room(other_room.clone(), lvl.clone()).expect("Could not load connected room");

            game_state.level.rooms.insert(room.id.clone(), room);
        }

        game_state.level.exits.insert(exit.id.clone(), exit);
    }

    game_state
}
