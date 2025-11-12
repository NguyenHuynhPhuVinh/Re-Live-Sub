import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { FileVideo, Loader2, Subtitles } from "lucide-react";

interface Video {
  name: string;
  path: string;
  size: number;
  created_at: string;
}

export default function VideoList() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingTasks, setProcessingTasks] = useState<Set<string>>(
    new Set()
  );

  useEffect(() => {
    loadVideos();
    const interval = setInterval(loadVideos, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadVideos = async () => {
    try {
      const data = await invoke<Video[]>("list_recordings");
      setVideos(data);
    } catch (err) {
      console.error("Error loading videos:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSRT = async (videoPath: string) => {
    setProcessingTasks((prev) => new Set(prev).add(videoPath));

    try {
      await invoke("generate_srt", {
        videoPath,
        language: "vi",
      });

      // Poll for completion
      setTimeout(() => {
        setProcessingTasks((prev) => {
          const next = new Set(prev);
          next.delete(videoPath);
          return next;
        });
      }, 5000);
    } catch (err) {
      console.error("Error generating SRT:", err);
      setProcessingTasks((prev) => {
        const next = new Set(prev);
        next.delete(videoPath);
        return next;
      });
    }
  };

  const formatSize = (bytes: number) => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleString("vi-VN");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-20">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Video đã ghi</CardTitle>
        <CardDescription>
          Tổng cộng {videos.length} video trong thư viện
        </CardDescription>
      </CardHeader>

      <CardContent>
        {videos.length === 0 ? (
          <div className="text-center py-16 space-y-4">
            <FileVideo className="w-16 h-16 mx-auto text-muted-foreground opacity-50" />
            <div className="space-y-2">
              <p className="text-lg font-semibold text-muted-foreground">
                Chưa có video nào
              </p>
              <p className="text-sm text-muted-foreground">
                Bắt đầu ghi stream để tạo video đầu tiên
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {videos.map((video) => (
              <div
                key={video.path}
                className="flex items-center justify-between p-6 bg-secondary rounded-xl border-2 border-border hover:border-primary transition-colors"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center border-2 border-primary/20">
                    <FileVideo className="w-6 h-6 text-primary" />
                  </div>

                  <div className="flex-1 min-w-0 space-y-1">
                    <p className="font-semibold text-foreground truncate text-base">
                      {video.name}
                    </p>
                    <p className="text-sm text-muted-foreground font-medium">
                      {formatSize(video.size)} • {formatDate(video.created_at)}
                    </p>
                  </div>
                </div>

                <Button
                  size="lg"
                  onClick={() => handleGenerateSRT(video.path)}
                  disabled={processingTasks.has(video.path)}
                  variant={
                    processingTasks.has(video.path) ? "secondary" : "default"
                  }
                  className="ml-4"
                >
                  {processingTasks.has(video.path) ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Đang xử lý...
                    </>
                  ) : (
                    <>
                      <Subtitles className="w-5 h-5" />
                      Tạo phụ đề
                    </>
                  )}
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
