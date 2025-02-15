import os
import json
import requests
import subprocess
import zipfile
from tqdm import tqdm
import urllib3

urllib3.disable_warnings()

# Функция для получения манифеста версий
def get_version_manifest():
    url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    response = requests.get(url, verify=True)  # Отключаем проверку SSL
    return response.json()

# Функция для получения данных о конкретной версии
def get_version_data(version_url):
    response = requests.get(version_url, verify=True)  # Отключаем проверку SSL
    return response.json()

# Функция для скачивания файла
def download_file(url, path):
    # Преобразуем путь в абсолютный
    abs_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)  # Создаём папки, если их нет
    response = requests.get(url, verify=False)
    with open(abs_path, "wb") as f:
        f.write(response.content)

# Функция для извлечения файлов из .jar
def extract_natives(jar_path, output_dir):
    with zipfile.ZipFile(jar_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"Извлечено: {jar_path} -> {output_dir}")

def assets_exist(version_data, version_id):
    assets_dir = f"versions/{version_id}/assets"
    if not os.path.exists(assets_dir):
        return False

    # Проверяем индекс ассетов
    asset_index_path = f"{assets_dir}/indexes/{version_data['assetIndex']['id']}.json"
    if not os.path.exists(asset_index_path):
        return False

    # Проверяем объекты ассетов
    with open(asset_index_path, "r", encoding="utf-8") as f:
        asset_index = json.load(f)

    for asset_name, asset_info in asset_index["objects"].items():
        asset_hash = asset_info["hash"]
        asset_path = f"{assets_dir}/objects/{asset_hash[:2]}/{asset_hash}"
        if not os.path.exists(asset_path):
            return False

    return True

def libraries_exist(version_data, version_id):
    libraries_dir = f"versions/{version_id}/libraries"
    if not os.path.exists(libraries_dir):
        return False

    for library in version_data["libraries"]:
        if "rules" in library and not check_library_rules(library["rules"]):
            continue
        if "downloads" in library and "artifact" in library["downloads"]:
            lib_path = os.path.join(libraries_dir, library["downloads"]["artifact"]["path"])
            if not os.path.exists(lib_path):
                return False

    return True

def natives_exist(version_data, version_id):
    natives_dir = f"versions/{version_id}/natives"
    if not os.path.exists(natives_dir):
        return False

    for library in version_data["libraries"]:
        if "natives" in library:
            classifier = library["natives"].get("windows", "") if os.name == "nt" else ""
            if classifier and "classifiers" in library["downloads"]:
                native_path = os.path.join(natives_dir, os.path.basename(library["downloads"]["classifiers"][classifier]["path"]))
                if not os.path.exists(native_path):
                    return False

    return True

# Функция для скачивания версии Minecraft
def download_version(version_id):
    manifest = get_version_manifest()

    # Находим URL для нужной версии
    version_url = None
    for version in manifest["versions"]:
        if version["id"] == version_id:
            version_url = version["url"]
            break

    if not version_url:
        print(f"Версия {version_id} не найдена.")
        return

    # Получаем данные о версии
    version_data = get_version_data(version_url)

    # Скачиваем клиент
    client_url = version_data["downloads"]["client"]["url"]
    os.makedirs(f"versions/{version_id}", exist_ok=True)
    if not os.path.exists(f"versions/{version_id}/client.jar"):
        download_file(client_url, f"versions/{version_id}/client.jar")

    # Скачиваем библиотеки (если их нет)
    if not libraries_exist(version_data, version_id):
        download_libraries(version_data, version_id)

    # Скачиваем нативные библиотеки (если их нет)
    if not natives_exist(version_data, version_id):
        download_and_extract_natives(version_data, version_id)
    download_authlibfake(version_id)
    # Скачиваем ассеты (если их нет)
    if not assets_exist(version_data, version_id):
        download_assets(version_data, version_id)

    print(f"Версия {version_id} успешно скачана.")

# Функция для скачивания библиотек
def download_libraries(version_data, version_id):
    libraries_dir = f"versions/{version_id}/libraries"
    os.makedirs(libraries_dir, exist_ok=True)

    for library in version_data["libraries"]:
        # Проверяем правила для библиотек (например, ОС)
        if "rules" in library:
            if not check_library_rules(library["rules"]):
                continue

        # Проверяем наличие ключа "artifact"
        if "downloads" in library and "artifact" in library["downloads"]:
            library_path = library["downloads"]["artifact"]["path"]
            library_url = library["downloads"]["artifact"]["url"]
            library_file = os.path.join(libraries_dir, library_path)
            os.makedirs(os.path.dirname(library_file), exist_ok=True)
            download_file(library_url, library_file)
        else:
            print(f"Библиотека {library.get('name', 'unknown')} не содержит артефакта для скачивания.")

