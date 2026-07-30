use serde::{Deserialize, Serialize};
use serde_json;
use std::path::PathBuf;
use crate::room::Fragments;

#[derive(Serialize,Deserialize)]
pub struct Item {
    name: String,
}

pub fn load_exit(exit: String, level: String) -> Item {

    let path: PathBuf = 
        "/data/"
        .to_string()
        .join(level)
        .join("exits")
        .join(exit+".json");

    let file = File::open(path);

    let i: Item = serde_json::from_str(file)?;
    
    i
}