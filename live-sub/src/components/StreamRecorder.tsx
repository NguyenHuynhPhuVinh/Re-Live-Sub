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
    <Card>
      <CardHeader>
        <CardTitle>Ghi Stream YouTube</CardTitle>
        <CardDescription>
          Nhập link livestream để bắt đầu ghi và tự động tạo phụ đề với AI
        </CardDescription>
      </CardHeader>

      <CardContent>
        {error && (
          <Alert className="bg-destructive/10 border-2 border-destructive mb-6">
            <AlertDescription className="text-destructive font-medium">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-6">
          {/* URL Input */}
          <div className="space-y-3">
            <Label htmlFor="url" className="text-base font-semibold">
              URL Stream
            </Label>
            <Input
              id="url"
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isRecording || !backendOnline}
              className="h-12 text-base border-2"
            />
          </div>

          {/* Duration Input */}
          <div className="space-y-3">
            <Label htmlFor="duration" className="text-base font-semibold">
              Độ dài mỗi segment
            </Label>
            <Input
              id="duration"
              type="number"
              value={segmentDuration}
              onChange={(e) => setSegmentDuration(Number(e.target.value))}
              disabled={isRecording || !backendOnline}
              className="h-12 text-base border-2"
            />
            <p className="text-sm text-muted-foreground font-medium">
              {segmentDuration} giây = {Math.floor(segmentDuration / 60)} phút{" "}
              {segmentDuration % 60} giây
            </p>
          </div>

          {/* Status Display */}
          {status && (
            <div className="flex items-center gap-3 px-4 py-3 bg-primary/10 rounded-xl border-2 border-primary">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              <span className="font-semibold text-primary">{status}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4">
            {!isRecording ? (
              <Button
                onClick={handleStart}
                disabled={!backendOnline}
                variant="success"
                size="lg"
                className="flex-1"
              >
                <Play className="w-5 h-5" />
                Bắt đầu ghi
              </Button>
            ) : (
              <Button
                onClick={handleStop}
                variant="destructive"
                size="lg"
                className="flex-1"
              >
                <Square className="w-5 h-5" />
                Dừng ghi
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
