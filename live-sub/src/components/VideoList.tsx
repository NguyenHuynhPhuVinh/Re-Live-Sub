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
        <Loader2 className="w-8 h-8 animate-spin text-[#6366f1]" />
      </div>
    );
  }

  return (
    <Card className="bg-[#1e1b4b] border-2 border-[#312e81]">
      <CardHeader>
        <CardTitle className="text-white text-xl">Video Đã Ghi</CardTitle>
        <CardDescription className="text-[#8b92b0]">
          Tổng cộng {videos.length} video
        </CardDescription>
      </CardHeader>
      <CardContent>
        {videos.length === 0 ? (
          <div className="text-center py-12">
            <FileVideo className="w-16 h-16 text-[#4c1d95] mx-auto mb-4" />
            <p className="text-[#8b92b0] text-lg">Chưa có video nào</p>
            <p className="text-[#6b7280] text-sm mt-2">
              Bắt đầu ghi stream để tạo video
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {videos.map((video) => (
              <div
                key={video.path}
                className="flex items-center justify-between p-5 bg-[#0a0e27] border-2 border-[#312e81] rounded-lg hover:border-[#4c1d95] transition-colors"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="w-12 h-12 bg-[#1e1b4b] rounded-lg flex items-center justify-center flex-shrink-0">
                    <FileVideo className="w-6 h-6 text-[#6366f1]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-semibold truncate text-base">
                      {video.name}
                    </p>
                    <p className="text-sm text-[#8b92b0] mt-1">
                      {formatSize(video.size)} • {formatDate(video.created_at)}
                    </p>
                  </div>
                </div>

                <Button
                  onClick={() => handleGenerateSRT(video.path)}
                  disabled={processingTasks.has(video.path)}
                  className="bg-[#8b5cf6] hover:bg-[#7c3aed] text-white h-11 px-6 rounded-lg font-medium transition-colors disabled:bg-[#374151] disabled:text-[#6b7280] flex-shrink-0"
                >
                  {processingTasks.has(video.path) ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Đang xử lý...
                    </>
                  ) : (
                    <>
                      <Subtitles className="w-4 h-4 mr-2" />
                      Tạo Phụ Đề
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
