use crate::cmd_interpreter;
use crate::cmd_interpreter::CommandFn;
use crate::helper::get_user_input;
use crate::cmds;
use crate::game_start::game_start;

use std::{
    path::PathBuf,
    collections::HashMap,
};

struct GameState {
    current_room: String,
    level: Level,
}

struct Level {
    rooms: Vec<Room>,
    exits: Vec<Exit>,
    items: Vec<Items>,
}

pub fn run() {
    
    let (level, command_map) = game_start(); // added game_start here
    println!(
        "Start loading {} ...",
        level.file_name().unwrap().to_string_lossy()
    );
    
    let state: GameState = GameState { current_room: "start".to_string(), };
    
    // Game loop
    loop {
        let output: String = cmd_interpreter::interpret_command(get_user_input(), &command_map);
        println!("{}", output);
    };
}


