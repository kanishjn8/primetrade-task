"use client";

interface NavbarProps {
  username: string;
  onLogout: () => void;
}


export default function Navbar({ username, onLogout }: NavbarProps) {
  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="mx-auto flex max-w-3xl items-center justify-between">
        <p className="font-semibold text-gray-900">TaskManager</p>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">{username}</span>
          <button
            type="button"
            onClick={onLogout}
            className="bg-white text-gray-700 text-sm border border-gray-300 px-3 py-1 rounded hover:bg-gray-50"
          >
            Sign out
          </button>
        </div>
      </div>
    </nav>
  );
}
