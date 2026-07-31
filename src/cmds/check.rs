use crate::game_loop::GameState;
use crate::game_loop::Level;
use crate::world::room::Room;
use crate::world::room::Fragments;

pub fn execute(args: Vec<String>, state: &GameState) -> String {

    let room: Room = state.level.rooms.get(&state.current_room).expect("").clone();
    let mut output: String = "".to_string();

    output.push_str("\n\nYou see:\n");
    for see_frg in room.fragments.see {
        output.push_str(&see_frg);
        output.push_str("\n");
    }

    output.push_str("\n\nYou hear:\n");
    for hear_frg in room.fragments.hear {
        output.push_str(&hear_frg);
        output.push_str("\n");   
    }

    output.push_str("\n\nYou smell:\n");
    for smell_frg in room.fragments.smell {
        output.push_str(&smell_frg);
        output.push_str("\n");
    }

    output.push_str("\n\nYou feel:\n");
    for feel_frg in room.fragments.feel {
        output.push_str(&feel_frg);
        output.push_str("\n");
    }
    
    output
}