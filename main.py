from math import sqrt, ceil
from urllib.parse import urlencode
from zipfile import ZipFile

import io
import os
import sys
import shutil
import requests
from PIL import Image


base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
public_key = 'https://disk.yandex.ru/d/V47MEP5hZ3U1kg'


print('Введите имя папки, изображения из которой необходимо загрузить. Нажмите клавишу "Enter". Для завершения ввода '
      'просто нажмите клавишу "Enter"')
a = input('--->>> ')
input_list = []
while True:
    if a != '':
        input_list.append(a)
        a = input('--->>> ')
    else:
        break


# Получение ссылки на скачивание всей папки одним архивом
final_url = base_url + urlencode(dict(public_key=public_key))
response = requests.get(final_url)
download_url = response.json()['href']


# Извлечение из архива по полученной ссылке файлов из введенных пользователем папок
directory_list = []
with ZipFile(io.BytesIO(requests.get(download_url).content)) as archive:
    for i in archive.namelist():
        for field in input_list:
            if field in i:
                archive.extract(member=i)
                if i.endswith('/'):
                    directory_list.append(i[:-1])


if len(directory_list) == 0:
    sys.exit("Запрошенные папки не найдены!")


# Открытие всех изображений из пользовательских папок
pic = []
for directory in directory_list:
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for file in files:
        im = Image.open(os.path.join(directory, file))
        pic.append(im)


# В целях исключения проблем при совместном расположении изображений с разным разрешением, за разрешение суммируемого
# элемента принимается разрешение минимального изображения
min_res_side = min(pic[0].size)
for im in pic[1:]:
    if min(im.size) > min_res_side:
        min_res_side = min(im.size)

# Перемасштабирование списка полученных изображений
pic_resize = []
for im in pic:
    new_im = im.resize((min_res_side, min_res_side))
    pic_resize.append(new_im)

# Определение оптимального разрешения результирующего файла
x = ceil(sqrt(len(pic_resize)))
y = ceil((len(pic_resize)) / x)
new_im = Image.new('RGB', ((x * (100 + min_res_side)) + 100, (y * (100 + min_res_side)) + 100))

# Заполнение суммируемыми изображениями результирующего файла
j = -1
for num, pic in enumerate(pic_resize):
    i = num % x
    if i == 0:
        j += 1
    new_im.paste(pic, ((i * (min_res_side + 100)) + 100, (j * (min_res_side + 100)) + 100))

new_im.save('Result.tif')  # Сохранение результирующего файла

# Удаление загруженных суммируемых изображений
shutil.rmtree(os.path.join(os.path.abspath(os.path.dirname(__file__)), directory_list[0].split("/")[0]))


if __name__ == "__main__":
    print("Файл Result.tif успешно создан!")
