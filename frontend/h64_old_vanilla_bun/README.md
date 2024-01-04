# Deploy

```
rsync -aPvi --delete dist/ guavapi:var_www_html_h64/ && ssh guavapi sudo rsync -aPvi --delete var_www_html_h64/ /var/www/html/h64/
```