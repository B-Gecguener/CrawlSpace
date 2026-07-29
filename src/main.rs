use std::{
    fs,
    io,
    path::PathBuf, // Besser weil OS unabhänig und funktioniert als path
};

fn main() {
    greet_user();

    let level = level_selection();

    println!("Selected level:");
    println!("{}", level.display());
}

fn greet_user() {
    println!("Hello, Adventurer!");
    println!("Welcome to CrawlSpace.");
}

fn get_user_input() -> String {
    let mut input = String::new();

    io::stdin()
        .read_line(&mut input)
        .expect("Failed to read input");

    input.trim().to_owned() // Der Rust-"Style", das letzte Statement ohne ";" wird automatisch returned
}

fn get_levels() -> Vec<PathBuf> {
    let mut levels = Vec::new();

    let entries = fs::read_dir("data")
        .expect("Could not open data directory");

    for entry in entries {
        let entry = entry.expect("Invalid directory entry");

        let path = entry.path();

        if path.is_dir() {
            levels.push(path);
        }
    }

    levels
}

fn level_selection() -> PathBuf {
    let levels: Vec<PathBuf> = get_levels();

    loop { // Rust mag "while true" nicht, loop ist anscheinden der weg für endlos-loops
        println!();
        println!("Available levels:");

        for level in &levels {
            println!(
                "- {}",
                level.file_name().unwrap().to_string_lossy()
            );
        }

        println!();
        println!("Choose a level:");

        let input: String = get_user_input();

        for level in &levels {
            let name = level
                .file_name()
                .unwrap()
                .to_string_lossy();

            if name == input {
                return level.clone();
            }
        }

        println!("Level '{}' does not exist.", input);
    }
}