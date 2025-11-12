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
    <div className="space-y-6">
      {/* URL Input - Prominent at top */}
      <div className="bg-[#1e1b4b] border-2 border-[#312e81] rounded-lg p-6">
        <Label
          htmlFor="url"
          className="text-white text-lg font-semibold mb-3 block"
        >
          URL Stream YouTube
        </Label>
        <Input
          id="url"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={isRecording || !backendOnline}
          className="bg-[#0a0e27] border-2 border-[#4c1d95] text-white text-lg h-14 rounded-lg placeholder:text-[#6b7280] focus:border-[#6366f1] transition-colors"
        />
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="bg-[#1e1b4b] border-2 border-[#ef4444]">
          <AlertDescription className="text-[#fca5a5] font-medium">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Settings Card */}
      <Card className="bg-[#1e1b4b] border-2 border-[#312e81]">
        <CardHeader>
          <CardTitle className="text-white text-xl">Cài Đặt</CardTitle>
          <CardDescription className="text-[#8b92b0]">
            Tùy chỉnh thời lượng và các tham số ghi hình
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Duration Setting */}
          <div className="space-y-3">
            <Label
              htmlFor="duration"
              className="text-white font-medium text-base"
            >
              Thời lượng mỗi segment
            </Label>
            <div className="flex items-center gap-4">
              <Input
                id="duration"
                type="number"
                value={segmentDuration}
                onChange={(e) => setSegmentDuration(Number(e.target.value))}
                disabled={isRecording || !backendOnline}
                className="bg-[#0a0e27] border-2 border-[#4c1d95] text-white h-12 rounded-lg w-32 text-center text-lg font-semibold focus:border-[#6366f1] transition-colors"
              />
              <div className="flex-1">
                <p className="text-[#8b92b0] text-sm">
                  = {Math.floor(segmentDuration / 60)} phút{" "}
                  {segmentDuration % 60} giây
                </p>
              </div>
            </div>
          </div>

          {/* Status Display */}
          {status && (
            <div className="flex items-center gap-3 p-4 bg-[#0a0e27] border-2 border-[#3b82f6] rounded-lg">
              <Loader2 className="w-5 h-5 animate-spin text-[#3b82f6]" />
              <span className="text-white font-medium">{status}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            {!isRecording ? (
              <Button
                onClick={handleStart}
                disabled={!backendOnline}
                className="bg-[#10b981] hover:bg-[#059669] text-white h-12 px-8 rounded-lg font-semibold text-base transition-colors disabled:bg-[#374151] disabled:text-[#6b7280]"
              >
                <Play className="w-5 h-5 mr-2" />
                Bắt Đầu Ghi
              </Button>
            ) : (
              <Button
                onClick={handleStop}
                className="bg-[#ef4444] hover:bg-[#dc2626] text-white h-12 px-8 rounded-lg font-semibold text-base transition-colors"
              >
                <Square className="w-5 h-5 mr-2" />
                Dừng Ghi
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
