"use client";

import { useEffect, useState, type FormEvent } from "react";

import type { Task, TaskFormValues, TaskPriority, TaskStatus } from "@/lib/types";


interface TaskFormProps {
  initial?: Task;
  errors?: Partial<Record<keyof TaskFormValues, string>>;
  loading: boolean;
  onCancel: () => void;
  onSubmit: (data: TaskFormValues) => void | Promise<void>;
}


const inputClassName =
  "w-full border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500";
const labelClassName = "text-sm font-medium text-gray-700";
const errorClassName = "mt-1 text-sm text-red-600";

const statusOptions: Array<{ value: TaskStatus; label: string }> = [
  { value: "pending", label: "Pending" },
  { value: "in_progress", label: "In Progress" },
  { value: "completed", label: "Completed" },
];

const priorityOptions: Array<{ value: TaskPriority; label: string }> = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];


function getInitialValues(task?: Task): TaskFormValues {
  return {
    title: task?.title ?? "",
    description: task?.description ?? "",
    status: task?.status ?? "pending",
    priority: task?.priority ?? "medium",
  };
}


export default function TaskForm({ initial, errors, loading, onCancel, onSubmit }: TaskFormProps) {
  const [values, setValues] = useState<TaskFormValues>(getInitialValues(initial));

  useEffect(() => {
    setValues(getInitialValues(initial));
  }, [initial]);

  const handleChange = <Field extends keyof TaskFormValues>(field: Field, value: TaskFormValues[Field]) => {
    setValues((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit(values);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded p-4">
      <div className="space-y-4">
        <div>
          <label htmlFor="title" className={labelClassName}>
            Title
          </label>
          <input
            id="title"
            type="text"
            value={values.title}
            onChange={(event) => handleChange("title", event.target.value)}
            className={`${inputClassName} mt-1`}
            placeholder="Enter a task title"
            required
          />
          {errors?.title ? <p className={errorClassName}>{errors.title}</p> : null}
        </div>

        <div>
          <label htmlFor="description" className={labelClassName}>
            Description
          </label>
          <textarea
            id="description"
            rows={3}
            value={values.description}
            onChange={(event) => handleChange("description", event.target.value)}
            className={`${inputClassName} mt-1`}
            placeholder="Add more detail"
          />
          {errors?.description ? <p className={errorClassName}>{errors.description}</p> : null}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="status" className={labelClassName}>
              Status
            </label>
            <select
              id="status"
              value={values.status}
              onChange={(event) => handleChange("status", event.target.value as TaskStatus)}
              className={`${inputClassName} mt-1`}
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors?.status ? <p className={errorClassName}>{errors.status}</p> : null}
          </div>

          <div>
            <label htmlFor="priority" className={labelClassName}>
              Priority
            </label>
            <select
              id="priority"
              value={values.priority}
              onChange={(event) => handleChange("priority", event.target.value as TaskPriority)}
              className={`${inputClassName} mt-1`}
            >
              {priorityOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors?.priority ? <p className={errorClassName}>{errors.priority}</p> : null}
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {loading ? "Saving..." : "Save"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="bg-white text-gray-700 text-sm border border-gray-300 px-3 py-1 rounded hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
