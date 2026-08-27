const API_BASE_URL = "http://localhost:8000";

export { API_BASE_URL };

async function request(path, options) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body && body.detail) detail = body.detail;
    } catch {
      // response had no JSON body; keep the default message
    }
    throw new Error(detail);
  }

  return response.json();
}

export async function getReports() {
  const data = await request("/reports");
  return data.reports ?? [];
}

export async function createReport({ force = false } = {}) {
  return request("/reports", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ force }),
  });
}

export async function checkHealth() {
  return request("/health");
}

export function fileUrl(report) {
  return `${API_BASE_URL}${report.file}`;
}
