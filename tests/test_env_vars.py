import os
import pytest
from django.conf import settings


class TestRequiredEnvVars():

    def test_required_env_vars_exist(self):
        required_vars = ['SECRET_KEY', 'BOT_TOKEN', 'DEBUG']
        for var_name in required_vars:
            assert os.getenv(var_name) is not None, f'Переменная {var_name} не установлена'
            assert os.getenv(var_name) != '', f'Переменная {var_name} пустая'
