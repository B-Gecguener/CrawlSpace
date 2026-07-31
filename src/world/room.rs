use serde::{Deserialize, Serialize};
use serde_json;
use std::{
    error::Error,
    fs::File,
    path::PathBuf,
};

#[derive(Serialize, Deserialize, Clone)]
pub struct Fragments {
    pub see: Vec<String>,
    pub hear: Vec<String>,
    pub smell: Vec<String>,
    pub feel: Vec<String>
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Room {
    pub id: String,
    pub name: String,
    pub fragments: Fragments,
    pub exits: Vec<String>,
    pub objects: Vec<String>,
    pub creatures: Vec<String>
}

pub fn load_room(room: String, level: PathBuf) -> Result<Room, Box<dyn Error>> {

    let path = level
        .join("rooms")
        .join(format!("{room}.json"));

    let file = File::open(path)?;

    let room = serde_json::from_reader(file)?;

    Ok(room)
}