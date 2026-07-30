use crate::world::room::Room;
use crate::world::exit::Exit;
use crate::world::item::Item;
use std::collections::HashMap;
use std::path::PathBuf;
use crate::world::room::load_room;
use crate::game_start::game_start;
use crate::helper::get_user_input;
use crate::cmd_interpreter;

pub struct GameState {
    current_room: Room,
    level: Level,
}

pub struct Level {
    rooms: HashMap<String, Room>,
    exits: HashMap<String, Exit>,
    items: HashMap<String, Item>,
}

pub fn run() {
    
    let (level, command_map) = game_start(); // added game_start here
    println!(
        "Start loading {} ...",
        level.file_name().unwrap().to_string_lossy()
    );
    
    // Game loop
    loop {
        let output: String = cmd_interpreter::interpret_command(get_user_input(), &command_map, &state);
        println!("{}", output);
    };
}

fn create_level(lvl: PathBuf) {

    let start_room: Room = load_room("start".to_string(), lvl);

    let game_state: GameState { 
        current_room: start_room,
        level: Level { rooms: HashMap::new(), exits: HashMap::new(), items: HashMap::new() }
    };

    game_state.level.rooms.append(start_room);

    for exit in start_room.exits {
        if exit.room_a != start_room.id {

        }
    }
}


