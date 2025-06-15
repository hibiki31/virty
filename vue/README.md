## DEV

```
pnpm install
```

`.env.local`

```
VITE_APP_API_HOST="http://100.81.114.103:8765"
```

```
npx openapi-typescript http://100.81.114.103:8765/api/openapi.json -o ./src/api.d.ts
```