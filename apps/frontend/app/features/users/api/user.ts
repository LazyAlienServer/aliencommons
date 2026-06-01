import { api, apiBare } from "~/composables/api";

function createProfile(
  email: string,
  password: string,
  confirmPassword: string,
) {
  return apiBare.post("/profiles/", {
    email: email,
    password: password,
    confirm_password: confirmPassword,
  });
}

function listProfiles() {
  return api.get("/profiles/");
}

function retrieveProfile(id: string) {
  return api.get(`/profiles/${id}/`);
}

function retrieveMyProfile() {
  return api.get("/profiles/me/", { withCredentials: true });
}

function updateAvatar(file: File) {
  const formData = new FormData();
  formData.append("avatar", file);
  return api.patch(`/profiles/me/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

function updateUsername(name: string) {
  return api.patch("/profiles/me/", {
    username: name,
  });
}

function loginUser(email: string, password: string) {
  return apiBare.post("/auth/login/", {
    email: email,
    password: password,
  });
}

function refreshUserLoginToken(refreshToken: string) {
  return apiBare.post("/auth/refresh_login_token/", { refresh: refreshToken });
}

export {
  createProfile,
  listProfiles,
  retrieveProfile,
  retrieveMyProfile,
  updateAvatar,
  updateUsername,
  loginUser,
  refreshUserLoginToken,
};
