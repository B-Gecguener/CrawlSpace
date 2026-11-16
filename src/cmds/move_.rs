use crate::world::exit::Exit;
use crate::world::room::Room;
use std::collections::HashMap;
use std::collections::hash_map::Keys;

use crate::game_loop::GameState;

pub fn execute(args: Vec<String>, state: &mut GameState) -> String {
    let input: String = args.join(" ");

    let current_room_id: String = state.current_room.clone();
    let exit_ids: Vec<String> = state
        .level
        .rooms
        .get(&current_room_id)
        .expect("no current room")
        .exits
        .clone();

    for exit_id in exit_ids {
        let exit = state
            .level
            .exits
            .get(&exit_id)
            .expect("exit does not exist");

        if exit.name == input {
            let target_room = if exit.room_a == current_room_id {
                exit.room_b.clone()
            } else {
                exit.room_a.clone()
            };

            state.current_room = target_room;

            return format!("Moving through {}", input).to_string();
        }
    }

    return format!("There is no exit named {}", input).to_string();
}
