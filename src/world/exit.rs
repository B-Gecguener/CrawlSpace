use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::fs::File;
use crate::world::room::Fragments;

#[derive(Serialize,Deserialize)]
pub struct Exit {
    name: String,
    room_A: String,
    room_B: String,
    A: ExitSide,
    B: ExitSide,
}

#[derive(Serialize, Deserialize)]
pub struct ExitSide {
    fragments: Fragments,
    use_requirements: Vec<String>,
    check_requirements: Vec<String>,
}

pub fn load_exit(exit: String, level: PathBuf) -> Exit {

    let path: PathBuf = 
        level
        .join("exits")
        .join(exit+".json");

    let file = File::open(path);

    let e: Exit = serde_json::from_str(file)?;
    
    e
}