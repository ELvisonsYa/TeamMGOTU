# Отчёт о выполнении задачи "Создание программы для обнаружения повышенного радиационного фона в трубах с паром на атомной электростанции"

- [Отчёт о выполнении задачи "Создание программы для обнаружения повышенного радиационного фона в трубах с паром на атомной электростанции"](#отчёт-о-выполнении-задачи-Создание программы для обнаружения повышенного радиационного фона в трубах с паром на атомной электростанции)
  - [Постановка задачи](#постановка-задачи)
  - [Известные ограничения и вводные условия](#известные-ограничения-и-вводные-условия)
    - [Цели и Предположения Безопасности (ЦПБ)](#цели-и-предположения-безопасности-цпб)
  - [Архитектура системы](#архитектура-системы)
    - [Компоненты](#компоненты)
    - [Алгоритм работы решения](#алгоритм-работы-решения)
    - [Описание Сценариев (последовательности выполнения операций), при которых ЦБ нарушаются](#описание-сценариев-последовательности-выполнения-операций-при-которых-цб-нарушаются)
    - [Указание "доверенных компонент" на архитектурной диаграмме.](#указание-доверенных-компонент-на-архитектурной-диаграмме)
    - [Политики безопасности](#политики-безопасности)
  - [Запуск приложения и тестов](#запуск-приложения-и-тестов)
    - [Запуск приложения](#запуск-приложения)
    - [Запуск тестов](#запуск-тестов)

## Постановка задачи

Рассматриваемое устройство детектирования (УД) обрабатывает входящие
сигналы от датчиков, в случае превышения порога срабатывания
принимает решение о выдаче команды в систему управления защиты
(СУЗ) реактора (автоматическое срабатывание).

УД передаёт обработанные данные в автоматизированную систему
управления технологическим процессом (АСУ ТП) АЭС для дальнейшей
обработки, на основе этих данных оператор АСУ ТП может принять
решение о выдаче команды в СУЗ (административное срабатывание)
Вторичные функции
- УД сохраняет во встроенном журнале события

![Устройство детектирования и его окружение](devise.png)

## Известные ограничения и вводные условия

1. Данные от внешнего окружения передаются по HTTP
2. Данные на внешние устройства передаются по HTTP по REST API.
3. Монитор безопасности и брокер сообщения явялются защищенными

## События безопасности

1. превышение входным сигналом порога предупреждения
2. превышение входным сигналом порога аварии
3. активация режима обновления системы
4. активация режима изменения настроек
5. изменение порога предупреждения
6. изменение порога аварии


### Цели и Предположения Безопасности (ЦПБ)
Цели безопасности:

1. Только авторизованный оператор-технолог в присутствии
оператора-безопасника может инициировать изменение настроек УД
2. Только авторизованный оператор-безопасник в присутствии
оператора-технолога может обновлять ПО УД
3. УД выдаёт целостные и достоверные данные во внешние системы с
задержкой не более 1 секунды в предположении, что операционная
система удовлетворяет требованиям обработки данных в реальном
времени
4. Только авторизованный оператор-безопасник удаляет и читает содержимое журнала
5. Устанавлиется только верифицированная прошивка

Предположения безопасности:

- не рассматриваются атаки, связанные с физическим доступом к
оборудованию (например, подмена входных данных; подключение
имитатора УД и т.п.)
- не рассматриваются риски, связанные с физическим отказом внешнего
оборудования, включая обесточивание УД
- не рассматриваются риски, связанные с физическим отказом
аппаратного обеспечения устройства

## Архитектура системы

### Компоненты

| Название | Назначение | Комментарий |
|----|----|----|
|*hendler* | Обработчик входящего потока данных с *sensor*.  Принимает POST-запросы с показателями и передает их внутрь системы УД | - |
|*analyser* | Анализатор полученных показателей. Входящие данные сравниваются с уровнем предупреждения и уровнем тревоги. В случае превышения порога уровня тревоги, отправляет событие в генератор команд (*commander*). Все события анализа перенатпрявляются в генератор событий (*gen_event*)  | - |
|*commander* | На основе входящих событий безопасности оптравляет бинарную команду на *protection_system* | - |
|*gen_event* | Создает и отправляет события безопасности в журнал УД и АСУ ТП (*scada*) | - |
|*journal* | Принимает входящие события от генератора событий и авторизаторов. Хранит в себе события безопасности | - |
|*Авторизатор для работы с журналом* | Авторизует оператора-безопасника по входящему ключу | - |
|*Авторизатор* | Принимает на вход два ключа операторов, авторизует их. Отправляет событие в журнал  | - |
|*manager* | После авторизации операторов отпраляет команду в *downloader* для скачивания обновления с *file_server* | - |
|*Архиватор* | Шифрует файл обновления при скачивании с *file_server*. Для шифрования использует внутренний ключ, устройства | - |
|*verifier* | Принимает зашифрованный файл обновления, расшифровывает его и применяет алгоритмы статического анализа кода для проверки на угрозы  | - |
|*updater* | Устанавливает файл обновления на устройство. Документирует событие в журнале  | - |
|*file_server* | Поскольку в реализации подразумевалось, что инженеры загружают обновление напрямую в устройство, то для эмуляции этого процесса был использован данный компонент. Его стоит рассматривать как подключенное к device устройство, с которого при успешной аутентификации ключей скачивается на device обновление. Поэтому в т.ч. обладает своей памятью в ./data, где и лежит "обновление". | - |
|*protection_system* | Эмулятор системы защиты станции. При выявлении превышающего порог значения в УД, сюда отправляется сообщение, чтобы "сработала" защита. | - |
|*scada*  | Эмулятор пульта управления станцией. Получает все данные (значения, сообщения об ошибках и т.д.) от УД.  | - |
|*sensor* | Эмулятор аналогового датчика, который раз в заданное время подает сгенерированный в заданном диапазоне сигнал через HTTP в УД.  | - |
|*storage* | Фактически это лишь папка с данными, которая является эмулятором некоторой физической памяти устройства УД. | - |

### Алгоритм работы решения
1. Срабатывание системы защиты
![Отправка команд в СУЗ](http://www.plantuml.com/plantuml/png/ZP9FIiD05CRtSuf7zbwW2-aTFC7K3bAeQSca2rsr4Vn35Wekt0dY1QQrmI6syGhVkv6F6KBIh5nr-lBxVNppah7DTPQlhkTggdCzqTPGSc5IkyWIqfPiEAgbCBFBsLAdEILunvRNSDYYuO8Vu547U379z6J0lk0ev8ymtt1SYB4Eh4xr_COEu5TKWbUyRb52ZGO7E1dlWtTbKfFft0pC3tpYBJPUtIeLQzFPUUmq8aWicdxla7da4XLXt_rHGUYP0wk6wv1u2M7-bHpf4yzrs-azRkyueWI_abjXnoK_XkLuIUKx6JROIUupSH496Np19wgL9OXa5wEJ5SAH76hfwCLmV2-_ddW3pniPLZXmIU5DFS5BSgd69ftAr_47)

2. Сценарий генерации событий
![Сценарий генерации событий](http://www.plantuml.com/plantuml/png/nPFDJlf05CNtynIJhlc_08j_I7m4jsm6QGm61zAFXQvAIVn85nXDTATHNg1WgxL2VOKpR-Jj30qKJIHkN34p_Cxbt7ClBTSJZkSVzrbNUA8ZN9jR-xPq1ux5XSjTVMH3Ode7lQ6G7hTmZvaA46E6GeNg71bo3GywZkXiiLTO4lbEp2jY5P8YqAoGed_YRi4tI0bFLL2X73aAB13JSw9rXxQq7U7PFohL20NvZEYQuQtIrcLxcEBEzEcVRbMyLMCL6FEQEF8T-QMtHqmvdl1WMd9znanW_Dz_aqQJbxPGR2Qckrcg22b7ihumBTXKrbKvuZLYuYDcfyg6hkdYzLmslgxIRL9t7rGtnPmIlD3XPbHLPr9WJdKdN8M6e8TdP1Qhn5IepBDP6nvYJeTSJsEEM9tHPrOEALCZUaonK17NEtA9Z2f7TLU_CTJWRRc3QaKaQhmwlI0nf9fOZRRyxfT9fjSjr5sJHxqUVsMoya0BM5gufbJJslwN36CjMtRfZ_u9)

3. Установка обновления

![Обнровление](http://www.plantuml.com/plantuml/png/ZLN1RjD04BtlLwno3Z-G0-g1Fq3Sk6mI0w6f4pbEaJWb3McAWbhe0QGAAX0SE9gqBcdJEBymyqUydNXLh-MYHh8IUzzxysRckTqPn2QAXtjTPLfnBz8rEgSDfJoYX0yeuv76LyfJMbD6ArmNDMq6EWvQh-vbq1bz4jHkK_MXtcbr-YQCWVn8Yos6blJNuGLgXj3gl2tXlr9AQroNT4LfZjmpeNaPH3xoIUzDsEsPTX09fftVghQ9JTCC0cYTMYK-4hrKyzGQniqINItvFQL2VD7f1cNFFE8fO0lVRuG1-C1JQn5Qxm2-yS3xPRlF-Z2MUntss_xXKqm27ShXG7wNBNtc2IgjuNybgDV3A5JAxaG_Ukn6sT1miU9ZdgdTflySewSD538UQokZiTS_ik45ff7ALDBw7Jzd-YABKhk7-7rIW8ghXgx1wvWssz43Tg8fAQL0c3NzF4Hhtt0_0m9Hqxd7Gt37qAYo2LwXfCi6t7rvI8iQgaje8-5qotELqwsIIn2apa2wbQnSGWUK6_4eYTXwq1X2GjSGhlQed1gK9MAL1ZSWhJ2jcRDt9mirPNdWI_B0_xKzudbrHOi2sWK81EGVuWSe2OmKk2vi6F22-6-xLslEzLWs8tX_J6Y8ZtmUAivHnJ6zCUpRDRcJUaKcAmDshC3p-l86wVgXHEK0Lmfhp5iL0VVmEtJ7dcrKyblry3-GbGJNqcv9eY1ZHA-IMUJP8z-pcswiUK8NjY88U9ewOC8Zd5m9D5CQdxmy_afKlBYGiV6L-cAU9tKO-6yqH1Lo_XJFoy3InXshy6BJpyABdRaUIY8r5NG70Ow0nAZjiNNC7ng-JtVCysBNKgdQdCm10ScJbgaWR2jyTl2DVsV_0000)

### Описание Сценариев (последовательности выполнения операций), при которых ЦБ нарушаются



**Отдельная диаграмма для первого негативного сценария - Verifier не проверил файл обновления:**
![](http://www.plantuml.com/plantuml/png/ZLN1RjD04BtlLwp2DVn03wW7_W1n0WwRs41ewaIEKoHEIKEQeaWjz01I1HK83XnDMfUqQP9VcFaZtawySjToKIDPYRtllNapyznkzn8J9_tTjZBDf1Fh6ftHcZ8UKChxjEA1nbV6OrhIYXQupclQz7GIDb_VoQ1J-YIedORgGhtLR7LDb03vaMOR3CtfhyCBrFIXrNfNmd-bZ9QuBkYIiXovQoBpAenzvEFEswZTCK4O2oR8RrLW4jCmlH1Q9rQ93qKlqposXd4pHrTp_a2P45-ssc7PCmzu3DZCznjZ03xmn5g4rdk0hptmNjdkqowCvLxxtS0_V899e4CvxCdligNFF4Ab9Vml1FMc7qTAsPteXu_SABSqN2puY2Tgf-4_n-XfpGFu6sehex7NFxBX6QQHoLIoUi7FcRx8hDJk0NuVtuAAgorTWzSXhJUZ1-nOKrfAWJ1h-dc4rhxXVW84egPpZmVW3dbOQHEyMoLTDk3kotrQr52TGni9fnkUgfnkbLo287KAqeravG8we5oBHqd4neF645AwWd2rH-NKe2mHgpIu1cc1QKqAUquMQihom9VaWVzhSyJJweeM1RGB40Z8FyJtKH8OAN1LR5ZWXVXlkrThJdgiC2DuVqneY0zBl2LFKSKnlJ7isJMvatf59Yi3TgJ0A_eg3zBrGwdA0QuKrfYtYhlYuNVe3ZtRgEItAlXd3-8mUE5OFv2O5DVSxae28SD4nv9SfDgJk6D3xKJpYCvjNH3mD7F0b0SukHJeIcbyF1FuYr7n4aFCHbbSI2CygiF6VsCYsf0hj8kvdXNmwa2MkUw5fv_52mzWLldgrLGO1GgVRNpZtyy_)

Нарушение ЦБ №5 - установлена неверифицированная прошивка

**Отдельная диаграмма для второго негативного сценария - Авторизатор не проверил ключи операторов:**
![](http://www.plantuml.com/plantuml/png/ZLN1RX9H5Ds_htZ1BVq15aqN_e5nfIu6PbGi7SWmQE8AYaWDJQjTQD9eez65ov7sjHHQ-8Nx_iXpBsyAZqoD98IPUUUUS-vzvmqxxJH8qivUGmMrj9de4ftHWepjKcRtQMwx6Z_63kYMvZJ3zxoaWxPEezhBUoleb3u9QhUgMc2lr-gj84w1_4ZZ9OOcT9NZ1Hfqm5L_ku7_IWR2XYxeaen3xWLny29AVEJ3vfkuqGp2A15Cw6vL6AH1DMX7u3fX9diWV4RR0Hl6pGHTJUm7CbBulDw8DZtRhXq0DlRz9XY03pnXY-1w1_3K0x_UjFku1MFEQwSL-ekFC0bqA8jjkTwqzDdseNGB_pD1lUeaiLAy9tfhEnzbHSF5p1xPeTgj-iynUbg0OMvxccaqzlMFxF0Oqp0o5LDUrRjAlVNaGHA5pzQfnXjDlyVriKhYPXhf9lhEePeh5KT3A6d2maOlRUGiiXKzUwYYE1IAbVAsD5dH9RJUeuNRoSmUQygyK3aB9VqqngI-uNu819BhjB1ieD4hx1frwv8kQcZpo_zCJ8CL_ld0q8qTALVEJ7aWGNMAeXk9tWLuK38LZnAmfGUDQMPq3U9YZofd0xCajj3WWWyifZLSsSjfmQQu3lKIPDJ_MYxPKR4Yeu3EyuW272UGxqCI616uNWkCWplotnmGjz5PaHd1-sD2G_R0huFY22fvfJS6HArojr8kY7XXKeyKwho-_46wVYXJ3d0dbGVP4RY7ty7Rysn3oM_Lm_z0LZ9y9xnB4WKPOxOysvndh_YUlMcaslRfN1IltBaI8BYxMBaKw5nfV9myNZf5xm4-N6p9QKnjlmm3_uu6iuBEd-AP1opOyRKgTx3fv-fW0s8AZrX9HOrsn4iB7ZKlisDxMF5zvijsjDwrA1MRapaW82vfStu5ANnsy8j_nxy0)

Нарушение ЦБ №2


### Указание "доверенных компонент" на архитектурной диаграмме.

![Политика архитекутры устройства детектирования](архитектура.png)


### Политики безопасности 


```python {lineNo:true}
    if  src == 'downloader' and dst == 'manager' \
        and operation == 'download_done':
        authorized = True    
    if src == 'manager' and dst == 'downloader' \
        and operation == 'download_file':
        authorized = True    
    if src == 'downloader' and dst == 'archiver' \
        and operation == 'file_archive':
        authorized = True    
    if src == 'downloader' and dst == 'verifier' \
        and operation == 'verification_requested':
        authorized = True    
    if src == 'verifier' and dst == 'updater' \
        and operation == 'handle_verification_result' \
        and details['verified'] is True:
        authorized = True    
    if src == 'updater' and dst == 'journal' \
        and operation == 'update_event':
        authorized = True      
    if src == 'verifier' and dst == 'storage' \
        and operation == 'get_blob':
        authorized = True
    if src == 'storage' and dst == 'verifier' \
        and operation == 'blob_content':
        authorized = True    
    if src == 'updater' and dst == 'storage' \
        and operation == 'get_blob':
        authorized = True
    if src == 'storage' and dst == 'updater' \
        and operation == 'blob_content':
        authorized = True
    if src == 'hendler' and dst == 'analyser' \
        and operation == 'new_input':
        authorized = True
    if src == 'analyser' and dst == 'gen_event' \
        and operation == 'event_security':
        authorized = True
    if src == 'gen_event' and dst == 'journal' \
        and operation == 'event_security':
        authorized = True
```

## Запуск приложения и тестов

### Запуск приложения

см. [инструкцию по запуску](README.md)
