mod cmd_interpreter;
mod game_loop;
mod game_start;

use game_start::game_start;

fn main() {
    let level = game_start();

    game_loop::run(level);
}
