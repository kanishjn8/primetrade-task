import LoginClient from "./LoginClient";


interface LoginPageProps {
  searchParams?: {
    registered?: string | string[];
  };
}


export default function LoginPage({ searchParams }: LoginPageProps) {
  const registeredValue = searchParams?.registered;
  const isRegistered = Array.isArray(registeredValue)
    ? registeredValue.includes("1")
    : registeredValue === "1";

  return <LoginClient registered={isRegistered} />;
}
