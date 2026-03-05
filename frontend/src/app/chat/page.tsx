"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Send, FileText, Loader2, ArrowLeft } from "lucide-react";
import { chat, listDocuments, type DocumentItem } from "@/lib/api";
import { cn } from "@/lib/utils";

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: { page: number }[];
};

export default function ChatPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listDocuments()
      .then(setDocuments)
      .catch(() => setDocuments([]))
      .finally(() => setLoadingDocs(false));
  }, []);

  useEffect(() => {
    if (documents.length > 0 && !selectedDoc) {
      setSelectedDoc(documents[0]);
    }
  }, [documents, selectedDoc]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(async () => {
    const q = input.trim();
    if (!q || !selectedDoc || loading) return;

    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }]);
    setLoading(true);

    try {
      const res = await chat(selectedDoc.document_id, q);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: err instanceof Error ? err.message : "Something went wrong.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, selectedDoc, loading]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-zinc-800 px-4 py-3 flex items-center gap-4">
        <Link
          href="/"
          className="text-zinc-400 hover:text-white transition-colors flex items-center gap-1"
        >
          <ArrowLeft className="w-4 h-4" />
          Upload
        </Link>
        <div className="flex-1 flex items-center gap-2">
          <FileText className="w-4 h-4 text-zinc-500" />
          <select
            value={selectedDoc?.document_id ?? ""}
            onChange={(e) => {
              const doc = documents.find((d) => d.document_id === e.target.value);
              setSelectedDoc(doc ?? null);
              setMessages([]);
            }}
            className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {loadingDocs ? (
              <option>Loading documents…</option>
            ) : documents.length === 0 ? (
              <option>No documents — upload one first</option>
            ) : (
              documents.map((d) => (
                <option key={d.document_id} value={d.document_id}>
                  {d.filename} ({d.pages} pages)
                </option>
              ))
            )}
          </select>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 max-w-3xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="text-center text-zinc-500 py-16">
            {!selectedDoc ? (
              <p>Upload a document first, then select it to start chatting.</p>
            ) : (
              <p>Ask a question about {selectedDoc.filename}</p>
            )}
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={cn(
              "mb-4",
              m.role === "user" ? "text-right" : "text-left"
            )}
          >
            <div
              className={cn(
                "inline-block max-w-[85%] rounded-xl px-4 py-3",
                m.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-zinc-800 text-zinc-100"
              )}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.sources && m.sources.length > 0 && (
                <p className="mt-2 text-xs text-zinc-400">
                  Sources: pages {m.sources.map((s) => s.page).join(", ")}
                </p>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-2 items-center text-zinc-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Thinking…</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="border-t border-zinc-800 p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              selectedDoc
                ? `Ask about ${selectedDoc.filename}…`
                : "Select a document first"
            }
            disabled={!selectedDoc || loading}
            className="flex-1 bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={!selectedDoc || !input.trim() || loading}
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl px-4 py-3 flex items-center justify-center transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
