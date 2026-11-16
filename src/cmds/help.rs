use crate::game_loop::GameState;

pub fn execute(args: Vec<String>, state: &mut GameState) -> String {
    if args.is_empty() {
        "
        help - help [command_name] - explains command, lists all if no command_name given
        check - check [object_name] - discribes the object or the room if no object given based on your senses
        move - move [exit_name] - moves you through the given exit into the connected room
        ".into()
    } else {
        "Showing help".into()
    }
}
