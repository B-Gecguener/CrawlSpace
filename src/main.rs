mod cmd_interpreter;
mod game_loop;
mod game_start;
mod helper;

use game_start::game_start;

fn main() {
    let level = game_start();

    game_loop::run(level);
}
