import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import StreamRecorder from "./components/StreamRecorder";
import VideoList from "./components/VideoList";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";

function App() {
  const [backendStatus, setBackendStatus] = useState<
    "checking" | "online" | "offline"
  >("checking");

  useEffect(() => {
    checkBackend();
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkBackend = async () => {
    try {
      const isHealthy = await invoke<boolean>("check_backend_health");
      setBackendStatus(isHealthy ? "online" : "offline");
    } catch {
      setBackendStatus("offline");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto p-6">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🎬 Live Stream Subtitle System
          </h1>
          <p className="text-slate-300">
            Tự động ghi stream, tạo phụ đề và dịch sang tiếng Việt
          </p>

          {backendStatus === "offline" && (
            <Alert className="mt-4 bg-red-500/20 border-red-500">
              <AlertDescription className="text-red-200">
                ⚠️ Backend offline. Chạy:{" "}
                <code className="bg-black/30 px-2 py-1 rounded">
                  cd backend && python main.py
                </code>
              </AlertDescription>
            </Alert>
          )}

          {backendStatus === "online" && (
            <div className="mt-4 flex items-center gap-2 text-green-400">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm">Backend đang chạy</span>
            </div>
          )}
        </header>

        <Tabs defaultValue="record" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-slate-800/50">
            <TabsTrigger value="record">📹 Ghi Stream</TabsTrigger>
            <TabsTrigger value="videos">📁 Video</TabsTrigger>
          </TabsList>

          <TabsContent value="record" className="mt-6">
            <StreamRecorder backendOnline={backendStatus === "online"} />
          </TabsContent>

          <TabsContent value="videos" className="mt-6">
            <VideoList />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;
