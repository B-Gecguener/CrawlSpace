use crate::game_loop::GameState;
use crate::game_loop::Level;
use crate::world::exit::Exit;
use crate::world::room::Fragments;
use crate::world::room::Room;

pub fn execute(args: Vec<String>, state: &mut GameState) -> String {
    let room: Room = state
        .level
        .rooms
        .get(&state.current_room)
        .expect("")
        .clone();
    let mut output: String = "".to_string();

    if !args.is_empty() {
        let sense: &str = args[0].as_str();
        match sense {
            "see" => {
                output.push_str("\n\nYou see:\n");
                for see_frg in room.fragments.see {
                    output.push_str(&see_frg);
                    output.push_str("\n");
                }
            },
            "hear" => {
                output.push_str("\n\nYou hear:\n");
                for hear_frg in room.fragments.hear {
                    output.push_str(&hear_frg);
                    output.push_str("\n");
                }
            },
            "smell" => {
                output.push_str("\n\nYou smell:\n");
                for smell_frg in room.fragments.smell {
                    output.push_str(&smell_frg);
                    output.push_str("\n");
                }
            },
            "feel" => {
                output.push_str("\n\nYou feel:\n");
                for feel_frg in room.fragments.feel {
                    output.push_str(&feel_frg);
                    output.push_str("\n");
                }
            },
            _ => println!(),
        }
    } else {
        output.push_str("\n\nYou see ");
    }

    output.push_str("\n\nYou can exit this room through \n");
    for exit in room.exits {
        let exit_object: &Exit = state.level.exits.get(&exit).expect("");
        output.push_str(&exit_object.name);
    }

    output
}
