use serde::{Deserialize, Serialize};
use serde_json;
use std::{
    error::Error,
    fs::File,
    path::PathBuf,
};

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

fn load_room(room: String, level: PathBuf) -> Result<Room, Box<dyn Error>> {

    let path = level
        .join("rooms")
        .join(format!("{room}.json"));

    let file = File::open(path)?;

    let room = serde_json::from_reader(file)?;

    Ok(room)
}