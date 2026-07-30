use serde::{Deserialize, Serialize};
use crate::world::room::Fragments;
use serde_json;
use std::{
    error::Error,
    fs::File,
    path::PathBuf,
};

#[derive(Serialize,Deserialize)]
pub struct Exit {
    pub id: String,
    pub name: String,
    pub room_a: String,
    pub room_b: String,
    pub a: ExitSide,
    pub b: ExitSide,
}

#[derive(Serialize, Deserialize)]
pub struct ExitSide {
    fragments: Fragments,
    use_requirements: Vec<String>,
    check_requirements: Vec<String>,
}

pub fn load_exit(exit: String, level: PathBuf) -> Result<Exit, Box<dyn Error>> {

    let path = level
        .join("exits")
        .join(format!("{exit}.json"));

    let file = File::open(path)?;

    let e = serde_json::from_reader(file)?;

    Ok(e)
}