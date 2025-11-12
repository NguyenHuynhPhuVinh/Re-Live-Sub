import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { Loader2, Play, Square } from "lucide-react";

interface StreamRecorderProps {
  backendOnline: boolean;
}

export default function StreamRecorder({ backendOnline }: StreamRecorderProps) {
  const [url, setUrl] = useState("");
  const [segmentDuration, setSegmentDuration] = useState(60);
  const [isRecording, setIsRecording] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");

  const handleStart = async () => {
    if (!url.trim()) {
      setError("Vui lòng nhập URL stream");
      return;
    }

    setError(null);
    setIsRecording(true);
    setStatus("Đang khởi động...");

    try {
      const response = await invoke<{ task_id: string; status: string }>(
        "start_recording",
        {
          url: url.trim(),
          segmentDuration,
          enhanceQuality: false,
        }
      );

      setTaskId(response.task_id);
      setStatus("Đang ghi stream...");

      // Poll status
      const interval = setInterval(async () => {
        try {
          const statusData = await invoke("get_recording_status", {
            taskId: response.task_id,
          });
          console.log("Status:", statusData);
        } catch (err) {
          console.error("Status check error:", err);
        }
      }, 3000);

      // Store interval ID for cleanup
      (window as any).statusInterval = interval;
    } catch (err) {
      setError(`Lỗi: ${err}`);
      setIsRecording(false);
      setStatus("");
    }
  };

  const handleStop = async () => {
    if (!taskId) return;

    try {
      await invoke("stop_recording", { taskId });
      setIsRecording(false);
      setStatus("Đã dừng");
      setTaskId(null);

      // Clear interval
      if ((window as any).statusInterval) {
        clearInterval((window as any).statusInterval);
      }
    } catch (err) {
      setError(`Lỗi khi dừng: ${err}`);
    }
  };

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Ghi Stream YouTube</CardTitle>
        <CardDescription className="text-slate-400">
          Nhập link livestream để bắt đầu ghi và tự động tạo phụ đề
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert className="bg-red-500/20 border-red-500">
            <AlertDescription className="text-red-200">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          <Label htmlFor="url" className="text-white">
            URL Stream
          </Label>
          <Input
            id="url"
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isRecording || !backendOnline}
            className="bg-slate-900/50 border-slate-600 text-white"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="duration" className="text-white">
            Độ dài mỗi segment (giây)
          </Label>
          <Input
            id="duration"
            type="number"
            value={segmentDuration}
            onChange={(e) => setSegmentDuration(Number(e.target.value))}
            disabled={isRecording || !backendOnline}
            className="bg-slate-900/50 border-slate-600 text-white"
          />
          <p className="text-sm text-slate-400">
            {segmentDuration} giây = {Math.floor(segmentDuration / 60)} phút{" "}
            {segmentDuration % 60} giây
          </p>
        </div>

        {status && (
          <div className="flex items-center gap-2 text-blue-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>{status}</span>
          </div>
        )}

        <div className="flex gap-2">
          {!isRecording ? (
            <Button
              onClick={handleStart}
              disabled={!backendOnline}
              className="bg-green-600 hover:bg-green-700"
            >
              <Play className="w-4 h-4 mr-2" />
              Bắt đầu ghi
            </Button>
          ) : (
            <Button onClick={handleStop} variant="destructive">
              <Square className="w-4 h-4 mr-2" />
              Dừng ghi
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
