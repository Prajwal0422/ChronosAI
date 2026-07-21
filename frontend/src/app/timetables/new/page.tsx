import { PlaceholderPage } from "@/components/ui/placeholder-page";

export default function NewTimetablePage() {
  return (
    <PlaceholderPage
      title="New Timetable"
      description="The AI-powered timetable generator is under active development. You will soon be able to configure constraints, select teachers, subjects, and classrooms, and generate an optimized timetable in seconds."
      breadcrumbs={[
        { label: "Home", href: "/" },
        { label: "Timetables", href: "/timetables" },
        { label: "New Timetable", href: "/timetables/new" },
      ]}
    />
  );
}
