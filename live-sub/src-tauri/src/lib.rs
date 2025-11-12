use serde::{Deserialize, Serialize};
use tauri::Manager;

#[derive(Debug, Serialize, Deserialize)]
struct StreamRequest {
    url: String,
    segment_duration: u32,
    enhance_quality: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct ApiResponse {
    task_id: Option<String>,
    status: String,
    message: Option<String>,
}

const API_BASE_URL: &str = "http://127.0.0.1:8000/api";

#[tauri::command]
async fn start_recording(url: String, segment_duration: u32, enhance_quality: bool) -> Result<ApiResponse, String> {
    let client = reqwest::Client::new();
    let request = StreamRequest {
        url,
        segment_duration,
        enhance_quality,
    };
    
    let response = client
        .post(format!("{}/stream/start", API_BASE_URL))
        .json(&request)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let result: ApiResponse = response.json().await.map_err(|e| e.to_string())?;
    Ok(result)
}

#[tauri::command]
async fn stop_recording(task_id: String) -> Result<ApiResponse, String> {
    let client = reqwest::Client::new();
    
    let response = client
        .post(format!("{}/stream/stop/{}", API_BASE_URL, task_id))
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let result: ApiResponse = response.json().await.map_err(|e| e.to_string())?;
    Ok(result)
}

#[tauri::command]
async fn get_recording_status(task_id: String) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    
    let response = client
        .get(format!("{}/stream/status/{}", API_BASE_URL, task_id))
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let result: serde_json::Value = response.json().await.map_err(|e| e.to_string())?;
    Ok(result)
}

#[tauri::command]
async fn list_recordings() -> Result<Vec<serde_json::Value>, String> {
    let client = reqwest::Client::new();
    
    let response = client
        .get(format!("{}/stream/list", API_BASE_URL))
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let result: Vec<serde_json::Value> = response.json().await.map_err(|e| e.to_string())?;
    Ok(result)
}

#[tauri::command]
async fn generate_srt(video_path: String, language: String) -> Result<ApiResponse, String> {
    let client = reqwest::Client::new();
    let request = serde_json::json!({
        "video_path": video_path,
        "language": language,
        "burn_subtitle": false
    });
    
    let response = client
        .post(format!("{}/processing/generate-srt", API_BASE_URL))
        .json(&request)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let result: ApiResponse = response.json().await.map_err(|e| e.to_string())?;
    Ok(result)
}

#[tauri::command]
async fn check_backend_health() -> Result<bool, String> {
    let client = reqwest::Client::new();
    
    match client.get("http://127.0.0.1:8000/health").send().await {
        Ok(_) => Ok(true),
        Err(_) => Ok(false),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            start_recording,
            stop_recording,
            get_recording_status,
            list_recordings,
            generate_srt,
            check_backend_health
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
