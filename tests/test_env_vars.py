import os


class TestRequiredEnvVars():

    def test_required_env_vars_exist(self):
        '''Проверка наличия обязательных переменных и их значений.'''
        required_vars = ['SECRET_KEY', 'BOT_TOKEN']
        for var_name in required_vars:
            assert os.getenv(var_name) is not None, f'Переменная {var_name} не установлена'
            assert os.getenv(var_name) != '', f'Переменная {var_name} пустая'
