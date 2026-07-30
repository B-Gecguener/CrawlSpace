use serde::{Deserialize, Serialize};
use serde_json;
use std::path::PathBuf;
use std::fs::File;

#[derive(Serialize,Deserialize)]
pub struct Item {
    name: String,
}

pub fn load_item(item: String, level: PathBuf) -> Item {

    let path: PathBuf = 
        level
        .join("items")
        .join(item+".json");

    let file = File::open(path);

    let i: Item = serde_json::from_str(file)?;
    
    i
}