def download_assets(version_data, version_id):
    assets_dir = f"versions/{version_id}/assets"
    os.makedirs(assets_dir, exist_ok=True)

    # Скачиваем индекс ассетов
    asset_index_url = version_data["assetIndex"]["url"]
    asset_index_path = f"{assets_dir}/indexes/{version_data['assetIndex']['id']}.json"
    download_file(asset_index_url, asset_index_path)

    # Парсим индекс ассетов
    with open(asset_index_path, "r", encoding="utf-8") as f:
        asset_index = json.load(f)

    # Скачиваем все объекты ассетов
    objects_dir = f"{assets_dir}/objects"
    os.makedirs(objects_dir, exist_ok=True)

    for asset_name, asset_info in tqdm(asset_index["objects"].items(), desc="Скачивание ассетов"):
        asset_hash = asset_info["hash"]
        asset_url = f"https://resources.download.minecraft.net/{asset_hash[:2]}/{asset_hash}"
        asset_path = f"{objects_dir}/{asset_hash[:2]}/{asset_hash}"

        # Скачиваем, если файла нет
        if not os.path.exists(asset_path):
            download_file(asset_url, asset_path)

def download_authlibfake(version_id):
    authlibfakepath = f"versions/{version_id}/fakeauthlib"
    os.makedirs(authlibfakepath, exist_ok=True)
    authlibfakeurl = "https://github.com/yushijinhun/authlib-injector/releases/download/v1.2.5/authlib-injector-1.2.5.jar"
    path = os.path.join(authlibfakepath, "authlib-injector-1.2.5.jar")  # Используем os.path.join для корректного формирования пути
    if not os.path.exists(path):
        download_file(authlibfakeurl, path)  # Передаем полный путь к файлу
        print('Fake authlib downloaded successfuly')
    else:
        print('Fake authlib is allredy downloaded')

# Функция для скачивания и извлечения нативных библиотек
def download_and_extract_natives(version_data, version_id):
    natives_dir = f"versions/{version_id}/natives"
    os.makedirs(natives_dir, exist_ok=True)

    for library in version_data["libraries"]:
        if "natives" in library:
            # Проверяем правила для библиотек (например, ОС)
            if "rules" in library and not check_library_rules(library["rules"]):
                continue

            # Определяем классификатор для текущей ОС
            classifier = library["natives"]["windows"]  # Для Windows
            if os.name == "posix":
                classifier = library["natives"]["linux"]  # Для Linux
            elif os.name == "mac":
                classifier = library["natives"]["osx"]  # Для macOS

            # Получаем URL и путь для нативных библиотек
            if "classifiers" in library["downloads"] and classifier in library["downloads"]["classifiers"]:
                native_url = library["downloads"]["classifiers"][classifier]["url"]
                native_path = library["downloads"]["classifiers"][classifier]["path"]
                native_file = os.path.join(natives_dir, os.path.basename(native_path))

                # Скачиваем .jar-файл
                download_file(native_url, native_file)

                # Извлекаем файлы из .jar
                extract_natives(native_file, natives_dir)
            else:
                print(f"Нативные библиотеки для {classifier} не найдены.")

# Функция для проверки правил библиотек
def check_library_rules(rules):
    for rule in rules:
        if rule["action"] == "allow":
            if "os" in rule and rule["os"]["name"] != os.name:
                return False
        elif rule["action"] == "disallow":
            if "os" in rule and rule["os"]["name"] == os.name:
                return False
    return True

# Функция для формирования classpath
def get_classpath(version_id):
    libraries_dir = f"versions/{version_id}/libraries"
    classpath = []

    # Добавляем client.jar
    classpath.append(f"versions/{version_id}/client.jar")

    # Добавляем все библиотеки
    for root, _, files in os.walk(libraries_dir):
        for file in files:
            if file.endswith(".jar"):
                classpath.append(os.path.join(root, file))

    return ";".join(classpath)  # Для Windows
    # return ":".join(classpath)  # Для Linux/macOS