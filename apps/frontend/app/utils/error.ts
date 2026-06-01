function extractErrorMessage(err: unknown): string {
  if (err && typeof err === "object" && "response" in err) {
    const response = (
      err as { response?: { data?: { detail?: string; data?: unknown } } }
    ).response;
    if (response?.data?.detail) {
      return response.data.detail;
    }
    if (response?.data) {
      return JSON.stringify(response.data);
    }
  }
  if (err instanceof Error) {
    return err.message;
  }
  return String(err);
}

export { extractErrorMessage };
