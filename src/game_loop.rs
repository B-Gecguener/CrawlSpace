use crate::cmd_interpreter;
use crate::helper::get_user_input;
use std::path::PathBuf;

pub fn run(level: PathBuf) {
    println!(
        "Loading {} ...",
        level.file_name().unwrap().to_string_lossy()
    );
    loop {
        let output: String = cmd_interpreter::interpret_command(get_user_input());
        print!("{}", output);
    }
}
