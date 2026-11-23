use crate::game_loop::GameState;
use crate::world::exit::Exit;
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
                output.push_str("You see ");
                for see_frg in room.fragments.see {
                    output.push_str(&see_frg);
                    output.push_str(". \n");
                }
            }
            "hear" => {
                output.push_str("You hear ");
                for hear_frg in room.fragments.hear {
                    output.push_str(&hear_frg);
                    output.push_str(". \n");
                }
            }
            "smell" => {
                output.push_str("You smell ");
                for smell_frg in room.fragments.smell {
                    output.push_str(&smell_frg);
                    output.push_str(". \n");
                }
            }
            "feel" => {
                output.push_str("You feel ");
                for feel_frg in room.fragments.feel {
                    output.push_str(&feel_frg);
                    output.push_str(". \n");
                }
            }
            _ => {
                output.push_str("The option ");
                output.push_str(sense);
                output.push_str(" does not exist for the check command.\n");
            }
        }
    } else {
        output.push_str("You see ");
        output.push_str(&room.fragments.see[0]);
        output.push_str(".\n");
        output.push_str("You hear ");
        output.push_str(&room.fragments.hear[0]);
        output.push_str(".\n");
    }

    output.push_str("\nYou can exit this room through \n");
    for exit in room.exits {
        let exit_object: &Exit = state.level.exits.get(&exit).expect("");
        output.push_str(&exit_object.name);
    }

    output
}
