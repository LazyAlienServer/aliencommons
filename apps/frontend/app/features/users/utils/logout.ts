function handleLogout() {
  const userStore = useUserStore();
  userStore.logout();
}

export { handleLogout };
