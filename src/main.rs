use std::{fs, io};

fn main() {
    println!("Hello, Adventurer!");
    println!("Welcome to CrawlSpace.");
    println!("Choose your level:");
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

    println!("You entered: {}", input);
    return input.to_string();
}
