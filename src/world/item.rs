use serde::{Deserialize, Serialize};
use serde_json;
use std::{
    error::Error,
    fs::File,
    path::PathBuf,
};

#[derive(Serialize,Deserialize)]
pub struct Item {
    pub id: String,
    pub name: String,
}

pub fn load_item(item: String, level: PathBuf) -> Result<Item, Box<dyn Error>> {

    let path = level
        .join("items")
        .join(format!("{item}.json"));

    let file = File::open(path)?;

    let i = serde_json::from_reader(file)?;

    Ok(i)
}