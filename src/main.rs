use std::collections::HashMap;
use std::{fs, io};

fn main() {
    println!("Hello, Adventurer!");
    println!("Welcome to CrawlSpace.");

    choose_level();
    get_user_input();
}

fn get_user_input() -> String {
    let mut input = String::new();

    println!("Enter something:");

    io::stdin()
        .read_line(&mut input)
        .expect("Failed to read line");

    // input includes the trailing newline, so trim it
    let input = input.trim();
    return input.to_string();
}

fn get_levels() -> HashMap<std::ffi::OsString, fs::DirEntry> {
    let entries = fs::read_dir("data").expect("Failed to read directory");
    let mut levels = HashMap::new();
    for entry in entries {
        let entry = entry.expect("Failed to read entry");
        let file_name = entry.file_name();
        levels.insert(file_name, entry);
    }
    return levels;
}

fn choose_level() {
    let levels = get_levels();

    print!("Choose your level: ");
    let level_names = levels.keys();
    for name in level_names {
        println!("{}", name.to_string_lossy())
    }
    let input = get_user_input();
    for name in level_names {
        if (name == input) {}
    }
}
