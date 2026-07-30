use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use crate::room::Fragments;

#[derive(Serialize, Deserialize)]
struct Exit {
    name: String,
    room_A: String,
    room_B: String,
    A: ExitSide,
    B: ExitSide,
}

#[derive(Serialize, Deserialize)]
struct ExitSide {
    fragments: Fragments,
    use_requirements: Vec<String>,
    check_requirements: Vec<String>,
}

pub fn load_exit(exit: String, level: String) -> Exit {

    let path: PathBuf = 
        "/data/"
        .to_string()
        .join(level)
        .join("exits")
        .join(exit+".json");

    let file = File::open(path);

    let e: Exit = serde_json::from_str(file)?;
    
    e
}