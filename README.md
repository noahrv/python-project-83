# Page Analyzer


[![Python CI](https://github.com/noahrv/python-project-83/actions/workflows/python-ci.yml/badge.svg)](https://github.com/noahrv/python-project-83/actions/workflows/python-ci.yml)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=noahrv_python-project-83&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=noahrv_python-project-83)

### Hexlet tests and linter status:

[![Actions Status](https://github.com/noahrv/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/noahrv/python-project-83/actions)


## Демо: 

https://python-project-83-k2jm.onrender.com

## Описание проекта

Page Analyzer — это веб-приложение для анализа сайтов.  
Оно позволяет добавлять страницы и выполнять их проверку с извлечением SEO-данных.

В результате проверки сохраняются:
- код ответа сервера
- заголовок `h1`
- содержимое `title`
- meta `description`

## Возможности

- добавление сайтов в базу
- проверка доступности сайта
- сбор SEO-данных со страницы
- хранение истории проверок
- обработка ошибок сети и HTTP

## Установка

Склонируйте репозиторий и установите зависимости:

```bash
git clone https://github.com/noahrv/python-project-83.git
cd python-project-83
make install
```

## Запуск

Для запуска приложения в режиме разработки выполните:

```bash
make dev
```