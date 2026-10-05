"""菜单路径白名单（见施工规范 §4.7）。"""
ALLOWED_MENU_PATHS = frozenset({
    "/admin/dashboard", "/admin/travelers", "/admin/trips", "/admin/templates",
    "/admin/bookings", "/admin/groups", "/admin/alerts", "/admin/guides",
    "/admin/records", "/admin/agent-tools", "/admin/agent-logs",
    "/admin/users", "/admin/logs", "/admin/menus",
})


def is_allowed_menu_path(path: str) -> bool:
    """建菜单时校验路径是否合法。"""
    return path in ALLOWED_MENU_PATHS
