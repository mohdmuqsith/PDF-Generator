const API_BASE_URL = "http://localhost:8000";

export async function getReports() {
  const response = await fetch(`${API_BASE_URL}/reports`);
  return response.json();
}
