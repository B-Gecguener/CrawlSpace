use std::path::PathBuf;
use crate::get_user_input;
use crate::cmd_interpreter;

pub fn run(level: PathBuf) {
    println!("Loading {} ...", level.file_name().unwrap().to_string_lossy());
    loop {
        let output: String = cmd_interpreter::interpret_command(get_user_input());
        print!("{}", output);
    };
}