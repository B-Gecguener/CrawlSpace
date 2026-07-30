use crate::cmd_interpreter;
use crate::get_user_input;
use std::path::PathBuf;

pub fn run(level: PathBuf) {
<<<<<<< HEAD
    println!(
        "Loading {} ...",
        level.file_name().unwrap().to_string_lossy()
    );

    loop {
        cmd_interpreter::interpret_command(get_user_input());
    }
}
=======
    println!("Loading {} ...", level.file_name().unwrap().to_string_lossy());
    loop {
        let output: String = cmd_interpreter::interpret_command(get_user_input());
        print!("{}", output);
    };
}
>>>>>>> refs/remotes/origin/main
