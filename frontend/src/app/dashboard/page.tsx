"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Navbar from "@/components/Navbar";
import StatusMessage from "@/components/StatusMessage";
import TaskCard from "@/components/TaskCard";
import TaskForm from "@/components/TaskForm";
import { useAuth } from "@/context/AuthContext";
import api, { getApiErrorMessage, getApiFieldErrors } from "@/lib/api";
import type { Task, TaskFormValues } from "@/lib/types";


type TaskFormErrors = Partial<Record<keyof TaskFormValues, string>>;


export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, isReady, logout, user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | undefined>(undefined);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [formErrors, setFormErrors] = useState<TaskFormErrors>({});

  useEffect(() => {
    if (isReady && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isReady, router]);

  useEffect(() => {
    if (!isReady || !isAuthenticated) {
      return;
    }

    const loadTasks = async () => {
      setLoading(true);

      try {
        const response = await api.get<Task[]>("/api/v1/tasks");
        setTasks(response.data);
      } catch (error) {
        setMessage({ type: "error", text: getApiErrorMessage(error, "Failed to load tasks.") });
      } finally {
        setLoading(false);
      }
    };

    void loadTasks();
  }, [isAuthenticated, isReady]);

  const resetFormState = () => {
    setEditingTask(undefined);
    setShowForm(false);
    setFormErrors({});
  };

  const handleCreateClick = () => {
    setEditingTask(undefined);
    setFormErrors({});
    setShowForm(true);
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setFormErrors({});
    setShowForm(true);
  };

  const handleDelete = async (taskId: string) => {
    const shouldDelete = window.confirm("Delete this task?");
    if (!shouldDelete) {
      return;
    }

    try {
      await api.delete(`/api/v1/tasks/${taskId}`);
      setTasks((current) => current.filter((task) => task.id !== taskId));
      setMessage({ type: "success", text: "Task deleted." });
    } catch (error) {
      setMessage({ type: "error", text: getApiErrorMessage(error, "Failed to delete task.") });
    }
  };

  const handleSubmit = async (values: TaskFormValues) => {
    setSubmitting(true);
    setFormErrors({});

    try {
      if (editingTask) {
        const response = await api.patch<Task>(`/api/v1/tasks/${editingTask.id}`, values);
        setTasks((current) =>
          current.map((task) => (task.id === editingTask.id ? response.data : task)),
        );
        setMessage({ type: "success", text: "Task updated." });
      } else {
        const response = await api.post<Task>("/api/v1/tasks", values);
        setTasks((current) => [response.data, ...current]);
        setMessage({ type: "success", text: "Task created." });
      }

      resetFormState();
    } catch (error) {
      const errors = getApiFieldErrors(error);
      setFormErrors(errors as TaskFormErrors);
      setMessage({ type: "error", text: getApiErrorMessage(error, "Failed to save task.") });
    } finally {
      setSubmitting(false);
    }
  };

  if (!isReady || (isAuthenticated && loading)) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-3xl px-4 py-8 text-sm text-gray-400">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar username={user?.email ?? "Signed in"} onLogout={logout} />
      <main className="max-w-3xl mx-auto px-4 py-8">
        {user?.role === "admin" ? (
          <div className="mb-4 rounded border border-yellow-200 bg-yellow-50 px-3 py-1 text-xs text-yellow-800">
            Admin view - showing all users&apos; tasks
          </div>
        ) : null}

        {message ? (
          <div className="mb-4">
            <StatusMessage
              type={message.type}
              message={message.text}
              onClose={() => setMessage(null)}
            />
          </div>
        ) : null}

        <div className="flex items-center justify-between gap-4">
          <h1 className="text-xl font-semibold text-gray-900">Your Tasks</h1>
          <button
            type="button"
            onClick={handleCreateClick}
            className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            New Task
          </button>
        </div>

        {showForm ? (
          <div className="mt-6">
            <TaskForm
              initial={editingTask}
              errors={formErrors}
              loading={submitting}
              onCancel={resetFormState}
              onSubmit={handleSubmit}
            />
          </div>
        ) : null}

        <div className="mt-6 space-y-4">
          {tasks.length === 0 ? (
            <div className="py-12 text-center text-sm text-gray-400">
              No tasks yet. Create one to get started.
            </div>
          ) : (
            tasks.map((task) => (
              <TaskCard key={task.id} task={task} onEdit={handleEdit} onDelete={handleDelete} />
            ))
          )}
        </div>
      </main>
    </div>
  );
}
