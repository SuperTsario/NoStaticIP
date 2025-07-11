# Инструкция по заполнению данных SMTP-сервера
Для использования NoStaticIP необходимо заполнить данные SMTP сервера. Большинство почтовых сервисов поддерживают использование специальных протоколов для электронной почты, включая SMTP. Если вашей почтовой программы нет в данной инструкции, пожалуйста, получите эту информацию у оператора вашего почтового сервиса.

## Требуемые данные
Для использования программы требуются следующие данные: SMTP-сервер, порт SMTP-сервера, логин и пароль. Адреса SMTP-серверов и их порты будут приведены ниже, инструкции по получению пароля будут приведены ниже. В качестве логина используется ваш адрес электронной почты.

## Сервера и порты
|    Сервис      |     SMTP-сервер     |       Порт       |
|----------------|---------------------|------------------|
|Почта Gmail     |smtp.gmail.com       |587               |
|Яндекс Почта    |smtp.yandex.ru       |465               |
|Почта Mail.ru   |smtp.mail.ru         |465               |
|Почта VK        |smtp.vk.com          |465               |
|Почта Rambler   |smtp.rambler.ru      |25<br/>465<br/>587|
|Почта Yahoo     |smtp.mail.yahoo.com  |465<br/>587       |
|Почта Outlook   |smtp-mail.outlook.com|587               |

## Получения пароля от SMTP сервера
В зависимости от вашего почтового сервиса пароль от SMTP сервера может быть паролем от вашего аккаунта или может создаваться отдельно. Ниже приведены инструкции для самых популярных почтовых сервисов.

### Почта Gmail
Для получения пароля приложения войдите в свой аккаунт Google и пройдите по ссылке [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) или же вы можете воспользоваться следующими шагами:
1. Войдите в свой аккаунт Google.
2. Перейдите на вкладку **«безопасность»**.
3. Пролистайте до **«Вход в Google»** и нажмите на **«Двухэтапная аунтефикация»**.
4. Нажмите на пункт **«Создать пароль приложения»**.

### Яндекс Почта
1. Войдите в свой аккаунт Яндекс и перейдите на страницу управления аккаунтом [(id.yandex.ru)](id.yandex.ru).
2. Нажмите на кнопку **«Еще»** (слева на странице).
3. Найдите пункт **«Пароли приложений»** во вкладке **«Безопасность»** и нажмите на него.
4. Нажмите на **«Почта»** во владке **«Создать пароль приложения»**.
5. Введите название пароля.
6. Зайдите в настройки почты (шестеренка в правом верхнем углу) → **«Все настройки»** → **«Почтовые программы»**.
7. Включите пункт **«С сервера imap.yandex.ru по протоколу IMAP»** (в Яндекс Почте включение этого пункта делает возможным использование SMTP-сервера).

###  Почта Outlook
  Используйте пароль от вашего Microsoft-аккаунта. Если вы используете аккаунт без пароля, вам придется отключить эту функцию и использовать пароль. Для поддержания уровня безопасности используйте двухфакторную аунтефикацию и сложный пароль.

### Почта Mail.ru
[Официальная инструкция от Mail.ru](https://help.mail.ru/mail/mailer/password/)
1. Перейдите в «Настройки» почты (шестерёнка в левом нижнем углу) → **«Все настройки»** → **«Безопасность»** → **«Пароли для внешних приложений»**.
2. Нажмите **«Создать»**.
3. Введите название пароля.
4. Нажмите **«Продолжить»**.
5. Выберите тип протокола SMTP.
6. Нажмите **«Продолжить»**.

### Почта VK
1. Перейдите в настройки аккаунта, далее **«Безопасность»** → **«Пароли для внешних приложений»**.
2. Нажмите **«Добавить»**.
3. Ввести название приложения.
4. Нажать **«Продолжить»**.

### Почта Rambler
1. Зайдите в свой аккаунт Rambler.
2. Откройте настройки почты.
3. Перейдите в раздел **«Программы**" и включите функцию **«Доступ к почтовому ящику с помощью почтовых клиентов»**.
4. Вернитесь в раздел **«Мой профиль»**, нажмите на имя учётной записи и выберете **«Мой профиль»**.
5. В разделе **«Адреса электронной почты»** перейдите по ссылке **«Я использую почтовый клиент»**.
6. В открывшемся окне введите пароль от учётной записи Rambler и код из приложения для двухфакторной аутентификации, после нажмите **«Создать пароль»**.

### Почта Yahoo
1. Войдите в свой аккаунт Yahoo.
2. Нажмите **«Generate app password»** или **«Generate and manage app passwords»**.
3. Нажмите **«Get Started»**.
4. Введите название пароля и нажмите **«Generate password»**.

