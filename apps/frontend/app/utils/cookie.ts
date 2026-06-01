import Cookies from "js-cookie";

function isHttps() {
  return import.meta.client && window.location.protocol === "https:";
}

function setRefreshToken(token: string, expiresDays = 30) {
  Cookies.set(`${import.meta.env.MODE}_refreshToken`, token, {
    expires: expiresDays,
    secure: isHttps(),
    sameSite: "strict",
  });
}

function getRefreshToken() {
  return Cookies.get(`${import.meta.env.MODE}_refreshToken`);
}

function removeRefreshToken() {
  Cookies.remove(`${import.meta.env.MODE}_refreshToken`);
}

export { setRefreshToken, getRefreshToken, removeRefreshToken };
