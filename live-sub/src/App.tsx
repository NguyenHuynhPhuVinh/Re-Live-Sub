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
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-8 py-12">
        {/* Header Section */}
        <header className="mb-12 space-y-6">
          <div className="space-y-3">
            <h1 className="text-5xl font-bold text-foreground tracking-tight">
              Live Stream Subtitle System
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed max-w-2xl">
              Tự động ghi stream, tạo phụ đề và dịch sang tiếng Việt với công
              nghệ AI
            </p>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center gap-4">
            {backendStatus === "checking" && (
              <div className="flex items-center gap-3 px-4 py-3 bg-muted rounded-xl border-2 border-border">
                <div className="w-2.5 h-2.5 bg-muted-foreground rounded-full animate-pulse" />
                <span className="text-sm font-medium text-muted-foreground">
                  Đang kiểm tra backend...
                </span>
              </div>
            )}

            {backendStatus === "offline" && (
              <Alert className="bg-destructive/10 border-2 border-destructive">
                <AlertDescription className="text-destructive-foreground font-medium">
                  ⚠️ Backend offline. Chạy:{" "}
                  <code className="bg-destructive/20 px-3 py-1.5 rounded-lg font-mono text-sm">
                    cd backend && python main.py
                  </code>
                </AlertDescription>
              </Alert>
            )}

            {backendStatus === "online" && (
              <div className="flex items-center gap-3 px-4 py-3 bg-success/10 rounded-xl border-2 border-success">
                <div className="w-2.5 h-2.5 bg-success rounded-full animate-pulse" />
                <span className="text-sm font-semibold text-success">
                  Backend đang hoạt động
                </span>
              </div>
            )}
          </div>
        </header>

        {/* Main Content */}
        <Tabs defaultValue="record" className="w-full space-y-8">
          <TabsList className="w-full max-w-md">
            <TabsTrigger value="record" className="flex-1">
              <span className="text-base">📹 Ghi Stream</span>
            </TabsTrigger>
            <TabsTrigger value="videos" className="flex-1">
              <span className="text-base">📁 Quản lý Video</span>
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
