## プロジェクトの作成

https://ja.vitejs.dev/guide/

プロジェクトの作成

```bash
yarn create vite
mv virty-dev/* ./
rmdir virty-dev
```

パッケージのインストール

```bash
yarn install
```

他ホストからの通信を許可する(vite.config.ts)

```ts
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
  },
})
```


実行

```bash
yarn run dev
```

