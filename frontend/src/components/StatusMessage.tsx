"use client";

import { useEffect, useState } from "react";


interface StatusMessageProps {
  type: "success" | "error";
  message: string;
  onClose?: () => void;
}


export default function StatusMessage({ type, message, onClose }: StatusMessageProps) {
  const [visible, setVisible] = useState(Boolean(message));

  useEffect(() => {
    setVisible(Boolean(message));
    if (!message) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      setVisible(false);
      onClose?.();
    }, 4000);

    return () => window.clearTimeout(timeoutId);
  }, [message, onClose]);

  if (!visible || !message) {
    return null;
  }

  const className =
    type === "error"
      ? "bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2 rounded"
      : "bg-green-50 border border-green-200 text-green-700 text-sm px-4 py-2 rounded";

  return <div className={className}>{message}</div>;
}
