# Nginx PHP Scan Blocking

## 목표

PHP/WordPress/phpinfo 탐색 요청을 Django, gunicorn, Sentry까지 보내지 않고 nginx에서 1차로 종료한다.

## 차단 대상

Sentry breadcrumbs와 요청 URL 기준으로 다음 패턴은 현재 서비스와 무관하다.

- `*.php`
- `/wp.php`
- `/wp-admin/...`
- `/wp-content/...`
- `/wp-includes/...`
- `/bbs/board.php`
- `/public_html/phpinfo.php`
- `/site/phpinfo.php`
- `/includes/phpinfo.php`
- 기타 `phpinfo.php`, `xmlrpc.php`, `wp-login.php`

## 권장 nginx 설정

운영 `server` 블록 안에 다음 location을 Django proxy location보다 앞에 둔다.

```nginx
# PHP, WordPress, phpinfo scanners. This service does not run PHP.
location ~* (^|/)(wp-admin|wp-content|wp-includes)(/|$) {
    access_log off;
    log_not_found off;
    return 444;
}

location ~* (^|/)(phpinfo|xmlrpc|wp-login|wp-config|wp-cron|wp-load|wp-mail|wp-settings|wp-signup|wp-trackback|wp)\.php$ {
    access_log off;
    log_not_found off;
    return 444;
}

location ~* \.php(?:/|$) {
    access_log off;
    log_not_found off;
    return 444;
}
```

`444`는 nginx 전용 비표준 상태로, 응답 본문 없이 연결을 닫는다. 운영 표준이나 로드밸런서 정책상 `444`를 쓰기 어렵다면 `return 404;` 또는 `return 403;`으로 바꾼다.

## Host 헤더 차단

알 수 없는 도메인 또는 IP 직결 요청도 default server에서 버린다.

```nginx
server {
    listen 80 default_server;
    listen 443 ssl default_server;
    server_name _;

    access_log off;
    log_not_found off;
    return 444;
}

server {
    listen 80;
    listen 443 ssl;
    server_name devspoon.com www.devspoon.com;

    # normal Django proxy settings here
}
```

TLS 인증서 설정 구조상 `default_server`에 인증서가 필요할 수 있다. 기존 운영 nginx 구성을 확인한 뒤 적용한다.

## reverse proxy 사용 시 확인 사항

- 로드밸런서 또는 CDN이 앞단에 있으면 실제 nginx까지 Host 헤더가 어떻게 전달되는지 확인한다.
- Cloudflare, ALB, NCP, AWS ELB 등 앞단이 있다면 해당 계층에서도 WAF/rule로 `.php` 차단을 추가하는 것이 좋다.
- proxy upstream으로 넘기기 전에 차단 location이 매칭되는지 `nginx -T`로 최종 설정을 확인한다.

## 배포 절차

1. 운영 nginx 설정 파일에 차단 location을 추가한다.
2. `nginx -t`로 문법 검증을 한다.
3. `nginx -s reload` 또는 systemd reload를 수행한다.
4. 다음 요청으로 확인한다.

```bash
curl -I http://devspoon.com/wp.php
curl -I http://devspoon.com/site/phpinfo.php
curl -I http://devspoon.com/bbs/board.php
```

`444`는 curl에서 `Empty reply from server`로 보일 수 있다. `404`/`403` 정책을 택한 경우 해당 status를 확인한다.

## 관측 포인트

- gunicorn access log에 `.php` 요청이 더 이상 남지 않아야 한다.
- Sentry의 `/wp.php`, `/bbs/board.php`, `/phpinfo.php` 관련 이벤트가 감소해야 한다.
- 정상 URL `/`, `/portfolio/`, `/blog/`는 영향을 받지 않아야 한다.
