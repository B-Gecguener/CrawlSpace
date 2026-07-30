use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use serde_json;
use std::fs::File;

#[derive(Serialize, Deserialize)]
pub struct Fragments {
    see: Vec<String>,
    hear: Vec<String>,
    smell: Vec<String>,
    feel: Vec<String>
}

#[derive(Serialize, Deserialize)]
pub struct Room {
    name: String,
    fragments: Fragments,
    exits: Vec<String>,
    objects: Vec<String>,
    creatures: Vec<String>
}

fn load_room(room: String, level: PathBuf) -> Room {

    let path: PathBuf = 
        level
        .join("rooms")
        .join(room+".json");

    let file = File::open(path);

    let r: Room = serde_json::from_str(file)?;
    
    r
}