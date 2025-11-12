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
    <div className="min-h-screen bg-[#0a0e27]">
      <div className="container mx-auto p-8 max-w-5xl">
        {/* Header */}
        <header className="mb-10">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">
                Live Stream Subtitle System
              </h1>
              <p className="text-[#8b92b0]">
                Tự động ghi stream, tạo phụ đề và dịch sang tiếng Việt
              </p>
            </div>

            {backendStatus === "online" && (
              <div className="flex items-center gap-2 px-4 py-2 bg-[#10b981] text-white rounded-lg">
                <div className="w-2 h-2 bg-white rounded-full" />
                <span className="text-sm font-medium">Backend Online</span>
              </div>
            )}

            {backendStatus === "offline" && (
              <div className="flex items-center gap-2 px-4 py-2 bg-[#ef4444] text-white rounded-lg">
                <div className="w-2 h-2 bg-white rounded-full" />
                <span className="text-sm font-medium">Backend Offline</span>
              </div>
            )}
          </div>

          {backendStatus === "offline" && (
            <Alert className="bg-[#1e1b4b] border-2 border-[#ef4444]">
              <AlertDescription className="text-[#fca5a5]">
                ⚠️ Backend offline. Chạy:{" "}
                <code className="bg-[#0a0e27] px-2 py-1 rounded text-white">
                  cd backend && python main.py
                </code>
              </AlertDescription>
            </Alert>
          )}
        </header>

        {/* Navigation Tabs */}
        <Tabs defaultValue="record" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-[#1e1b4b] p-1 rounded-lg mb-8">
            <TabsTrigger
              value="record"
              className="data-[state=active]:bg-[#6366f1] data-[state=active]:text-white text-[#8b92b0] rounded-md py-3 font-medium transition-colors"
            >
              📹 Ghi Stream
            </TabsTrigger>
            <TabsTrigger
              value="videos"
              className="data-[state=active]:bg-[#6366f1] data-[state=active]:text-white text-[#8b92b0] rounded-md py-3 font-medium transition-colors"
            >
              📁 Danh Sách Video
            </TabsTrigger>
          </TabsList>

          <TabsContent value="record">
            <StreamRecorder backendOnline={backendStatus === "online"} />
          </TabsContent>

          <TabsContent value="videos">
            <VideoList />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;
