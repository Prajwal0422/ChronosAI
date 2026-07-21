import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { LandingPage } from "./landing/landing-page";

export default function Home() {
  const cookieStore = cookies();
  const token = cookieStore.get("access_token");

  if (token?.value) {
    redirect("/dashboard");
  }

  return <LandingPage />;
}
