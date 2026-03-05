"use client";

import { useCallback, useState } from "react";
import Link from "next/link";
import { Upload, FileText, Loader2, CheckCircle2, ArrowRight } from "lucide-react";
import { uploadDocument } from "@/lib/api";
import { cn } from "@/lib/utils";

const ACCEPT = ".pdf,.docx,.txt";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [documentId, setDocumentId] = useState<string | null>(null);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setStatus("idle");
      setMessage("");
    }
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!file) return;
    setStatus("uploading");
    setMessage("");
    try {
      const res = await uploadDocument(file);
      setDocumentId(res.document_id);
      setMessage(`Uploaded successfully. ${res.pages} pages indexed.`);
      setStatus("success");
      setFile(null);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Upload failed");
      setStatus("error");
    }
  }, [file]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const f = e.dataTransfer.files[0];
      if (f && ACCEPT.split(",").some((ext) => f.name.toLowerCase().endsWith(ext.trim()))) {
        setFile(f);
        setStatus("idle");
        setMessage("");
      }
    },
    []
  );

  const handleDragOver = useCallback((e: React.DragEvent) => e.preventDefault(), []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-lg">
        <h1 className="text-2xl font-semibold text-center mb-2">DocIntelligenceChat</h1>
        <p className="text-center text-zinc-400 mb-8">
          Upload a document to get started. Supported: PDF, DOCX, TXT
        </p>

        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className={cn(
            "border-2 border-dashed rounded-xl p-12 text-center transition-colors",
            file ? "border-blue-500/50 bg-blue-500/5" : "border-zinc-600 hover:border-zinc-500"
          )}
        >
          <input
            type="file"
            accept={ACCEPT}
            onChange={handleFileChange}
            className="hidden"
            id="file-input"
          />
          <label htmlFor="file-input" className="cursor-pointer block">
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <FileText className="w-12 h-12 text-blue-400" />
                <span className="font-medium">{file.name}</span>
                <span className="text-sm text-zinc-500">
                  {(file.size / 1024).toFixed(1)} KB
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <Upload className="w-12 h-12 text-zinc-500" />
                <span className="text-zinc-400">Drop a file here or click to browse</span>
              </div>
            )}
          </label>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!file || status === "uploading"}
          className={cn(
            "mt-6 w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors",
            file && status !== "uploading"
              ? "bg-blue-600 hover:bg-blue-500 text-white"
              : "bg-zinc-700 text-zinc-400 cursor-not-allowed"
          )}
        >
          {status === "uploading" ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Uploading & indexing…
            </>
          ) : (
            "Upload & Index"
          )}
        </button>

        {message && (
          <div
            className={cn(
              "mt-4 p-3 rounded-lg flex items-center gap-2",
              status === "success" && "bg-emerald-500/10 text-emerald-400",
              status === "error" && "bg-red-500/10 text-red-400"
            )}
          >
            {status === "success" && <CheckCircle2 className="w-5 h-5 shrink-0" />}
            {message}
          </div>
        )}

        <Link
          href="/chat"
          className="mt-8 flex items-center justify-center gap-2 text-blue-400 hover:text-blue-300 transition-colors"
        >
          Go to Chat
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
