use crate::cmds::check;
use crate::game_loop::GameState;

pub fn execute(args: Vec<String>, state: &mut GameState) -> String {
    let input: String = args.join(" ");
    let mut output: String = "".to_string();

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
            output.push_str(&format!("Moving through {}\n", input));
            // calls check
            output.push_str(&format!("{}", check::execute(Vec::new(), state)));

            return output;
        }
    }
    return format!("There is no exit named {}", input);
}
