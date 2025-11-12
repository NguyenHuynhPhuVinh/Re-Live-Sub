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
      <div className="flex items-center justify-center p-12">
        <Loader2 className="w-8 h-8 animate-spin text-white" />
      </div>
    );
  }

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Video đã ghi</CardTitle>
        <CardDescription className="text-slate-400">
          {videos.length} video
        </CardDescription>
      </CardHeader>
      <CardContent>
        {videos.length === 0 ? (
          <p className="text-slate-400 text-center py-8">
            Chưa có video nào. Bắt đầu ghi stream để tạo video.
          </p>
        ) : (
          <div className="space-y-3">
            {videos.map((video) => (
              <div
                key={video.path}
                className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg border border-slate-700"
              >
                <div className="flex items-center gap-3 flex-1">
                  <FileVideo className="w-5 h-5 text-blue-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium truncate">
                      {video.name}
                    </p>
                    <p className="text-sm text-slate-400">
                      {formatSize(video.size)} • {formatDate(video.created_at)}
                    </p>
                  </div>
                </div>

                <Button
                  size="sm"
                  onClick={() => handleGenerateSRT(video.path)}
                  disabled={processingTasks.has(video.path)}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  {processingTasks.has(video.path) ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Đang xử lý...
                    </>
                  ) : (
                    <>
                      <Subtitles className="w-4 h-4 mr-2" />
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
