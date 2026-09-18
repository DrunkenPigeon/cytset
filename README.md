# 🛡️ CYTSET & CYBERSEC ACADEMY

> **Комплексная образовательная платформа и мобильное/десктопное приложение по информационной безопасности в стиле Duolingo (микро-обучение по 15 минут в день).**  
> Разработано для системной подготовки к работе в Enterprise SOC / AppSec и обучения на профильных кафедрах ИБ в университете.

---

## 📦 Готовые к запуску сборки (Releases)

В репозитории уже собраны готовые автономные релизы:

* 📱 **[cytset.apk](cytset.apk)** *(~287 КБ)* — нативное Android-приложение (Android 7.0+, API 24–36). Подписано, оптимизировано через `zipalign`, полностью автономно (`offline-first`).
* 💻 **[cytset.exe](cytset.exe)** *(~13.7 МБ)* — десктопное приложение для Windows 10/11 (WebView2 / аппаратное ускорение, встроенная база уроков и звуковой синтезатор).
* 🌐 **[infosec-course/](infosec-course/)** — веб-портал курса с интерактивным WAF-инспектором, фильтрами ролей и изолированным Docker-стендом.

---

## 🦉 Ключевые возможности приложения «CYTSET»

1. **Геймификация в стиле Duolingo:**
   * 🔥 **Серия дней (Streak):** мотивация ежедневных занятий.
   * ❤️ **Жизни (Hearts):** 5 жизней с восстановлением.
   * ⚡ **Опыт (XP):** начисление очков за правильные ответы и завершение дней.
   * 🎵 **Синтезатор звуков (Web Audio API):** победные мажорные аккорды, зуммер ошибки и фанфары при завершении дня.
   * ❌ **Интерактивное управление:** закрытие урока с подтверждением и защитой от случайной потери прогресса.

2. **4-секторная глубина каждого урока (увеличение теории в 3 раза):**
   * ⚙️ **Внутренняя механика:** стандарты RFC (793, 826, 1035, 3227, 4120), структуры ядра Linux (`struct cred`, `task_struct`), деревья AST, протокол Kerberos и криптография.
   * 🔴 **Реализация атак (Offensive PoC):** боевые команды и утилиты (`sqlmap`, `nmap`, `arpspoof`, `bettercap`, `p0f`, `impacket`, `hashcat`, `responder`, `mimikatz`, `certipy`, `volatility`).
   * 🔵 **Архитектурная защита (Blue Team):** параметризованные запросы (`COM_STMT_PREPARE`), транзакционные блокировки `SELECT FOR UPDATE`, Dynamic ARP Inspection (DAI), DHCP Snooping, SMB Signing, `PR_SET_NO_NEW_PRIVS`.
   * 🟣 **Детектирование (SOC & SIEM):** привязка к точным Windows Sysmon Event ID (1, 3, 7, 8, 10, 11, 13), правила Sigma (YAML), сигнатуры Suricata/Snort, параметры `auditd`.

3. **270 проверочных задач (по 9 задач в день):**
   * Вместо базовых вопросов — глубокие технические задачи на анализ дампов, флагов утилит, поведения сетевого стека и защитных правил.

4. **Интервальное повторение (Spaced Repetition):**
   * В ежедневный пул заданий динамически подмешиваются **2–3 случайные задачи из ранее завершенных дней** с бейджем `🔄 ПОВТОРЕНИЕ`.

5. **Система «Работа над ошибками» (Mistake Tracking Engine):**
   * Ошибочные вопросы автоматически фиксируются в реестре приложения (`⚠️ N` в шапке).
   * На следующий день неисправленные ошибки **гарантированно выставляются первыми** в очередь заданий с бейджем `⚠️ РАБОТА НАД ОШИБКАМИ`.
   * За успешное закрытие ошибки начисляется повышенный бонус **+25 XP**.

---

## 📅 Программа 30-дневного интенсива

### 🌐 Неделя 1: Веб-безопасность & API (Web AppSec)
* **День 1:** SQLi AST & Lexer (`sqlmap`, Prepared Statements, `information_schema`).
* **День 2:** Union-Based SQLi (выравнивание колонок `ORDER BY`, `CONCAT_WS`, Suricata SID).
* **День 3:** Error-Based & Blind SQLi (`EXTRACTVALUE`, `pg_sleep`, бинарный поиск, WAF).
* **День 4:** Prepared Statements & WAF Bypassing (`COM_STMT_PREPARE`, HPP, ModSecurity).
* **День 5:** SSRF & Cloud Metadata (обход IP, `0x7f.1`, `http://169.254.169.254/latest/meta-data/`).
* **День 6:** SSRF Hardening & DNS Rebinding (IMDSv2 `X-aws-ec2-metadata-token`, TTL=0, `127.0.0.1`).
* **День 7:** Race Conditions & HTTP/2 (Single-Packet Attack, `SELECT FOR UPDATE`, TOCTOU).

