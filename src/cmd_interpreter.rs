// cmd_interpreter ist dafür zuständig commands zu erkennen und auszuführen

use std::{collections::HashMap/*, os::raw::c_double*/};
use crate::game_loop::GameState;

pub type CommandFn = fn(Vec<String>,&GameState) -> String;

pub fn interpret_command(cmd: String, cmd_map: &HashMap<String, CommandFn>, state: &GameState) -> String {
    let mut parts = cmd.split_whitespace();

    let command = match parts.next() {
        Some(cmd) => cmd,
        None => return "No command entered.".to_string(),
    };

    let args: Vec<String> = parts.map(|s| s.to_string()).collect();
    
    match cmd_map.get(command) {
        Some(function) => function(args, &state),
        None => format!("Unknown command '{}'. Type 'help' for a list of commands.", command),
    }
}