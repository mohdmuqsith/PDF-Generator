import ReportList from "./components/ReportList.jsx";

export default function App() {
  return (
    <main className="app">
      <header className="app-header">
        <h1>PDF Report Generator</h1>
        <p>Generate sales reports and download them as PDF.</p>
      </header>
      <ReportList />
    </main>
  );
}
