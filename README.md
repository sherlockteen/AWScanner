# AWS IP Range Scanner

Это вторая обновлённая версия скрипта, теперь можно сканировать все json файлы (регионы).
Скрипт позволяет сканировать диапазоны IP-адресов AWS с использованием **Masscan** и выполнять анализ открытых TLS-соединений. Он загружает актуальные диапазоны IP для выбранного региона AWS, сканирует их на порту 443, а затем анализирует сертификаты с помощью **tls-scan**.

## Особенности:
- Автоматическая загрузка актуальных диапазонов IP-адресов для заданного региона AWS.
- Сканирование портов с помощью **Masscan**.
- Извлечение открытых IP-адресов с порта 443.
- Анализ TLS-сертификатов и вывод информации в CSV-формате.

## Использование:

**Запустить скрипт**:
```bash
sudo python3 AWScanner.py
```
![изображение](https://github.com/user-attachments/assets/42707a96-46fc-47fe-96e8-c069a5295916)


Вывод результатов:

    Результаты сканирования будут сохранены в файлы.
    Такие как <region>-range.txt, <region>-range.masscan, <region>-range.tlsopen, и <region>-range-tlsinfo.csv.

Файлы выходных данных:

    *.txt: Содержит уникальные диапазоны IP для указанного региона.
    *.masscan: Результаты сканирования, полученные с помощью Masscan.
