## DEV

```
pnpm install
```

`.env.local`

```
VITE_APP_API_HOST="http://100.81.114.103:8765"
```

```
npx openapi-typescript http://100.81.114.103:8765/api/openapi.json -o ./src/api/openapi.d.ts
npx openapi-typescript http://192.168.218.79:7799/api/openapi.json -o ./src/api/openapi.d.ts
```
