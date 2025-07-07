# H64 (h64-quasar)

Frontend of h64 project. Visualization of data from my home.

## Install the dependencies
```bash
yarn
# or
npm install
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)
```bash
quasar dev
```


### Lint the files
```bash
yarn lint
# or
npm run lint
```


### Format the files
```bash
yarn format
# or
npm run format
```



### Build the app for production
```bash
quasar build
```

### Deploy

```bash
rsync -rtlPvi --delete ~/h64/frontend/h64-quasar/dist/spa/ host:h64/frontend/h64-quasar/dist/spa/
ssh host
sudo rsync -rtlPvi --delete ~/h64/frontend/h64-quasar/dist/spa/ /var/www/html/h64/
```

### Customize the configuration
See [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-vite/quasar-config-js).
