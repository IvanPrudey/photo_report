from constants.constants import ROLE_CHOICES, CATEGORY_CHOICES


class TestConstants:

    def test_no_empty_two_roles(self):
        assert len(ROLE_CHOICES) != 0, 'Список ролей пуст, определите роли в константах.'

    def test_admin_exist(self):
        admin_exists = any(code == 'admin' for code, name in ROLE_CHOICES)
        assert admin_exists is True, 'Должна быть роль "admin"'

    def test_user_exist(self):
        user_exists = any(code == 'user' for code, name in ROLE_CHOICES)
        assert user_exists is True, 'Должна быть роль "user"'

    def test_roles_correspond_to_values(self):
        roles_dict = dict(ROLE_CHOICES)
        assert roles_dict['admin'] == 'Администратор', 'Роль admin должна отображаться как "Администратор"'
        assert roles_dict['user'] == 'Сотрудник', 'Роль user должна отображаться как "Сотрудник"'

    def test_no_empty_category(self):
        assert len(CATEGORY_CHOICES) != 0, 'Список категорий пуст,определите роли в константах.'
