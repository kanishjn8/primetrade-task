"use client";

import type { Task } from "@/lib/types";


interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
}


const statusConfig: Record<Task["status"], { dotClassName: string; label: string }> = {
  pending: { dotClassName: "bg-gray-400", label: "Pending" },
  in_progress: { dotClassName: "bg-blue-500", label: "In Progress" },
  completed: { dotClassName: "bg-green-500", label: "Completed" },
};


export default function TaskCard({ task, onEdit, onDelete }: TaskCardProps) {
  const status = statusConfig[task.status];

  return (
    <div className="bg-white border border-gray-200 rounded p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h3 className="font-medium text-gray-900">{task.title}</h3>
          <p
            className="mt-2 overflow-hidden text-sm text-gray-500"
            style={{
              display: "-webkit-box",
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 2,
            }}
          >
            {task.description || "No description provided."}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={() => onEdit(task)}
            className="bg-white text-gray-700 text-sm border border-gray-300 px-3 py-1 rounded hover:bg-gray-50"
          >
            Edit
          </button>
          <button
            type="button"
            onClick={() => onDelete(task.id)}
            className="bg-white text-red-600 text-sm border border-red-300 px-3 py-1 rounded hover:bg-red-50"
          >
            Delete
          </button>
        </div>
      </div>
      <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
        <span className="inline-flex items-center gap-2">
          <span className={`inline-block h-2 w-2 rounded-full ${status.dotClassName}`} />
          {status.label}
        </span>
        <span className="text-xs uppercase text-gray-500">{task.priority}</span>
      </div>
    </div>
  );
}
