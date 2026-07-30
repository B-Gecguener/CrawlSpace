use crate::world::room::Room;
use crate::world::exit::Exit;
use crate::world::item::Item;
use crate::game_start::game_start;
use crate::helper::get_user_input;
use crate::cmd_interpreter;

pub struct GameState {
    current_room: String,
    level: Level,
}

pub struct Level {
    rooms: Vec<Room>,
    exits: Vec<Exit>,
    items: Vec<Item>,
}

pub fn run() {
    
    let (level, command_map) = game_start(); // added game_start here
    println!(
        "Start loading {} ...",
        level.file_name().unwrap().to_string_lossy()
    );
    
    let state: GameState = GameState { 
        current_room: "start".to_string(), 
        level: Level { rooms: Vec::new(), exits: Vec::new(), items: Vec::new() }
    };
    
    // Game loop
    loop {
        let output: String = cmd_interpreter::interpret_command(get_user_input(), &command_map, &state);
        println!("{}", output);
    };
}