### 📡 Неделя 2: Сетевые протоколы и безопасность (L2–L7)
* **День 8:** L2 Ethernet & CAM Table Flooding (`macof`, Port Security, 802.1Q).
* **День 9:** ARP Cache Poisoning (RFC 826, `arpspoof`, `bettercap`, MITM).
* **День 10:** L2 Hardening (Dynamic ARP Inspection, DHCP Snooping Trust ports).
* **День 11:** TCP FSM & Сканирование (RFC 793, SYN Half-Open, FIN, NULL, Xmas, `nftables`).
* **День 12:** Пассивный OS Fingerprinting (TCP Window Size, SYN Options, `p0f`).
* **День 13:** DNS Kaminsky Attack & Cache Poisoning (RFC 1035, Bailiwick rule, 16-bit TXID, 0x20 bit encoding).
* **День 14:** DNS Tunneling & Shannon Entropy (`dnscat2`, `iodine`, вычисление $H(X) > 4.5$, Zeek).

### 🐧 Неделя 3: Безопасность Linux & Контейнеров
* **День 15:** Linux DAC & `struct cred` (UID/GID, fsuid, `task_struct`, Capabilities).
* **День 16:** Опасные Linux Capabilities (`CAP_DAC_READ_SEARCH`, `CAP_SYS_ADMIN`, `capsh`).
* **День 17:** Capabilities Hardening (`PR_SET_NO_NEW_PRIVS`, `drop-capabilities`, Seccomp).
* **День 18:** Docker Namespaces & Cgroups (`CLONE_NEWPID`, `cgroupfs`, Rootless Docker).
* **День 19:** Побег через `docker.sock` (монтирование хостового корня `/host`, chroot).
* **День 20:** Побег из `--privileged` контейнера (манипуляция `release_agent` в cgroup v1).
* **День 21:** SUID Binaries & `glibc AT_SECURE` (PATH Hijacking, фильтрация `LD_PRELOAD`).

### 🏢 Неделя 4: Active Directory & Корпоративная инфраструктура
* **День 22:** Протокол Kerberos V5 (RFC 4120, триада AS/TGS/AP, структура билета PAC).
* **День 23:** Kerberoasting (`GetUserSPNs.py`, SPN, TGS-REP RC4 ticket, Hashcat `-m 13100`, gMSA).
* **День 24:** AS-REP Roasting (`GetNPUsers.py`, `DONT_REQ_PREAUTH`, Hashcat `-m 18200`, Kerberos Pre-Auth).
* **День 25:** NTLM Pass-the-Hash (`impacket-psexec`, SAML/LSASS, Restricted Admin mode).
* **День 26:** NTLM Relay & LLMNR/NBT-NS (`Responder`, `ntlmrelayx`, SMB Signing, LDAP Channel Binding).
* **День 27:** Active Directory Certificate Services (AD CS ESC1, `certipy find`, SAN `ENROLLEE_SUPPLIES_SUBJECT`).
* **День 28:** AD Hardening & Tier Model (Tier 0/1/2, LAPS, Protected Users Security Group).

### 🕵️ Финал: SOC, DFIR & Комплексный экзамен
* **День 29:** Detection Engineering (Sigma правила YAML, Sysmon Event ID 1/3/7/8/10/11/13, Pyramid of Pain).
* **День 30:** DFIR RAM Forensics & Итоговый экзамен (RFC 3227 Order of Volatility, LiME, Volatility 3 `windows.malfind`, `windows.pslist`, экзаменационные кейсы).

---

## 🚀 Инструкция по сборке и запуску

### 1. Запуск Android приложения (`cytset.apk`)
* Скопируйте файл `cytset.apk` на Android-устройство и запустите установку, либо через ADB:
  ```bash
  adb install cytset.apk
  ```

### 2. Запуск Windows Desktop приложения (`cytset.exe`)
* Просто запустите файл `cytset.exe` двойным кликом. Не требует установки Python или сторонних зависимостей.

### 3. Запуск веб-платформы и лабораторного стенда (Docker)
1. Перейдите в папку стенда:
   ```bash
   cd infosec-course/lab
   docker compose up -d
   ```
2. Откройте в браузере:
   * **Веб-портал курса:** откройте `infosec-course/index.html` (или запустите `python -m http.server 8080` в `infosec-course/`).
   * **Уязвимый полигон (Flask API):** `http://localhost:5000`
   * **WAF Прокси (ModSecurity):** `http://localhost:8080`
   * **OWASP Juice Shop:** `http://localhost:3000`
   * **Изолированный Cloud Vault (IMDS):** `http://172.28.2.50:8080` (внутренняя сеть).

---

## 🛠️ Сборка из исходников

### Пересборка APK:
```bash
python cytset-android/build_apk.py
```

### Пересборка EXE:
```bash
pip install pyinstaller pywebview
pyinstaller --noconsole --onefile --name cytset --icon cytset-desktop/app.ico --add-data "cytset-android/assets;assets" cytset-desktop/main.py
```

---

## 📄 Лицензия
Разработано в учебных и исследовательских целях (Educational & Security Research).