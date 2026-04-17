# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_server.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('ml/weights', 'ml/weights'),
        ('core_api/settings', 'core_api/settings'),
    ],
    hiddenimports=[
        'users',
        'users.models',
        'users.views',
        'users.serializers',
        'users.urls',
        'ml',
        'ml.models',
        'ml.views',
        'ml.serializers',
        'ml.urls',
        'ml.tasks',
        'celery',
        'django_celery_results',
        'rest_framework',
        'rest_framework_simplejwt',
        'rest_framework_simplejwt.token_blacklist',
        'corsheaders',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='run_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run_server',
)
